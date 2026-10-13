# GLPI <-> LibreNMS Integration API

## Status

**Executable implementation available — pilot validation required.**

This service is the internal correlation layer between GLPI Service Desk / CMDB and LibreNMS.

```text
GLPI Assets / Tickets
        |
        +------ Integration API ------ LibreNMS
                 |
                 +-- IP/MAC -> switch/port/VLAN
                 +-- alert -> GLPI incident
                 +-- duplicate suppression
                 +-- recovery -> GLPI follow-up
```

## Implemented endpoints

```text
GET  /health
GET  /ready
GET  /v1/endpoints/by-ip/{ip}
GET  /v1/endpoints/by-mac/{mac}
GET  /v1/assets/{asset_id}/network
POST /v1/events/librenms
GET  /v1/correlations/{key}
```

Read/correlation endpoints require:

```text
X-API-Key: <INTEGRATION_API_KEY>
```

LibreNMS webhook ingestion requires:

```text
X-Webhook-Secret: <WEBHOOK_SECRET>
```

## Current API choices

### LibreNMS

The implementation uses the stable documented LibreNMS API v0 with:

```http
Authorization: Bearer <token>
```

Used routes include:

```text
/api/v0
/api/v0/resources/ip/arp/{query}
/api/v0/resources/fdb/{mac}
/api/v0/ports/{port_id}?with=device,vlans
/api/v0/devices/{device_id}
```

### GLPI

The first executable implementation uses GLPI's legacy REST API v1 for ITSM write operations:

```text
/apirest.php/initSession/
/apirest.php/Ticket/
/apirest.php/ITILFollowup/
```

This is deliberate for the pilot because the legacy API has the established generic item write contract. GLPI 11's high-level API v2 uses OAuth2 and will be evaluated against the deployed pilot before migration.

## Environment

The root `.env` contains the integration settings.

Minimum:

```env
INTEGRATION_ENABLED=true
INTEGRATION_API_KEY=<generated/private>
WEBHOOK_SECRET=<generated/private>

LIBRENMS_BASE_URL=http://librenms:8000
LIBRENMS_API_TOKEN=<LibreNMS API token>
LIBRENMS_VERIFY_TLS=false

GLPI_BASE_URL=http://glpi
GLPI_API_MODE=legacy_v1
GLPI_APP_TOKEN=<GLPI API client app token>
GLPI_USER_TOKEN=<dedicated GLPI integration user token>
GLPI_VERIFY_TLS=false
GLPI_ASSET_ITEMTYPE=Computer
GLPI_DEFAULT_GROUP_ID=
```

`scripts/init-env.sh` generates the internal API key and webhook secret. The LibreNMS/GLPI tokens must be created in the applications and inserted only into the private `.env`.

Deploy:

```bash
bash scripts/validate.sh
bash scripts/deploy.sh
```

The service runs as Compose profile `integration` and is not host-published. LibreNMS reaches it on the Docker network at:

```text
http://integration-api:8088
```

## LibreNMS API transport

LibreNMS supports an API alert transport with custom headers/body.

Suggested transport:

```text
Method: POST
URL:
http://integration-api:8088/v1/events/librenms

Header:
X-Webhook-Secret: <WEBHOOK_SECRET>
Content-Type: application/json
```

Example body using LibreNMS transport/template variables:

```json
{
  "alert_id": "{{ $id }}",
  "rule_id": 0,
  "device_id": "{{ $device_id }}",
  "hostname": "{{ $hostname }}",
  "severity": "{{ $severity }}",
  "state": "{{ $state }}",
  "timestamp": "{{ $timestamp }}",
  "fault_object": "{{ $name }}",
  "message": "{{ $msg }}"
}
```

For installations where the API transport expects variables without the `$alert->` prefix, use the variables exactly as offered by the LibreNMS transport UI. Validate the rendered JSON with one pilot alert and one recovery event.

## Correlation and deduplication

Correlation key:

```text
librenms:<device_id>:<rule_id>:<fault_object>
```

If the transport does not provide a numeric rule ID, `rule_id=0` is accepted and the rule name can be placed in `fault_object`.

Behavior:

```text
new problem
  -> create one GLPI Ticket
  -> store alert/ticket correlation

same problem again
  -> ignored (no duplicate ticket)

recovery
  -> add ITILFollowup to original ticket
  -> mark correlation recovered

same recovery again
  -> ignored
```

Automatic ticket closure is intentionally not implemented in the first version.

## Persistence

Correlation state is stored in SQLite:

```text
/data/correlations.db
```

and persisted in the Compose volume `integration_data`.

The first version is intentionally one Uvicorn worker. For HA/multi-replica operation, move correlation state/locking to PostgreSQL or another shared transactional store.

## IP/MAC resolution

IP lookup:

```text
IP -> LibreNMS ARP -> MAC -> FDB -> port/device
```

MAC lookup:

```text
MAC -> LibreNMS FDB -> candidate ports -> port/device details
```

If multiple FDB candidates exist, the service returns a conservative confidence value rather than claiming certainty.

## Asset enrichment

For:

```text
GET /v1/assets/{asset_id}/network
```

the first implementation treats the GLPI asset as `Computer` unless `GLPI_ASSET_ITEMTYPE` is changed. It reads associated `NetworkPort` records and resolves the first MAC with usable LibreNMS evidence.

## Tests

```bash
cd integration-api
python3 -m pip install -r requirements-dev.txt
pytest -q
```

CI also builds the integration container.

## Security

- no direct DB access to GLPI or LibreNMS;
- no SNMP write;
- no switch configuration actions;
- API/webhook secrets required;
- tokens only in private environment/secrets;
- no host port published for the integration API;
- non-root container;
- no Docker socket;
- outbound access only to GLPI/LibreNMS APIs;
- logs must not include tokens.

## Pilot acceptance

- [ ] `/ready` reports both upstream systems reachable.
- [ ] known IP resolves to expected switch/port.
- [ ] known MAC resolves to expected switch/port.
- [ ] GLPI asset MAC resolves to network evidence.
- [ ] one LibreNMS alert creates exactly one GLPI ticket.
- [ ] duplicate alert creates no second ticket.
- [ ] recovery adds follow-up to the original ticket.
- [ ] repeated recovery is ignored.
- [ ] correlation survives container restart.
- [ ] backup includes correlation state.
- [ ] GLPI/LibreNMS tokens are least privilege.
