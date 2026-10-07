---
title: "GLPI + LibreNMS"
subtitle: "Ghid complet de instalare, configurare si operare pentru Cisco si MikroTik"
author: "anatolie-ernu/GLPI-LibreNMS"
date: "14 septembrie 2026"
lang: ro
---

# Despre acest document

Acest ghid reuneste si extinde documentatia repository-ului **GLPI-LibreNMS** intr-un document operational unic. Scopul este implementarea unei platforme self-hosted care poate raspunde la doua intrebari diferite:

1. **Ce este acest asset?** - GLPI.
2. **Unde este conectat in retea?** - LibreNMS.

Rezultatul urmarit este corelarea:

```text
Computer -> IP -> MAC -> VLAN -> Switch -> Physical Port
```

Stack-ul este destinat in principal retelelor enterprise cu switch-uri **Cisco IOS/IOS XE** si **MikroTik RouterOS**.

> Important: un MAC invatat pe un uplink/trunk nu demonstreaza ca endpoint-ul este conectat fizic pe acel port. Pentru localizare se folosesc impreuna FDB/MAC, VLAN, LLDP/CDP si topologia downstream.

# 1. Componente

| Componenta | Rol |
|---|---|
| GLPI | Asset Management / CMDB / inventar hardware si software |
| GLPI Agent | Inventarierea endpoint-urilor Windows/Linux |
| LibreNMS | Network discovery, SNMP polling, FDB/MAC, VLAN, LLDP/CDP |
| MySQL | Baza de date GLPI |
| MariaDB | Baza de date LibreNMS |
| Redis | Cache si sesiuni LibreNMS |
| LibreNMS Dispatcher | Polling/discovery sidecar |

## 1.1 Ownership-ul datelor

**GLPI este autoritativ pentru:**

- calculatoare si servere;
- serial number, vendor, model;
- CPU, RAM, storage;
- OS si software instalat;
- user/departament/locatie;
- lifecycle si asset metadata;
- IP/MAC raportate de GLPI Agent.

**LibreNMS este autoritativ pentru:**

- starea curenta a switch-urilor/routerelor;
- interfaces si counters;
- VLAN-uri;
- FDB/MAC tables;
- ARP/NDP unde sunt disponibile;
- LLDP/CDP neighbors;
- port utilization/errors;
- device availability si sensors.

# 2. Arhitectura

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
         |                              | SNMPv3                        |
         |                       +------+-------+                       |
         +-----------------------| MikroTik     |-----------------------+
                                 | switches     |
                                 +--------------+
```

Docker foloseste retele separate `glpi-net` si `librenms-net`. In Stage 1 nu este necesara comunicarea directa GLPI-LibreNMS. O integrare API poate fi adaugata ulterior ca serviciu separat.

# 3. Cerinte recomandate

| Resursa | Baseline recomandat |
|---|---|
| OS | Ubuntu Server 24.04 LTS |
| CPU | 4-8 vCPU |
| RAM | 16 GB |
| Storage | 200-250 GB SSD minim |
| Network | IP static in management LAN |
| DNS/NTP | Configurate si functionale |
| Backup | Storage separat de host |

LibreNMS poate genera o cantitate semnificativa de RRD/history data. Monitorizeaza permanent capacitatea filesystem-ului Docker.

# 4. Cerinte firewall si routing

| Flux | Port | Directie | Status |
|---|---:|---|---|
| SNMP polling | UDP/161 | LibreNMS -> device | Obligatoriu |
| ICMP | ICMP | LibreNMS -> device | Recomandat |
| GLPI web | TCP/8081 implicit | Admin/Agent -> host | Stage 1 |
| LibreNMS web | TCP/8000 implicit | Admin -> host | Stage 1 |
| SNMP traps | UDP/162 | Device -> LibreNMS | Optional |
| Syslog | UDP/514 | Device -> LibreNMS | Optional |
| HTTPS | TCP/443 | User/Agent -> reverse proxy | Productie |

Recomandari:

- SNMP trebuie permis numai din IP-ul LibreNMS.
- MySQL, MariaDB si Redis nu se publica in exterior.
- Porturile 8081/8000 nu se expun pe Internet.
- Foloseste un VLAN de management si routing stabil catre echipamente.

# 5. Structura repository

```text
GLPI-LibreNMS/
├── README.md
├── SECURITY.md
├── LICENSE
├── compose.yml
├── .env.example
├── docs/
│   ├── INSTALL.md
│   ├── ARCHITECTURE.md
│   ├── CISCO-SNMPV3.md
│   ├── MIKROTIK-SNMPV3.md
│   ├── GLPI-AGENT.md
│   ├── BACKUP-RESTORE.md
│   ├── TROUBLESHOOTING.md
│   └── COMPLETE-GUIDE-RO.md
├── config/
│   ├── cisco/snmpv3-example.txt
│   └── mikrotik/snmpv3-example.rsc
├── scripts/
│   ├── install-docker.sh
│   ├── validate.sh
│   ├── deploy.sh
│   ├── status.sh
│   └── backup.sh
└── .github/workflows/
```

# 6. Instalarea hostului si Docker

## 6.1 Pregatirea Ubuntu

```bash
sudo apt update
sudo apt full-upgrade -y
sudo reboot
```

Configureaza IP static, DNS, NTP si hostname/FQDN inainte de deployment.

## 6.2 Clonarea repository-ului

```bash
cd /opt
sudo git clone https://github.com/anatolie-ernu/GLPI-LibreNMS.git
sudo chown -R $USER:$USER /opt/GLPI-LibreNMS
cd /opt/GLPI-LibreNMS
```

## 6.3 Instalarea Docker

```bash
sudo bash scripts/install-docker.sh
```

Verificare:

```bash
docker --version
docker compose version
systemctl status docker --no-pager
```

Daca utilizatorul a fost adaugat in grupul `docker`, executa logout/login inainte de rularea Docker fara `sudo`.

# 7. Configurarea `.env`

```bash
cd /opt/GLPI-LibreNMS
cp .env.example .env
chmod 600 .env
nano .env
```

Schimba obligatoriu:

```text
GLPI_DB_PASSWORD
LIBRENMS_DB_PASSWORD
PUID
PGID
```

Genereaza parole puternice:

```bash
openssl rand -base64 32
```

Verifica UID/GID:

```bash
id
```

Nu comite niciodata `.env` in Git. Repository-ul include `.gitignore` si verificare CI, dar acestea nu inlocuiesc secret management-ul operational.

# 8. Imagini si servicii Docker

Configuratia curenta din `.env.example` foloseste:

| Serviciu | Imagine |
|---|---|
| GLPI | `glpi/glpi:11.0.8` |
| GLPI DB | `mysql:8.4` |
| LibreNMS | `librenms/librenms:latest` |
| LibreNMS DB | `mariadb:10` |
| Redis | `redis:7.2-alpine` |

Volume persistente:

- `glpi_db` - MySQL GLPI;
- `glpi_data` - `/var/glpi`;
- `librenms_db` - MariaDB LibreNMS;
- `librenms_data` - `/data`, inclusiv RRD/config/history.

> Pentru productie controlata este recomandat sa testezi toate upgrade-urile in staging. Poti pin-ui imaginile la tag sau digest dupa validare.

# 9. Validare si deployment

## 9.1 Validare

```bash
bash scripts/validate.sh
```

Scriptul verifica:

- existenta `.env`;
- eliminarea placeholder-elor `CHANGE_ME`;
- `docker compose config`;
- sintaxa Bash a scripturilor.

## 9.2 Deployment

```bash
bash scripts/deploy.sh
```

Verificare:

```bash
docker compose ps
bash scripts/status.sh
```

Loguri:

```bash
docker compose logs --tail=200 glpi
docker compose logs --tail=200 glpi-db
docker compose logs --tail=200 librenms
docker compose logs --tail=200 librenms-dispatcher
docker compose logs --tail=200 librenms-db
```

Acces initial:

- GLPI: `http://SERVER-IP:8081`
- LibreNMS: `http://SERVER-IP:8000`

# 10. Configurarea initiala GLPI

1. Acceseaza GLPI si finalizeaza wizard-ul initial, daca apare.
2. Configureaza contul administrativ si elimina credentialele implicite.
3. Configureaza entitati, locatii si naming conventions.
4. Verifica automatic actions si cron worker-ul.
5. Configureaza GLPI Agent.
6. Configureaza LDAP/AD doar dupa validarea inventarului de baza.
7. Activeaza HTTPS inainte de rollout larg al agentilor.

GLPI trebuie folosit pentru asset inventory/CMDB, nu drept inlocuitor pentru FDB/LLDP polling in timp real.

# 11. GLPI Agent

Endpoint implicit pentru GLPI 10+ / 11:

```text
http://<GLPI_SERVER>:8081/front/inventory.php
```

Dupa reverse proxy foloseste URL-ul HTTPS canonic.

## 11.1 Pilot

1. Instaleaza GLPI Agent pe 2-5 statii reprezentative.
2. Configureaza target-ul catre GLPI.
3. Forteaza inventory.
4. Confirma ca fiecare device apare o singura data.
5. Verifica serial/model/OS/software/IP/MAC.
6. Cauta acelasi MAC in LibreNMS.
7. Valideaza switch/port/VLAN.

## 11.2 Rollout GPO

Model recomandat:

```text
Computer Configuration
  -> Policies
     -> Software Settings / Startup Script
        -> GLPI Agent MSI installation
```

Exemplu share:

```text
\\domain.example\NETLOGON\software\glpi-agent\
```

Rollout rings:

| Ring | Populatie |
|---|---|
| 0 | IT test devices |
| 1 | Departamentul IT |
| 2 | Business users selectati |
| 3 | Toate statiile administrate |
| 4 | Servere, dupa validare separata |

Deployment-ul trebuie sa fie idempotent. Nu incorpora credentiale administrative in startup scripts.

# 12. Configurarea initiala LibreNMS

1. Acceseaza `http://SERVER-IP:8000`.
2. Creeaza utilizatorul administrator.
3. Ruleaza validarea:

```bash
docker compose exec librenms lnms validate
```

4. Adauga un singur Cisco pilot.
5. Verifica interfaces, VLAN, FDB/MAC, LLDP/CDP, sensors si graphs.
6. Adauga un MikroTik pilot.
7. Extinde onboarding-ul numai dupa validarea pilotului.

Un device poate fi adaugat si din CLI:

```bash
docker compose exec librenms lnms device:add <HOSTNAME_OR_IP>
```

# 13. Cisco IOS / IOS XE - SNMPv3

Standard: **SNMPv3 authPriv**, read-only, ACL catre IP-ul LibreNMS.

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

Foloseste parole diferite pentru autentificare si privacy.

Daca setezi manual SNMP engine-id, configureaza-l inainte de crearea userilor SNMPv3.

Test de pe hostul LibreNMS:

```bash
sudo apt install -y snmp
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

Verificari Cisco:

```cisco
show snmp user
show snmp group
show access-lists ACL-LIBRENMS-SNMP
show lldp neighbors detail
show cdp neighbors detail
show mac address-table
```

Dupa polling confirma:

- ports corecte;
- VLAN-uri;
- FDB/MAC;
- LLDP/CDP neighbors;
- diferentierea uplink vs edge/access.

# 14. MikroTik RouterOS - SNMPv3

Configuratia de baza este read-only, cu acces limitat la LibreNMS `/32`.

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

Optional, daca raspunsul pleaca cu source address gresit:

```routeros
/snmp set src-address=<MANAGEMENT_IP>
```

Verificari:

```routeros
/snmp print detail
/snmp community print detail
/interface bridge host print
/ip neighbor print detail
```

Test SNMP din hostul LibreNMS este identic cu Cisco, folosind IP-ul MikroTik.

## 14.1 Enhanced VLAN discovery

LibreNMS poate utiliza helper-ul RouterOS `LNMS_vlans` pentru detalii VLAN. Acesta poate necesita SNMP write pentru a declansa un script RouterOS.

**Repository-ul lasa write-access dezactivat implicit.** Daca functia este necesara:

1. Restrictioneaza sursa la LibreNMS `/32`.
2. Pastreaza SNMPv3 authPriv.
3. Review-uieste scriptul.
4. Ofera numai policy-urile necesare.
5. Documenteaza exceptia ca acces privilegiat.
6. Monitorizeaza configuration changes.

# 15. Ordinea recomandata de onboarding

1. Un Cisco access switch.
2. Validare SNMPv3, interfaces, VLAN, FDB/MAC, LLDP/CDP.
3. Un MikroTik.
4. Validare SNMPv3, bridge/FDB si neighbors.
5. Core/distribution switches.
6. Restul access switches.
7. GLPI Agent pe cateva endpoint-uri.
8. Corelare end-to-end pentru 5-10 endpoint-uri.
9. Rollout larg al GLPI Agent.
10. Optional traps/syslog dupa stabilizarea polling-ului.

# 16. Corelarea PC -> IP -> MAC -> VLAN -> Switch -> Port

Exemplu:

```text
GLPI
  Hostname: HQ-PC-043
  IP:       10.129.21.43
  MAC:      00:25:90:AB:CD:EF

LibreNMS
  cauta MAC 00:25:90:AB:CD:EF
      |
      +-- access port -> endpoint probabil gasit
      |
      +-- uplink/trunk -> urmeaza LLDP/CDP catre downstream switch
                            |
                            +-- repeta FDB lookup

Rezultat:
  Switch: HQ-ACCESS-SW-04
  Port:   Gi1/0/31
  VLAN:   129
```

Reguli:

- confirma ca FDB entry este recenta;
- confirma VLAN si port state;
- daca portul este trunk, continua downstream;
- coreleaza GLPI Agent IP/MAC cu ARP/FDB;
- tine cont de AP-uri, telefoane IP, mini-switch-uri si bridge-uri.

# 17. Securitate si hardening

- SNMPv3 `authPriv` pentru Cisco si MikroTik.
- SNMP read-only implicit.
- ACL/restrictie `/32` la LibreNMS.
- `.env` cu `chmod 600`, niciodata in Git.
- Databases si Redis fara porturi publice.
- GLPI si LibreNMS in management LAN.
- HTTPS pentru productie.
- MikroTik SNMP write dezactivat implicit.
- Backup separat si restore tests.
- Upgrade numai dupa staging validation.

Nu folosi community `public` sau SNMPv2c in productie daca echipamentul suporta SNMPv3.

# 18. Reverse proxy si HTTPS

In productie foloseste FQDN-uri interne, de exemplu:

| Serviciu | FQDN | Backend |
|---|---|---|
| GLPI | `glpi.example.local` | `http://docker-host:8081` |
| LibreNMS | `librenms.example.local` | `http://docker-host:8000` |

Recomandari:

- certificat emis de CA interna sau ACME;
- preserve `Host` si `X-Forwarded-*` headers;
- evita SSL inspection care rupe certificatul pentru GLPI Agent;
- activeaza HSTS numai dupa validarea completa HTTPS;
- actualizeaza target-ul GLPI Agent dupa migrare.

# 19. Backup

```bash
bash scripts/backup.sh
```

Backup-ul include:

- GLPI database dump;
- LibreNMS database dump;
- `/var/glpi` persistent data;
- `/data` LibreNMS persistent data;
- `compose.yml`;
- template `.env`;
- `SHA256SUMS`.

Fisierul real `.env` nu este copiat intentionat.

Verificare:

```bash
cd <BACKUP_DIRECTORY>
sha256sum -c SHA256SUMS
```

# 20. Restore

Ordine:

1. Opreste serviciile aplicative.
2. Restaureaza datele persistente.
3. Restaureaza bazele de date.
4. Porneste stack-ul.
5. Ruleaza `lnms validate`.
6. Verifica un endpoint GLPI si un switch.

Exemplu:

```bash
BACKUP=/opt/backups/glpi-librenms/20260914_150000

docker compose stop glpi librenms librenms-dispatcher

gzip -dc "$BACKUP/glpi-data.tar.gz" | \
  docker compose run --rm -T glpi sh -lc 'rm -rf /var/glpi/* && tar -C /var/glpi -xzf -'

gzip -dc "$BACKUP/librenms-data.tar.gz" | \
  docker compose run --rm -T librenms sh -lc 'rm -rf /data/* && tar -C /data -xzf -'

gzip -dc "$BACKUP/glpi-db.sql.gz" | \
  docker compose exec -T glpi-db sh -lc \
  'mysql -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" "$MYSQL_DATABASE"'

gzip -dc "$BACKUP/librenms-db.sql.gz" | \
  docker compose exec -T librenms-db sh -lc \
  'mariadb -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" "$MYSQL_DATABASE"'

docker compose up -d
bash scripts/status.sh
docker compose exec librenms lnms validate
```

> Un backup care nu a fost restaurat niciodata nu este demonstrat. Executa periodic restore tests si inregistreaza RPO/RTO.

# 21. Upgrade si mentenanta

Flux recomandat:

1. Citeste release notes.
2. Executa backup.
3. Verifica checksums.
4. Testeaza in staging.
5. Actualizeaza tag/digest numai dupa validare.
6. Ruleaza pull/up.
7. Verifica status si `lnms validate`.
8. Testeaza login, inventory si polling.
9. Pastreaza rollback plan.

```bash
bash scripts/backup.sh
docker compose pull
docker compose up -d
bash scripts/status.sh
docker compose exec librenms lnms validate
```

# 22. Troubleshooting

## 22.1 Status si logs

```bash
docker compose ps
bash scripts/status.sh

docker compose logs --tail=200 glpi
docker compose logs --tail=200 glpi-db
docker compose logs --tail=200 librenms
docker compose logs --tail=200 librenms-dispatcher
docker compose logs --tail=200 librenms-db
```

## 22.2 SNMPv3 nu functioneaza

Verifica:

- routing catre management IP;
- UDP/161;
- username;
- `authPriv`;
- auth algorithm/password;
- privacy algorithm/password;
- ACL Cisco sau MikroTik `/32`;
- source IP real al LibreNMS;
- VRF/routing table folosit de device.

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

## 22.3 MAC apare pe uplink

Este normal. Urmareste LLDP/CDP/neighbor topology downstream si repeta FDB lookup pana la portul edge final.

## 22.4 Duplicate GLPI computers

Verifica:

- agent identity;
- serial number quality;
- Windows cloned images;
- assets create manual;
- reinstall/enrollment history.

Nu sterge duplicatele pana nu stabilesti recordul autoritativ.

## 22.5 Disk usage / restart loop

```bash
df -h
docker system df
docker volume ls
docker inspect <container>
docker compose logs --tail=300 <service>
```

# 23. Runbook operational

| Frecventa | Actiune |
|---|---|
| Zilnic | Alerte LibreNMS, restart/unhealthy, disk critic |
| Saptamanal | Device down, polling errors, GLPI agent failures, backup status |
| Lunar | Patching host, image review, capacity trend, access review |
| Trimestrial | Restore test, SNMP ACL/users, certificate expiry |
| Schimbare majora | Backup, staging, change ticket, rollback plan |

Quick health check:

```bash
cd /opt/GLPI-LibreNMS
bash scripts/status.sh
docker compose exec librenms lnms validate
df -h
docker system df
```

# 24. Checklist productie

- [ ] Ubuntu 24.04 patch-uit, IP static, DNS si NTP OK.
- [ ] Docker Engine si Compose plugin instalate.
- [ ] `.env` cu parole puternice si `chmod 600`.
- [ ] GLPI si LibreNMS fara restart loop.
- [ ] GLPI functional si cron worker activ.
- [ ] LibreNMS `lnms validate` fara FAIL critic.
- [ ] Cisco pilot SNMPv3 authPriv + ACL + LLDP/CDP validat.
- [ ] MikroTik pilot SNMPv3 + `/32` + write disabled validat.
- [ ] FDB/MAC si VLAN validate.
- [ ] GLPI Agent pilot pe 2-5 endpoint-uri.
- [ ] Corelare GLPI MAC -> LibreNMS switch/port confirmata.
- [ ] Reverse proxy + HTTPS configurat.
- [ ] Backup automatizat.
- [ ] Restore test executat.
- [ ] DB/Redis nu sunt expuse extern.
- [ ] CI repository green.

# Anexa A - `.env.example`

```dotenv
# General
TZ=Europe/Chisinau
PUID=1000
PGID=1000

# Published ports
GLPI_HTTP_PORT=8081
LIBRENMS_HTTP_PORT=8000

# Images
GLPI_IMAGE=glpi/glpi:11.0.8
GLPI_DB_IMAGE=mysql:8.4
LIBRENMS_IMAGE=librenms/librenms:latest
LIBRENMS_DB_IMAGE=mariadb:10
REDIS_IMAGE=redis:7.2-alpine

# GLPI database
GLPI_DB_NAME=glpi
GLPI_DB_USER=glpi
GLPI_DB_PASSWORD=CHANGE_ME_STRONG_GLPI_DB_PASSWORD
GLPI_CRONTAB_ENABLED=1
GLPI_SKIP_AUTOINSTALL=false
GLPI_SKIP_AUTOUPDATE=false

# LibreNMS database
LIBRENMS_DB_NAME=librenms
LIBRENMS_DB_USER=librenms
LIBRENMS_DB_PASSWORD=CHANGE_ME_STRONG_LIBRENMS_DB_PASSWORD

# LibreNMS PHP/runtime settings
LIBRENMS_MEMORY_LIMIT=512M
LIBRENMS_MAX_INPUT_VARS=2000
LIBRENMS_UPLOAD_MAX_SIZE=32M
LIBRENMS_OPCACHE_MEM_SIZE=256

# Deployment metadata
BACKUP_DIR=/opt/backups/glpi-librenms
```

# Anexa B - Configuratie Cisco

Fisier repository: `config/cisco/snmpv3-example.txt`.

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

# Anexa C - Configuratie MikroTik

Fisier repository: `config/mikrotik/snmpv3-example.rsc`.

```routeros
/snmp community
set [find default=yes] read-access=no write-access=no
add name="librenms" addresses=<LIBRENMS_IP>/32 security=private authentication-protocol=SHA1 authentication-password="<AUTH_PASSWORD>" encryption-protocol=AES encryption-password="<PRIV_PASSWORD>" read-access=yes write-access=no
/snmp
set enabled=yes contact="<CONTACT>" location="<LOCATION>"
# /snmp set src-address=<MANAGEMENT_IP>
/snmp print detail
/snmp community print detail
```

# Anexa D - Comenzi utile

| Comanda | Scop |
|---|---|
| `sudo bash scripts/install-docker.sh` | Instaleaza Docker |
| `bash scripts/validate.sh` | Valideaza configuratia |
| `bash scripts/deploy.sh` | Deploy stack |
| `bash scripts/status.sh` | Status + HTTP checks |
| `bash scripts/backup.sh` | Backup complet |
| `docker compose exec librenms lnms validate` | Validate LibreNMS |
| `docker compose logs --tail=200 <service>` | Troubleshooting |

# Anexa E - Referinte oficiale

- Repository: <https://github.com/anatolie-ernu/GLPI-LibreNMS>
- GLPI Docker: <https://github.com/glpi-project/docker-images>
- GLPI documentation: <https://help.glpi-project.org/documentation/>
- GLPI Agent: <https://glpi-agent.readthedocs.io/>
- LibreNMS Docker: <https://docs.librenms.org/Installation/Docker/>
- LibreNMS documentation: <https://docs.librenms.org/>
- Docker Engine Ubuntu: <https://docs.docker.com/engine/install/ubuntu/>
- MikroTik RouterOS documentation: <https://manual.mikrotik.com/>
- Cisco documentation: <https://www.cisco.com/>

# Anexa F - Glosar

| Termen | Explicatie |
|---|---|
| CMDB | Configuration Management Database |
| FDB | Forwarding Database / tabela MAC |
| ARP | Mapare IPv4 -> MAC |
| LLDP | Link Layer Discovery Protocol |
| CDP | Cisco Discovery Protocol |
| SNMPv3 authPriv | SNMP cu autentificare si criptare |
| RRD | Round Robin Database |
| Access port | Port edge asociat endpoint-ului |
| Trunk/uplink | Port intre switch-uri / multiple VLAN-uri |
| RPO | Recovery Point Objective |
| RTO | Recovery Time Objective |
