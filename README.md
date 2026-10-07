# GLPI-LibreNMS + Nginx Proxy Manager (Docker)

**Autor:** Anatolie Ernu (ernu.md)  
**Versiune:** 1.0  
**Date:** October 2026  
**Licență:** Proprietary (ERNU.EU)

---

## 📋 Descriere

Stack complet **Docker** cu:
- **GLPI** - IT Asset Management
- **LibreNMS** - Network Monitoring
- **Nginx Proxy Manager** - Publicare în rețea locală cu auto-discovery
- **MySQL** - Database server
- **Redis** - Cache server
- **Auto-Discovery Service** - Publicare automată a containerelor

---

## ⚡ Instalare Rapidă (30 minute)

### 1. Prerequisite

```bash
# Linux cu Docker și Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Adaugă user în grup docker (evita sudo)
sudo usermod -aG docker $USER
newgrp docker
```

### 2. Clone Repository

```bash
git clone https://github.com/anatolie-ernu/GLPI-LibreNMS.git
cd GLPI-LibreNMS
```

### 3. Rulează Installer

```bash
chmod +x install.sh
./install.sh
```

**Output așteptat:**

```
[INFO] Verificare prerequisite...
[✓] Docker instalat
[✓] Docker Compose instalat
[INFO] Build și start containerele...
[INFO] Aștept containerele să fie gata...
[✓] MySQL: ready
```

### 4. Acces Aplicații

```bash
# Nginx Proxy Manager Admin
http://localhost:81/

# GLPI
http://localhost:3000/

# LibreNMS
http://localhost:8000/

# MySQL
localhost:3306 (root / root_secure_pass)

# Redis
localhost:6379
```

---

## 🏗️ Arhitectură

```
┌─────────────────────────────────────────────────────────┐
│                 Docker Network                           │
│              (172.25.0.0/16 - glpi-net)                 │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌────────────────────────────────────────────┐        │
│  │   Nginx Proxy Manager (jc21/npm)           │        │
│  │   Port 80/443 (HTTP/HTTPS)                 │        │
│  │   Port 81 (Admin UI)                       │        │
│  │   - Auto-routes from Docker labels         │        │
│  │   - SSL/TLS support (Let's Encrypt)        │        │
│  └────────────────────────────────────────────┘        │
│         ↑           ↑           ↑                       │
│   ┌─────┴────┬─────┴────┬──────┴──────┐               │
│   │          │          │             │               │
│   ↓          ↓          ↓             ↓               │
│  ┌───────┐  ┌──────┐  ┌──────┐  ┌──────────┐         │
│  │ GLPI  │  │ Lib- │  │MySQL │  │ Redis   │         │
│  │:3000  │  │NMS   │  │:3306 │  │:6379   │         │
│  │       │  │:8000 │  │      │  │        │         │
│  └───────┘  └──────┘  └──────┘  └──────────┘         │
│                                                        │
│  ┌────────────────────────────────────────────┐        │
│  │  npm-auto-discovery                       │        │
│  │  - Scanează labels Docker npm.expose=true │        │
│  │  - Crează proxy hosts automat             │        │
│  │  - Interval: 5 minute                     │        │
│  └────────────────────────────────────────────┘        │
│                                                        │
└─────────────────────────────────────────────────────────┘
```

---

## 📦 Fișiere Incluse

```
.
├── docker-compose.yml              # Configurație containerelor
├── install.sh                       # Installer script
├── README.md                        # Această documentație
├── init-databases.sql               # Inițializare baze de date
├── requirements-discovery.txt       # Python dependencies
├── npm-auto-discovery.py           # Auto-discovery service (Python)
└── Dockerfile.discovery            # Dockerfile pentru discovery
```

---

## 🔧 Configurare Post-Install

### 1. Nginx Proxy Manager - Admin UI

**Adresă:** `http://localhost:81/` (sau `http://<SERVER_IP>:81/`)

**Login Default:**
- Email: `admin@ernu.md`
- Parola: `Npm@ernu2025!`

**Post-Login Setup:**

```
1. Settings → General
   - Change Admin Email
   - Change Admin Password ⚠️ IMPORTANT!
   - Set Application Title

2. Settings → Nginx
   - Enable HTTP/2 Support: ON
   - Enable WebSocket Support: ON
   - Worker Processes: auto

3. SSL Certificates
   - Click "Add SSL Certificate"
   - Select "Let's Encrypt"
   - Email: your@email.com
   - Use DNS challenge for wildcard (*.local)
```

### 2. GLPI - Configurare Inițială

**Adresă:** `http://localhost:3000/` (sau `http://<SERVER_IP>:3000/`)

```
1. Selectează limbă: English / Română
2. Selectează opțiune install:
   - "Install"
3. Completează:
   - SQL Host: mysql
   - SQL User: glpi
   - SQL Password: glpi_secure_pass
   - SQL Database: glpi
   - Default user: admin
   - Default password: admin
4. Click "Install"
```

**Post-Install:**
- Login cu admin / admin
- Settings → Schimbă parolă
- Configură settings generale

### 3. LibreNMS - Configurare Inițială

**Adresă:** `http://localhost:8000/` (sau `http://<SERVER_IP>:8000/`)

```
1. Click "Let's Get Started"
2. Selectează "MySQL" ca database
3. Completează:
   - Hostname: mysql
   - Database: librenms
   - Username: librenms
   - Password: librenms_secure_pass
4. Click "Check Connection"
5. Creează admin user
6. Click "Build Database"
```

**Post-Install:**
- Login cu admin user
- Settings → General
- Adaugă devices

### 4. DNS Local Configuration

**Opțiunea 1: dnsmasq (Recommended)**

```bash
# /etc/dnsmasq.d/glpi-local.conf
address=/.local/<SERVER_IP>
```

**Opțiunea 2: /etc/hosts (Quick)**

```bash
# /etc/hosts
<SERVER_IP> glpi.local
<SERVER_IP> librenms.local
<SERVER_IP> npm.local
```

**Opțiunea 3: Windows Hosts**

```
C:\Windows\System32\drivers\etc\hosts
<SERVER_IP> glpi.local
<SERVER_IP> librenms.local
<SERVER_IP> npm.local
```

---

## 🔄 Auto-Discovery Mechanism

### How It Works

```
Container cu label npm.expose=true
        ↓
npm-auto-discovery scanner (fiecare 5 minute)
        ↓
Crează proxy host automat în NPM
        ↓
Domain <app>.local → <container>:<port>
```

### Docker Labels

Adaugă labels containerului pentru a-l expune automat:

```yaml
services:
  my-app:
    image: my-app:latest
    labels:
      npm.expose: "true"              # REQUIRED - Activează discovery
      npm.hostname: "myapp"           # Domain: myapp.local
      npm.port: "8080"                # Port forward (default: 80)
      npm.ssl: "false"                # Force SSL redirect
      npm.websockets: "false"         # WebSocket support
```

### Exemplu - Adaugă aplicație nouă

```yaml
# Adaugă în docker-compose.yml:
  my-new-app:
    image: my-app:latest
    container_name: my-new-app
    ports:
      - "5000:5000"
    networks:
      - glpi-net
    labels:
      npm.expose: "true"
      npm.hostname: "myapp"
      npm.port: "5000"
```

```bash
# Restart docker-compose
docker-compose up -d my-new-app

# Verifică logs
docker-compose logs npm-auto-discovery
# [2026-10-07 14:22:18] ✓ Proxy creat: myapp.local → my-new-app:5000
```

---

## 📊 Comenzi Utile

### Status & Logs

```bash
# Vizualizează status containerelor
docker-compose ps

# Logs în real-time
docker-compose logs -f

# Logs per service
docker-compose logs -f nginx-proxy-manager
docker-compose logs -f npm-auto-discovery
docker-compose logs -f glpi
docker-compose logs -f librenms
docker-compose logs -f mysql

# Logs cu timestamp
docker-compose logs --timestamps
```

### Control Containerelor

```bash
# Start
docker-compose up -d

# Stop (fără a șterge volumele)
docker-compose down

# Restart specific service
docker-compose restart glpi

# Rebuild service
docker-compose up -d --build npm-auto-discovery

# Remove everything (inclusive volumes)
docker-compose down -v
```

### Database Access

```bash
# MySQL CLI
docker-compose exec mysql mysql -u root -proot_secure_pass

# Exemplu: Verificare GLPI database
mysql> USE glpi;
mysql> SHOW TABLES;

# Backup MySQL
docker-compose exec mysql mysqldump -u root -proot_secure_pass --all-databases > backup.sql

# Restore MySQL
docker-compose exec -T mysql mysql -u root -proot_secure_pass < backup.sql
```

### Docker Network

```bash
# Verificare network
docker network ls
docker network inspect glpi-librenms_glpi-net

# Test connectivity intre containers
docker-compose exec glpi ping mysql
docker-compose exec npm curl http://nginx-proxy-manager:81/health
```

---

## 🐛 Troubleshooting

### Container nu pornește

```bash
# Verifică logs
docker-compose logs <service_name>

# Exemplu
docker-compose logs mysql
```

### Port deja ocupat

```bash
# Găsește procesul pe port
lsof -i :80
lsof -i :443
lsof -i :81

# Oprește procesul
kill -9 <PID>

# Sau schimbă port în docker-compose.yml
# ports:
#   - "8080:80"  # Port 8080 local
```

### MySQL nu e gata

```bash
# MySQL are nevoie de timp să se inițializeze
# Așteptă ~30 secunde

# Verifică dacă e gata
docker-compose exec mysql mysqladmin ping -u root -proot_secure_pass

# Până nu răspunde OK, alte servicii așteptă
```

### Auto-discovery nu funcționează

```bash
# Verifică serviciul
docker-compose logs npm-auto-discovery

# Verifica containerele cu label npm.expose
docker ps --format "table {{.Names}}\t{{.Labels}}"

# Forțează rescanning
docker-compose restart npm-auto-discovery

# Aștept 5 minute, apoi verifică admin NPM dacă au apărut proxies noi
```

### NPM Admin UI nu răspunde

```bash
# Verifică dacă e running
docker-compose ps nginx-proxy-manager

# Restart
docker-compose restart nginx-proxy-manager

# Verifică health
curl http://localhost:81/health

# Dacă database e corupt
docker-compose down
docker volume rm glpi-librenms_npm_data
docker-compose up -d nginx-proxy-manager
```

### GLPI / LibreNMS not accessible

```bash
# Verifică dacă container-ul e running
docker-compose ps glpi

# Verifică logs
docker-compose logs glpi

# Verifica network connectivity
docker-compose exec glpi ping mysql

# Restart container
docker-compose restart glpi
```

---

## 📈 Performance & Scaling

### Resource Limits

Containerele au seturi minimum de resource requests. Dacă ai probleme:

```yaml
# Editează docker-compose.yml și adaugă limit:
services:
  glpi:
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 2G
        reservations:
          cpus: '0.5'
          memory: 1G
```

### Backup & Recovery

```bash
# Backup databases
docker-compose exec mysql mysqldump -u root -proot_secure_pass --all-databases | gzip > backup-$(date +%Y%m%d).sql.gz

# Backup volumes
docker run --rm -v glpi-librenms_npm_data:/data -v $(pwd):/backup alpine tar czf /backup/npm-data.tar.gz /data
docker run --rm -v glpi-librenms_glpi_data:/data -v $(pwd):/backup alpine tar czf /backup/glpi-data.tar.gz /data

# Restore
gunzip < backup-20261007.sql.gz | docker-compose exec -T mysql mysql -u root -proot_secure_pass
```

---

## 🔐 Security Considerations

⚠️ **IMPORTANT** - Acest setup este pentru development/lab. Pentru production:

1. **Schimbă toate parolele default**
   ```bash
   # NPM Admin
   npm.local:81 → Settings → Change Password
   
   # GLPI Admin
   glpi.local → Settings → Change admin password
   
   # LibreNMS Admin
   librenms.local → Settings → Change admin password
   
   # MySQL Root
   Edit docker-compose.yml și schimbă MYSQL_ROOT_PASSWORD
   ```

2. **Configurează SSL/TLS**
   - NPM Admin → SSL Certificates
   - Let's Encrypt (wildcard: *.local)
   - Sau certificate propriu

3. **Restricționează firewall**
   ```bash
   # Doar porturile necesare
   sudo ufw allow 22    # SSH
   sudo ufw allow 80    # HTTP
   sudo ufw allow 443   # HTTPS
   # Port 81 și alte porturi - RESTRICTED
   ```

4. **Network Isolation**
   - Containers pe rețea privată (glpi-net)
   - NPM singur cu acces la 80/443
   - Nu expune MySQL, Redis direct

---

## 📞 Support & Resources

- **Nginx Proxy Manager Docs:** https://nginxproxymanager.com/
- **GLPI Documentation:** https://glpi-project.org/
- **LibreNMS Documentation:** https://docs.librenms.org/
- **Docker Compose Reference:** https://docs.docker.com/compose/

---

## 📝 Changelog

**v1.0 (Oct 2026)**
- Initial release
- Docker Compose setup
- Nginx Proxy Manager + auto-discovery
- GLPI + LibreNMS + MySQL + Redis
- Complete documentation

---

## 👨‍💻 Author

**Anatolie Ernu**  
- **Company:** ERNU.EU
- **Role:** IT & Security Consultant
- **Email:** ITSec@ernu.md
- **GitHub:** https://github.com/anatolie-ernu

---

## 📄 License

**Proprietary** - ERNU.EU  
© 2026 Anatolie Ernu. Toate drepturile rezervate.

---

**Last Updated:** October 7, 2026
