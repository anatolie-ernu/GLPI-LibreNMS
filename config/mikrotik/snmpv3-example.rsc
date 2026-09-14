# MikroTik RouterOS - LibreNMS SNMPv3 authPriv example
# Replace all <PLACEHOLDER> values before applying.

/snmp community
set [find default=yes] read-access=no write-access=no
add name="librenms" addresses=<LIBRENMS_IP>/32 security=private authentication-protocol=SHA1 authentication-password="<AUTH_PASSWORD>" encryption-protocol=AES encryption-password="<PRIV_PASSWORD>" read-access=yes write-access=no

/snmp
set enabled=yes contact="<CONTACT>" location="<LOCATION>"

# Optional only if replies leave through an unexpected source address:
# /snmp set src-address=<MANAGEMENT_IP>

# Verification:
/snmp print detail
/snmp community print detail
