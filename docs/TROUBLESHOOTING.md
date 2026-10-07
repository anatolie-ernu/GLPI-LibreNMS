# Troubleshooting

## Stack status

```bash
docker compose ps
bash scripts/status.sh
```

## Logs

```bash
docker compose logs --tail=200 glpi
docker compose logs --tail=200 glpi-db
docker compose logs --tail=200 librenms
docker compose logs --tail=200 librenms-dispatcher
docker compose logs --tail=200 librenms-db
```

## Validate LibreNMS

```bash
docker compose exec librenms lnms validate
```

## SNMP connectivity

### Cisco / MikroTik SNMPv3 test

```bash
snmpwalk -v3 \
  -l authPriv \
  -u librenms \
  -a SHA \
  -A '<AUTH_PASSWORD>' \
  -x AES \
  -X '<PRIV_PASSWORD>' \
  <DEVICE_IP> \
  1.3.6.1.2.1.1
```

If it fails, check:

- route from Docker host to the management IP
- UDP/161 firewall/ACL
- SNMPv3 username
- security level `authPriv`
- authentication password/algorithm
- privacy password/algorithm
- SNMP source ACL `/32`
- device clock and general management-plane health

## Cisco checks

```text
show snmp user
show snmp group
show access-lists ACL-LIBRENMS-SNMP
show lldp neighbors detail
show cdp neighbors detail
show mac address-table
```

If system OIDs work but FDB/VLAN discovery does not, verify platform/MIB support and allow a complete LibreNMS discovery cycle.

## MikroTik checks

```routeros
/snmp print detail
/snmp community print detail
/interface bridge host print
/ip neighbor print detail
```

If SNMP works but VLAN detail is incomplete, remember that LibreNMS enhanced RouterOS VLAN discovery can require its helper script and SNMP write access. Do not enable that feature until its security implications have been reviewed.

## A MAC appears on an uplink

This is normal in switched networks. A switch can learn endpoint MAC addresses on an uplink toward another access switch. Follow LLDP/CDP topology and FDB entries downstream until the final access/edge port is found.

## Duplicate GLPI computers

Check:

- agent identity and serial number quality
- cloned Windows images
- manually created GLPI records
- duplicate network adapters
- agent reinstall/re-enrollment history

Do not delete duplicates blindly; determine which record contains authoritative lifecycle/history data first.

## Container restart loop

Inspect:

```bash
docker compose ps
docker inspect <container>
docker compose logs --tail=300 <service>
```

For database failures, verify volume space and permissions before recreating containers.

## Disk usage

```bash
df -h
docker system df
docker volume ls
```

LibreNMS RRD/history data can grow over time. Monitor the host filesystem and alert before capacity becomes critical.
