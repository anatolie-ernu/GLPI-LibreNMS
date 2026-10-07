# MikroTik RouterOS - LibreNMS SNMPv3

For production, use **SNMPv3/authPriv** and restrict SNMP queries to the LibreNMS server address.

## Base read-only configuration

Replace placeholders before applying:

```routeros
/snmp community
set [find default=yes] read-access=no write-access=no
add name="librenms" \
    addresses=<LIBRENMS_IP>/32 \
    security=private \
    authentication-protocol=SHA1 \
    authentication-password="<AUTH_PASSWORD>" \
    encryption-protocol=AES \
    encryption-password="<PRIV_PASSWORD>" \
    read-access=yes \
    write-access=no

/snmp
set enabled=yes contact="<CONTACT>" location="<LOCATION>"
```

Use passwords of at least 8 characters and keep them out of Git.

Depending on RouterOS version and device capabilities, displayed protocol names can vary. Verify accepted values with:

```routeros
/snmp community print detail
```

## Optional source address

If the MikroTik device has multiple routing tables/interfaces and SNMP replies use an unexpected source address, set an explicit source address:

```routeros
/snmp set src-address=<MANAGEMENT_IP>
```

## Test from LibreNMS host

```bash
sudo apt install -y snmp

snmpwalk -v3 \
  -l authPriv \
  -u librenms \
  -a SHA \
  -A '<AUTH_PASSWORD>' \
  -x AES \
  -X '<PRIV_PASSWORD>' \
  <MIKROTIK_IP> \
  1.3.6.1.2.1.1
```

## Add to LibreNMS

Use:

```text
SNMP version: v3
Security level: authPriv
Username: librenms
Auth algorithm: SHA
Privacy algorithm: AES
```

## What LibreNMS can inventory

Depending on RouterOS/platform support, LibreNMS can collect:

- identity and RouterOS version
- physical/logical interfaces
- traffic and errors
- bridge/interface information
- FDB/MAC data
- sensors and system resources
- LLDP neighbor data where exposed

## Optional enhanced VLAN discovery

LibreNMS has a RouterOS helper script (`LNMS_vlans`) that can provide detailed VLAN information from RouterOS bridge/VLAN configuration.

**Security warning:** the helper requires an SNMP community/user with write capability because LibreNMS triggers a RouterOS script through SNMP. Do **not** enable SNMP write globally just for convenience.

If this feature is required:

1. Restrict SNMP to the LibreNMS server `/32`.
2. Use SNMPv3 authPriv.
3. Review the helper script before deploying it.
4. Give the script only the policies required by RouterOS/LibreNMS documentation.
5. Document the exception as privileged network-management access.
6. Monitor configuration changes and SNMP access.

The base deployment in this repository deliberately remains **read-only**.

## Endpoint location caveat

On MikroTik bridges, a MAC may appear on an uplink/trunk or hardware-offloaded bridge path. Correlate bridge host/FDB information with topology before declaring that a port is the physical endpoint port.
