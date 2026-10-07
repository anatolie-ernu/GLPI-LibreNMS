# GLPI <-> LibreNMS Integration API

## Purpose

This service is the correlation layer between GLPI Service Desk / CMDB and LibreNMS network monitoring.

It must not replace either product's responsibilities.

```text
GLPI                        LibreNMS
Assets / Tickets            Network state / Alerts
      \                        /
       \                      /
        +-- Integration API --+
```

## Initial responsibilities

1. Resolve endpoint network location by MAC or IP.
2. Enrich a GLPI ticket/asset with current LibreNMS evidence.
3. Receive LibreNMS alert webhooks/API transports.
4. Create or update a GLPI incident.
5. Deduplicate repeated alerts.
6. Correlate alert recovery with the original ticket.
7. Record audit information for every automated action.

## Non-responsibilities

The first implementation must not:

- modify Cisco/MikroTik configuration;
- perform SNMP writes;
- shut/no-shut switch ports;
- automatically remediate incidents;
- expose GLPI or LibreNMS credentials to clients;
- directly access GLPI/LibreNMS databases.

Use supported HTTP APIs only.

## Proposed stack

Recommended implementation:

```text
Python 3.12+
FastAPI
httpx
pydantic
Redis (optional for locks/cache)
PostgreSQL or SQLite only if durable correlation state is required
```

For the first prototype, durable alert-to-ticket correlation can be implemented with a small dedicated database. Do not store this state in application container files if production resilience is required.

## Authentication

### Incoming calls

Use one of:

- reverse-proxy authentication;
- dedicated webhook secret/header;
- mTLS for higher-assurance internal deployments.

### Upstream APIs

- LibreNMS: API token in `X-Auth-Token`.
- GLPI: dedicated integration credentials/tokens according to the deployed GLPI API configuration.

All secrets are environment variables or external secrets. Never commit them.

## Environment contract

Example names only:

```env
INTEGRATION_BIND=0.0.0.0
INTEGRATION_PORT=8088

LIBRENMS_BASE_URL=https://librenms.example.internal
LIBRENMS_API_TOKEN=SECRET

GLPI_BASE_URL=https://glpi.example.internal
GLPI_APP_TOKEN=SECRET
GLPI_USER_TOKEN=SECRET

WEBHOOK_SECRET=SECRET
LOG_LEVEL=INFO
```

These values must not be added to the repository in a real `.env` file.

## Endpoint design

See `openapi.yaml` for the baseline contract.

Primary endpoints:

```text
GET  /health
GET  /v1/endpoints/by-ip/{ip}
GET  /v1/endpoints/by-mac/{mac}
GET  /v1/assets/{asset_id}/network
POST /v1/events/librenms
GET  /v1/correlations/{key}
```

## Endpoint resolution algorithm

### By MAC

1. Normalize the MAC address.
2. Query LibreNMS switching/FDB data.
3. Identify all matching FDB entries.
4. Exclude obvious upstream/uplink paths when topology evidence allows it.
5. Select or rank the likely edge/access port.
6. Resolve device, interface, VLAN and timestamps.
7. Return evidence and confidence, not only a final string.

Example:

```json
{
  "mac": "00:25:90:AB:CD:EF",
  "device": {
    "id": 42,
    "hostname": "HQ-ACCESS-SW-04"
  },
  "port": {
    "id": 1002,
    "ifName": "Gi1/0/31",
    "status": "up"
  },
  "vlan": 129,
  "confidence": "high",
  "last_seen": "2026-09-14T15:42:00+03:00"
}
```

### By IP

1. Normalize and validate the IP.
2. Resolve IP -> MAC using available LibreNMS ARP/NAC data or GLPI asset metadata.
3. Run the MAC workflow.
4. Return the source used for every correlation step.

## Alert -> ticket algorithm

Input from LibreNMS:

```text
alert_id
rule_id
device_id
hostname
severity
state
timestamp
fault information
```

Correlation key:

```text
librenms:<device_id>:<rule_id>:<fault_object>
```

Processing:

```text
Receive alert
  |
  +-- authenticate webhook
  +-- validate payload
  +-- calculate correlation key
  +-- lookup existing open correlation
          |
          +-- exists -> update existing GLPI ticket
          |
          +-- absent -> create new GLPI ticket
                         store ticket ID
```

On recovery:

```text
Recovery event
  -> locate correlation
  -> add GLPI follow-up
  -> mark correlation recovered
  -> optional policy-controlled ticket resolution
```

## Deduplication requirements

- repeated poll notifications must not create repeated tickets;
- concurrent identical webhook deliveries must be safe;
- correlation operations should be transactional or protected by a lock;
- ticket creation failure must not leave a false successful correlation record;
- retries must be bounded and observable.

## Logging

Log structured operational events without secrets:

```text
request_id
correlation_key
librenms_alert_id
glpi_ticket_id
action
result
latency
```

Never log API tokens, passwords, session tokens or full authorization headers.

## Health/readiness

`GET /health` should report only non-sensitive state.

Example:

```json
{
  "status": "ok",
  "librenms": "reachable",
  "glpi": "reachable"
}
```

A future `/ready` endpoint can fail when required upstream APIs are unavailable.

## Testing strategy

### Unit tests

- MAC normalization;
- correlation key construction;
- severity mapping;
- deduplication logic;
- recovery state transitions.

### Contract tests

Mock GLPI and LibreNMS APIs.

### Integration tests

Against staging instances:

- known MAC -> expected Cisco port;
- known MAC -> expected MikroTik bridge port;
- alert -> one ticket;
- duplicate alert -> same ticket;
- recovery -> same ticket follow-up;
- upstream timeout -> controlled retry/failure.

## Security requirements

- TLS in production.
- Least-privilege API tokens.
- IP allowlist at reverse proxy/firewall.
- Webhook authentication.
- Dependency scanning.
- Container runs as non-root where practical.
- Read-only filesystem where practical.
- No Docker socket mount.
- Rate limiting for webhook endpoints.
- Request size limits.
- Audit log for automatic ITSM actions.
