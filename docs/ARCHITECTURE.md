# Architecture

## Goal

Build a self-hosted inventory and network-discovery platform that answers two different questions reliably:

1. **What is this asset?** -> GLPI
2. **Where is this asset connected right now?** -> LibreNMS

## Logical model

```text
                         +----------------------+
                         |        GLPI          |
                         | Asset / CMDB / Agent |
                         +----------+-----------+
                                    |
                     Hostname / IP / MAC / User
                                    |
                                    v
+-------------+      SNMPv3     +----------------------+      LLDP/CDP/FDB
| Cisco       | <-------------- |      LibreNMS        | <--------------+
| switches    |                 | Network Discovery    |                |
+-------------+                 +----------------------+                |
         ^                              ^                               |
         |                              |                               |
         |                              | SNMPv3                        |
         |                       +------+-------+                       |
         +-----------------------| MikroTik     |-----------------------+
                                 | switches     |
                                 +--------------+
```

## Data ownership

### GLPI is authoritative for

- computers and servers
- serial numbers
- CPU/RAM/storage
- operating systems
- installed software
- assigned user/department
- lifecycle and asset metadata
- endpoint IP/MAC reported by GLPI Agent

### LibreNMS is authoritative for

- current network-device state
- switch interfaces and counters
- VLAN information
- FDB/MAC learning
- ARP/NDP where available
- LLDP/CDP neighbors
- port errors and utilization
- device availability and sensors

## Correlation workflow

Example:

```text
GLPI
HQ-PC-043
IP 10.129.21.43
MAC 00:25:90:AB:CD:EF
        |
        v
LibreNMS FDB search
MAC 00:25:90:AB:CD:EF
        |
        v
HQ-ACCESS-SW-04 / Gi1/0/31 / VLAN 129
```

## Important interpretation rule

A learned MAC on a trunk/uplink does not prove that the endpoint is physically connected to that port. The correct endpoint port is normally the last access/edge port in the topology path. LLDP/CDP plus FDB data should therefore be used together.

## Docker isolation

The base compose uses separate networks:

- `glpi-net`
- `librenms-net`

GLPI and LibreNMS do not require direct container-to-container communication in Stage 1. Future API correlation can be added through a deliberately scoped integration service.

## Stage roadmap

### Stage 1 - Baseline

- GLPI Docker deployment
- LibreNMS Docker deployment
- Cisco SNMPv3 onboarding
- MikroTik SNMPv3 onboarding
- basic backup

### Stage 2 - Endpoint inventory

- GLPI Agent
- Windows GPO deployment
- Active Directory integration
- inventory validation

### Stage 3 - Network correlation

- automated IP/MAC lookup
- FDB traversal
- switch/port identification
- VLAN correlation
- reporting/dashboard

### Stage 4 - Production hardening

- reverse proxy + HTTPS
- SSO/LDAP where applicable
- backup retention and restore tests
- monitoring/alerts
- optional syslog and SNMP traps
- vulnerability scanning and CI validation
