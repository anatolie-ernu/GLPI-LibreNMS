# GLPI Agent Deployment

GLPI Agent provides the endpoint side of the inventory system. LibreNMS identifies the network attachment; GLPI Agent identifies the computer and its hardware/software state.

## Target data

For each workstation/server the desired inventory includes:

- hostname
- serial number / manufacturer / model
- CPU, RAM and storage
- operating system and version
- installed software
- logged/assigned user where available
- network adapters
- IP addresses
- MAC addresses

## GLPI inventory endpoint

With the Docker deployment in this repository, the inventory endpoint is normally:

```text
http://<GLPI_SERVER>:8081/front/inventory.php
```

When a reverse proxy/HTTPS name is deployed, use that canonical HTTPS URL instead.

## Pilot first

Before domain-wide deployment:

1. Install GLPI Agent manually on 2-5 representative Windows machines.
2. Point them to the GLPI inventory endpoint.
3. Force an inventory.
4. Confirm the device appears exactly once in GLPI.
5. Verify IP and MAC addresses.
6. Search the same MAC address in LibreNMS and confirm the expected switch/port path.

## Windows GPO deployment design

Recommended enterprise pattern:

```text
Computer Configuration
  -> Policies
     -> Software Settings / Startup Script
        -> GLPI Agent MSI installation
```

Keep the MSI in a domain-accessible read-only software distribution share, for example:

```text
\\domain.example\NETLOGON\software\glpi-agent\
```

The deployment should be idempotent: detect an existing supported GLPI Agent installation before installing/upgrading.

## GPO rollout rings

Use staged groups/OUs:

```text
Ring 0 - IT test devices
Ring 1 - IT department
Ring 2 - selected business users
Ring 3 - all managed workstations
Ring 4 - servers, after separate validation
```

## Required production controls

- Use HTTPS before broad deployment when traffic crosses untrusted or shared network segments.
- Validate the server certificate.
- Restrict who can change the agent configuration.
- Do not embed administrative credentials in startup scripts.
- Keep installation packages checksummed and version-controlled through the software distribution process.
- Test upgrades on Ring 0 before broad rollout.

## Correlation test

A successful end-to-end test should look like:

```text
GLPI
  Hostname: HQ-PC-043
  IP:       10.129.21.43
  MAC:      00:25:90:AB:CD:EF

LibreNMS
  MAC:      00:25:90:AB:CD:EF
  Switch:   HQ-ACCESS-SW-04
  Port:     Gi1/0/31
  VLAN:     129
```

Future stages of this repository can automate this correlation through the GLPI and LibreNMS APIs.
