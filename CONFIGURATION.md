# Configurare - GLPI-LibreNMS + Nginx Proxy Manager

Documentație detaliată pentru toți pașii de configurare.

---

## 📋 Tabel de Conținut

1. [Trei Opțiuni de Configurare](#trei-opțiuni-de-configurare)
2. [Configurare Interactivă (Recommended)](#configurare-interactivă-recommended)
3. [Configurare cu Parametri Direct](#configurare-cu-parametri-direct)
4. [Configurare Manuală](#configurare-manuală)
5. [Variabile de Mediu (.env)](#variabile-de-mediu-env)
6. [Schimbare Post-Install](#schimbare-post-install)
7. [Migrare la DNS Diferit](#migrare-la-dns-diferit)

---

## 🔧 Trei Opțiuni de Configurare

### Opțiunea 1: Interactiv (RECOMMENDED)

**Best for:** Prima dată, vrei să fii sigur că totul e configurat corect

```bash
chmod +x install.sh
./install.sh
```

**Flow:**
1. Verifică prerequisite (Docker, Docker Compose)
2. Cere domain name
3. Cere hostname-uri pentru fiecare serviciu
4. Cere email și parola NPM
5. Afișează rezumatul
6. Cere confirmare
7. Generează `.env` file
8. Build și start containerele
9. Aștept să se gata serviciile
10. Afișează informații acces și DNS instructions

**Avantaje:**
- Interactiv, sigur, pas-cu-pas
- Validare input
- Afișează DNS instructions pe final
- Automat build + start

**Dezavantaje:**
- Cere input manual

---

### Opțiunea 2: Cu Parametri Direct

**Best for:** Scripturi automate, CI/CD pipelines, deployment repetat

```bash
chmod +x configure.sh
./configure.sh local glpi librenms npm admin@ernu.md MyPassword123!
```

**Sintaxă:**
```
./configure.sh <DOMAIN> <GLPI_HOST> <LIBRENMS_HOST> <NPM_HOST> <EMAIL> <PASSWORD>
```

**Exemplu:**
```bash
./configure.sh corp.internal glpi monitoring npm admin@corp.com SecurePass456!
```

**Output:**
```
[INFO] Generare .env file cu parametrii...
[✓] .env file generat

════════════════════════════════════════════════════════════════
  CONFIGURARE SALVATĂ
════════════════════════════════════════════════════════════════

Domain Name:          corp.internal

GLPI:                 glpi.corp.internal
LibreNMS:             monitoring.corp.internal
Nginx Proxy Manager:  npm.corp.internal

NPM Email:            admin@corp.com
NPM Password:         ••••••••••••••

════════════════════════════════════════════════════════════════

Următorul pas:
  docker-compose up -d
```

**Avantaje:**
- Non-interactiv
- Perfect pentru automation
- Rapid
- Ideal pentru scripting

**Dezavantaje:**
- Trebuie să știi exact parametrii
- Trebuie start manual: `docker-compose up -d`

---

### Opțiunea 3: Configurare Manuală

**Best for:** Full control, editori de text, environment variabile custom

```bash
# Copy template
cp .env.example .env

# Edit cu favoritul editor
nano .env          # Linux
code .env          # VS Code
notepad .env       # Windows

# Start manual
docker-compose up -d
```

**Exemplu .env:**
```bash
DOMAIN_NAME=mycompany.local
GLPI_HOSTNAME=glpi
LIBRENMS_HOSTNAME=librenms
NPM_HOSTNAME=npm

NPM_ADMIN_EMAIL=admin@company.com
NPM_ADMIN_PASSWORD=MySecurePass123!

MYSQL_ROOT_PASSWORD=RootPass456!
GLPI_DB_PASSWORD=GlpiPass789!
LIBRENMS_DB_PASSWORD=LibrenmsPass012!

GLPI_DOMAIN=glpi.mycompany.local
LIBRENMS_URL=http://librenms.mycompany.local

TZ=Europe/Bucharest
```

**Avantaje:**
- Full control
- Poți seta custom variabile
- Perfect pentru production setups
- Poți version control .env custom

**Dezavantaje:**
- Manual, mai lent
- Trebuie să edițezi fișierul
- Trebuie start manual

---

## 🔄 Configurare Interactivă (RECOMMENDED)

### Step-by-Step

#### 1. Rulează Installerul

```bash
chmod +x install.sh
./install.sh
```

#### 2. Domain Name

```
[INPUT] Introdu domain-ul pentru servicii [default: local]:
  Domain: internal
[✓] Domain setat: internal
```

**Ce Domain alegem?**
- `.local` - BEST pentru local networks (default)
- `.internal` - Doar pentru intranet (private networks)
- `.corp` - Corporate networks
- `.test` - Testing environments
- `.dev` - Development environments

#### 3. Hostname-uri

```
[INPUT] Introdu hostname-uri pentru servicii:
  GLPI hostname [default: glpi]: 
[✓] GLPI: glpi.internal

  LibreNMS hostname [default: librenms]: 
[✓] LibreNMS: librenms.internal

  Nginx Proxy Manager hostname [default: npm]: 
[✓] NPM: npm.internal
```

**Rezultat:**
- GLPI accesibil la: `http://glpi.internal/`
- LibreNMS accesibil la: `http://librenms.internal/`
- NPM Admin UI la: `http://npm.internal:81/`

#### 4. NPM Credentials

```
[INPUT] Configurare Nginx Proxy Manager:
  NPM Admin Email [default: admin@ernu.md]: your@email.com
[✓] Email: your@email.com

  NPM Admin Password [default: Npm@ernu2025!]: 
[✓] Parola setată (length: 16)
```

#### 5. Rezumat & Confirmare

```
════════════════════════════════════════════════════════════════
  DOMAIN & HOSTNAMES
════════════════════════════════════════════════════════════════
  Domain Name:          internal
  
  GLPI:                 glpi.internal
  LibreNMS:             librenms.internal
  Nginx Proxy Manager:  npm.internal

════════════════════════════════════════════════════════════════
  NPM CREDENTIALS
════════════════════════════════════════════════════════════════
  Email:                your@email.com
  Password:             ••••••••••••••••••

════════════════════════════════════════════════════════════════

Continui cu instalarea? (y/n): y
```

#### 6. Generare .env

```
[INFO] Generare .env file...
[✓] .env file generat
```

Fișierul `.env` va conține toate valorile introduse.

#### 7. Build & Start

```
[INFO] Verificare prerequisite...
[✓] Docker instalat
[✓] Docker Compose instalat
[✓] Permisiuni Docker OK

[INFO] Build și start containerele...
[INFO] Build npm-auto-discovery service...
[INFO] Start containerele...
[✓] Containerele au pornit

[INFO] Aștept containerele să fie gata...
[✓] MySQL: ready
```

#### 8. DNS Instructions

```
╔══════════════════════════════════════════════════════════════╗
║              CONFIGURARE DNS LOCAL (.local)                  ║
╚══════════════════════════════════════════════════════════════╝

Pentru a accesa serviciile prin domeniu (glpi.internal),
trebuie să configurezi DNS local:

┌──────────────────────────────────────────────────────────────┐
│ OPȚIUNE 1: dnsmasq (Recommended)                            │
└──────────────────────────────────────────────────────────────┘

  Editează: /etc/dnsmasq.d/glpi-local.conf

    address=/.internal/<SERVER_IP>

  Restart: sudo systemctl restart dnsmasq

...etc
```

---

## 📝 Configurare cu Parametri Direct

### Sintaxă

```bash
./configure.sh <DOMAIN> <GLPI_HOST> <LIBRENMS_HOST> <NPM_HOST> <EMAIL> <PASSWORD>
```

### Exemplu 1: Local Network

```bash
./configure.sh local glpi librenms npm admin@ernu.md Npm@ernu2025!
```

Rezultat:
- `glpi.local`
- `librenms.local`
- `npm.local:81`

### Exemplu 2: Corporate Network

```bash
./configure.sh corp.internal it-glpi monitor npm sysadmin@corp.com CorpPass123!
```

Rezultat:
- `it-glpi.corp.internal`
- `monitor.corp.internal`
- `npm.corp.internal:81`

### Exemplu 3: Testing Environment

```bash
./configure.sh test.dev glpi-test librenms-test npm-test admin@test.dev TestPass456!
```

Rezultat:
- `glpi-test.test.dev`
- `librenms-test.test.dev`
- `npm-test.test.dev:81`

### After Configuration

```bash
# Start containerele
docker-compose up -d

# Verifică status
docker-compose ps

# Verifică logs
docker-compose logs -f
```

---

## 📄 Configurare Manuală

### 1. Copy Template

```bash
cp .env.example .env
```

### 2. Edit .env

```bash
nano .env  # Linux/macOS
code .env  # VS Code
```

### 3. Exemplu .env Complet

```ini
# ============================================================================
# DOMAIN & HOSTNAME CONFIGURATION
# ============================================================================

DOMAIN_NAME=internal
GLPI_HOSTNAME=glpi
LIBRENMS_HOSTNAME=monitoring
NPM_HOSTNAME=npm

# ============================================================================
# NGINX PROXY MANAGER CREDENTIALS
# ============================================================================

NPM_ADMIN_EMAIL=admin@example.com
NPM_ADMIN_PASSWORD=MySecurePassword123!

# ============================================================================
# DATABASE CREDENTIALS
# ============================================================================

MYSQL_ROOT_PASSWORD=RootPassword456!
GLPI_DB_PASSWORD=GlpiPassword789!
LIBRENMS_DB_PASSWORD=LibrenmsPassword012!

# ============================================================================
# APPLICATION SETTINGS
# ============================================================================

GLPI_DOMAIN=glpi.internal
LIBRENMS_URL=http://monitoring.internal
TZ=Europe/Bucharest
```

### 4. Start Docker Compose

```bash
docker-compose up -d
```

### 5. Verificare

```bash
# Check containers
docker-compose ps

# Check logs
docker-compose logs npm-auto-discovery
```

---

## 🌍 Variabile de Mediu (.env)

### Domain Configuration

```bash
# Domain suffix pentru toate serviciile
DOMAIN_NAME=local

# Hostname-uri individuale
GLPI_HOSTNAME=glpi              # → glpi.local
LIBRENMS_HOSTNAME=librenms      # → librenms.local
NPM_HOSTNAME=npm                # → npm.local
```

### Nginx Proxy Manager

```bash
# Email admin
NPM_ADMIN_EMAIL=admin@ernu.md

# Password admin (SCHIMBĂ PE FIRST LOGIN!)
NPM_ADMIN_PASSWORD=Npm@ernu2025!
```

### Database Credentials

```bash
# MySQL Root
MYSQL_ROOT_PASSWORD=root_secure_pass

# GLPI User
GLPI_DB_PASSWORD=glpi_secure_pass

# LibreNMS User
LIBRENMS_DB_PASSWORD=librenms_secure_pass
```

### Application URLs

```bash
# GLPI domain
GLPI_DOMAIN=glpi.local

# LibreNMS URL
LIBRENMS_URL=http://librenms.local

# Timezone
TZ=Europe/Bucharest
```

---

## 🔄 Schimbare Post-Install

### Schimbă Domain Name

```bash
# Edit .env
nano .env
# Schimbă: DOMAIN_NAME=newdomain

# Restart services
docker-compose restart npm-auto-discovery

# Update DNS config
# /etc/dnsmasq.d/glpi-local.conf
# address=/.newdomain/<IP>
```

### Schimbă NPM Password

```bash
# Via Admin UI: http://npm.local:81/
# Settings → Change Password
```

### Schimbă Database Passwords

⚠️ **COMPLEX!** Implică restart și reinitializare.

```bash
# Edit .env cu noile password-uri
nano .env

# Delete volumes (WARNING: PIERDE DATELE!)
docker-compose down -v

# Restart cu noi parametrii
docker-compose up -d
```

---

## 📍 Migrare la DNS Diferit

### De la `.local` la `.internal`

```bash
# 1. Edit .env
sed -i 's/DOMAIN_NAME=local/DOMAIN_NAME=internal/' .env

# 2. Restart auto-discovery
docker-compose restart npm-auto-discovery

# 3. Update DNS
# /etc/dnsmasq.d/glpi-local.conf
# address=/.internal/<IP>

# 4. Update /etc/hosts (local machine)
# <IP> glpi.internal
# <IP> librenms.internal
# <IP> npm.internal
```

### De la Hostname-uri Generic la Custom

```bash
# Exemplu: glpi → it-asset-mgmt

# 1. Edit .env
nano .env
# Schimbă: GLPI_HOSTNAME=it-asset-mgmt

# 2. Restart
docker-compose restart npm-auto-discovery

# 3. NPM Admin UI va activa noul proxy
# Observă logs: docker-compose logs npm-auto-discovery

# 4. Update DNS: it-asset-mgmt.local
```

---

## ✅ Checklist Post-Configuration

- [ ] `.env` file generat
- [ ] Docker containers running
- [ ] MySQL healthy (databases create)
- [ ] NPM Admin UI accesibil (port 81)
- [ ] GLPI accesibil (port 3000)
- [ ] LibreNMS accesibil (port 8000)
- [ ] Auto-discovery service running
- [ ] DNS local configurat (.local domains)
- [ ] NPM password schimbat
- [ ] GLPI admin initialized
- [ ] LibreNMS admin initialized

---

**Next:** [README.md](./README.md) pentru instrucțiuni post-install și operaționale.

