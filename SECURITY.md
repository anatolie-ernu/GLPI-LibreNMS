# Security Policy

## Secrets

Never commit any of the following:

- production `.env` files
- SNMPv3 authentication/privacy passwords
- Active Directory credentials
- database passwords
- API tokens
- private keys or certificates

Use `.env.example` only as a template.

## Network management security

- Prefer SNMPv3 `authPriv`.
- Restrict SNMP access to the LibreNMS management IP using ACLs or RouterOS address restrictions.
- Keep MikroTik SNMP write access disabled unless a reviewed feature explicitly requires it.
- Do not expose GLPI, LibreNMS, databases, Redis or SNMP management interfaces directly to the Internet.
- Place web interfaces behind HTTPS for production use.

## Reporting vulnerabilities

For sensitive vulnerabilities, avoid posting secrets, production addresses or exploitable credentials in public GitHub issues. Provide enough sanitized detail to reproduce the issue safely.

## Dependency updates

Docker image updates should be tested in staging before production deployment. GLPI is pinned in the default `.env.example`; LibreNMS follows its rolling Docker image by default and should therefore be pulled under a controlled maintenance process.
