# Cisco IOS / IOS XE - LibreNMS SNMPv3

This project recommends **SNMPv3 authPriv** for Cisco switches.

## Objectives

LibreNMS should be able to read:

- device identity and uptime
- interfaces and counters
- VLAN information
- bridge/FDB MAC tables
- ARP information where available
- LLDP/CDP neighbors
- hardware/environmental sensors supported by the platform

## Example configuration

Replace the placeholders before applying:

```cisco
conf t

ip access-list standard ACL-LIBRENMS-SNMP
 permit host <LIBRENMS_IP>
 deny any log
exit

snmp-server view LIBRENMS-VIEW iso included
snmp-server group LIBRENMS-GROUP v3 priv read LIBRENMS-VIEW access ACL-LIBRENMS-SNMP
snmp-server user librenms LIBRENMS-GROUP v3 auth sha <AUTH_PASSWORD> priv aes 128 <PRIV_PASSWORD>

snmp-server contact <CONTACT>
snmp-server location <LOCATION>

lldp run
cdp run

end
write memory
```

Use different authentication and privacy passwords. Keep them out of Git.

## Important IOS/IOS XE note

On platforms where an SNMP engine ID is manually configured, configure it **before** creating SNMPv3 users because the user credentials are tied to the engine ID. Do not change the engine ID casually after SNMPv3 users are configured.

## Test from LibreNMS host

Install Net-SNMP tools if needed:

```bash
sudo apt install -y snmp
```

Test:

```bash
snmpwalk -v3 \
  -l authPriv \
  -u librenms \
  -a SHA \
  -A '<AUTH_PASSWORD>' \
  -x AES \
  -X '<PRIV_PASSWORD>' \
  <SWITCH_IP> \
  1.3.6.1.2.1.1
```

Expected result: system OIDs such as `sysDescr`, `sysObjectID`, `sysUpTime`, `sysName`, `sysLocation`.

## Add device to LibreNMS

In LibreNMS:

```text
Devices -> Add Device
```

Use:

```text
SNMP version: v3
Security level: authPriv
Username: librenms
Auth algorithm: SHA
Privacy algorithm: AES
```

## Validate discovery

After discovery/polling confirm:

- Ports are present with correct names.
- VLANs are present.
- FDB/MAC information is populated.
- LLDP/CDP neighbors are visible.
- Uplink ports are distinguished from edge/access ports.

For endpoint localization, use MAC/FDB data primarily on the access switch. A MAC learned on an uplink identifies the downstream path, not necessarily the physical endpoint port.

## Optional SNMP traps

Traps are not required for normal polling. Add them later only after the LibreNMS snmptrapd sidecar and firewall rules are intentionally enabled.
