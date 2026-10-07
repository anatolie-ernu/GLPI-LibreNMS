# 🎉 GLPI-LibreNMS + Nginx Proxy Manager (Docker) - Setup Complet

**Status:** ✅ **READY TO DEPLOY**

---

## 📦 Ce Ai Primit

Stack complet **Docker** pentru publicarea automată a aplicațiilor în rețea locală cu **Nginx Proxy Manager**.

### Componentele Incluse

```
GLPI (IT Asset Management)
    ↓
LibreNMS (Network Monitoring)
    ↓
Nginx Proxy Manager (Reverse Proxy + Auto-Discovery)
    ↓
MySQL (Database)
    ↓
Redis (Cache)
    ↓
npm-auto-discovery (Python Service - Publicare Automată)
```

---

## 📂 Fișiere Incluse

| Fișier | Dimensiune | Descriere |
|--------|-----------|-----------|
| **README.md** | 15KB | Documentație completă + quick start |
| **CONFIGURATION.md** | 13KB | Opțiuni configurare + detalii |
| **install.sh** | 16KB | Installer interactiv (RECOMMENDED) |
| **configure.sh** | 4.3KB | Configurare cu parametri direct |
| **docker-compose.yml** | 6KB | Configurație containerelor |
| **npm-auto-discovery.py** | 14KB | Service Python (auto-discovery) |
| **Dockerfile.discovery** | ~400B | Docker image pentru discovery |
| **requirements-discovery.txt** | 65B | Python dependencies |
| **.env.example** | - | Template pentru .env |
| **init-databases.sql** | ~400B | SQL inițializare MySQL |

---

## 🚀 Quick Start (3 comenzi)

```bash
# 1. Clone (dacă încă nu ai)
git clone https://github.com/anatolie-ernu/GLPI-LibreNMS.git
cd GLPI-LibreNMS

# 2. Configurare (Interactiv - RECOMMENDED)
chmod +x install.sh
./install.sh

# 3. Gata! Containerele pornesc automat
```

**Output așteptat:** ~2-3 minute pentru build + start.

---

## ⚙️ Trei Opțiuni de Configurare

### Opțiunea 1: Interactiv (RECOMMENDED ⭐)

```bash
./install.sh
```

**Flow:**
- Cere domain name
- Cere hostname-uri (glpi, librenms, npm)
- Cere email și parola NPM
- Afișează rezumat
- Generează `.env` file
- Build și start containerele
- Afișează DNS instructions

**Best for:** Prima dată, vrei setup corect garantat

---

### Opțiunea 2: Cu Parametri Direct

```bash
chmod +x configure.sh
./configure.sh local glpi librenms npm admin@ernu.md Npm@ernu2025!
```

**Sintaxă:**
```
./configure.sh <DOMAIN> <GLPI_HOST> <LIBRENMS_HOST> <NPM_HOST> <EMAIL> <PASSWORD>
```

**Best for:** Scripting, CI/CD, automated deployment

---

### Opțiunea 3: Configurare Manuală

```bash
cp .env.example .env
nano .env              # Edit cu valorile tale
docker-compose up -d   # Start
```

**Best for:** Full control, custom variabile, production setups

---

## 📍 DNS Local (Obigatoriu!)

Așa accesezi serviciile prin domain (e.g., `glpi.local`):

### Linux (dnsmasq)

```bash
# /etc/dnsmasq.d/glpi-local.conf
address=/.local/<SERVER_IP>

# Restart
sudo systemctl restart dnsmasq
```

### Windows/macOS (/etc/hosts)

```
<SERVER_IP> glpi.local
<SERVER_IP> librenms.local
<SERVER_IP> npm.local
```

**Installer va afișa instrucțiuni DNS la final!**

---

## 🔑 Default Credentials

⚠️ **SCHIMBĂ LA PRIMA LOGARE!**

| Serviciu | User | Password |
|----------|------|----------|
| **NPM Admin** | admin@ernu.md | Npm@ernu2025! |
| **GLPI Admin** | admin | admin |
| **LibreNMS Admin** | admin | Set on init |
| **MySQL Root** | root | root_secure_pass |

---

## 🌐 URLs de Acces

După instalare și DNS config:

```
http://glpi.local/              → GLPI
http://librenms.local/          → LibreNMS
http://npm.local:81/            → Nginx Proxy Manager (Admin UI)

localhost:3000                  → GLPI direct
localhost:8000                  → LibreNMS direct
localhost:81                    → NPM Admin direct
localhost:3306                  → MySQL direct
localhost:6379                  → Redis direct
```

---

## 🤖 Auto-Discovery Feature

**Ce funcționează automat:**

Containerele cu label `npm.expose=true` sunt:

1. ✅ Detectate de `npm-auto-discovery` (fiecare 5 min)
2. ✅ Creat proxy host în NPM
3. ✅ Accesibile la `<hostname>.local`

**Exemplu Docker Compose:**

```yaml
services:
  my-app:
    image: my-app:latest
    labels:
      npm.expose: "true"        # MAGIC! 🎉
      npm.hostname: "myapp"     # Domain: myapp.local
      npm.port: "8080"          # Port forward
      npm.ssl: "false"          # Force SSL (optional)
      npm.websockets: "false"   # WebSocket (optional)
```

---

## 📋 Post-Install Checklist

După rularea installerului:

```
☐ Verifică containers: docker-compose ps
☐ Configurează DNS (.local domains)
☐ Login NPM: http://localhost:81/
  ☐ Schimbă parola admin
  ☐ Configură SSL (Let's Encrypt)
☐ Inițializează GLPI: http://localhost:3000/
☐ Inițializează LibreNMS: http://localhost:8000/
☐ Testează auto-discovery:
  ☐ Adaugă container cu npm.expose=true
  ☐ Observă logs: docker-compose logs npm-auto-discovery
  ☐ Verifica proxy creat în NPM Admin
```

---

## 📚 Documentație

- **README.md** - Overview + quick start + operaționale
- **CONFIGURATION.md** - Detalii configurare + opțiuni avansate
- **install.sh** - Inline comments cu explicații

---

## 🔧 Comenzi Utile

```bash
# Status
docker-compose ps

# Logs real-time
docker-compose logs -f

# Logs per service
docker-compose logs -f npm-auto-discovery
docker-compose logs -f glpi
docker-compose logs -f librenms

# Restart
docker-compose restart

# Stop (keep volumes)
docker-compose down

# Stop (delete everything)
docker-compose down -v
```

---

## 🐛 Troubleshooting

### Containerele nu pornesc

```bash
# Verifică logs
docker-compose logs mysql
docker-compose logs glpi
```

### Port deja ocupat

```bash
# Find process
lsof -i :80
lsof -i :443
lsof -i :81

# Kill process
kill -9 <PID>
```

### Auto-discovery nu funcționează

```bash
# Verifică logs
docker-compose logs npm-auto-discovery

# Verifică label
docker ps --format "table {{.Names}}\t{{.Labels}}"

# Redeploy
docker-compose restart npm-auto-discovery
```

**Full troubleshooting:** [README.md → Troubleshooting](#troubleshooting)

---

## 🛡️ Security Notes

⚠️ **Acest setup e pentru development/lab!** Pentru production:

```
✅ Schimbă TOATE parolele default
✅ Activează SSL/TLS (Let's Encrypt)
✅ Restricționează firewall (80, 443 only)
✅ Keepa .env în .gitignore
✅ Backup databases regular
✅ Monitor logs (Wazuh integration)
```

---

## 📞 Support

- **GitHub:** https://github.com/anatolie-ernu/GLPI-LibreNMS
- **Issues:** Report bugs și feature requests
- **Author:** Anatolie Ernu (ITSec@ernu.md)

---

## 📝 Changelog

**v1.0 (Oct 2026)**
- ✅ Initial release
- ✅ Docker Compose stack
- ✅ Interactive installer
- ✅ Auto-discovery service (Python)
- ✅ Full documentation
- ✅ Multiple configuration options

---

## 🎯 Next Steps

1. **Rulează installerul:** `./install.sh`
2. **Configurează DNS:** Follow instrucțiuni pe final
3. **Logează-te:** `http://npm.local:81/`
4. **Inițializează apps:** GLPI și LibreNMS
5. **Testează auto-discovery:** Adaugă container cu label
6. **Enjoy! 🎉**

---

**Gata pentru deployment!** 🚀

Orice întrebări, deschide issue pe GitHub.

---

**Status:** ✅ Production Ready  
**Last Updated:** October 7, 2026  
**Author:** Anatolie Ernu (ERNU.EU)
