#!/bin/bash

################################################################################
# GLPI-LibreNMS + Nginx Proxy Manager - Docker Installer
#
# Installer simplu pentru a porni întregul stack pe Linux cu Docker
################################################################################

set -euo pipefail

readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m'

# ============================================================================
# FUNCȚII HELPER
# ============================================================================

log_info() {
    echo -e "${BLUE}[INFO]${NC} $*"
}

log_success() {
    echo -e "${GREEN}[✓]${NC} $*"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $*"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $*"
    exit 1
}

# ============================================================================
# VERIFICĂRI PREREQUISITE
# ============================================================================

check_prerequisites() {
    log_info "Verificare prerequisite..."
    
    # Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker nu e instalat. Instalează: https://docs.docker.com/engine/install/"
    fi
    log_success "Docker instalat"
    
    # Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose nu e instalat. Instalează: https://docs.docker.com/compose/install/"
    fi
    log_success "Docker Compose instalat"
    
    # Permisiuni Docker
    if ! docker ps &> /dev/null; then
        log_error "Nu ai permisiuni Docker. Rulează: sudo usermod -aG docker \$USER"
    fi
    log_success "Permisiuni Docker OK"
}

# ============================================================================
# BUILD & START
# ============================================================================

build_and_start() {
    log_info "Build și start containerele..."
    
    # Build discovery service
    log_info "Build npm-auto-discovery service..."
    docker-compose build npm-auto-discovery
    
    # Start all services
    log_info "Start containerele..."
    docker-compose up -d
    
    log_success "Containerele au pornit"
}

# ============================================================================
# WAIT & HEALTH CHECKS
# ============================================================================

wait_for_services() {
    log_info "Aștept containerele să fie gata..."
    
    local max_wait=120
    local elapsed=0
    
    while [ $elapsed -lt $max_wait ]; do
        # MySQL
        if docker-compose exec -T mysql mysqladmin ping -h 127.0.0.1 -u root -proot_secure_pass &> /dev/null; then
            log_success "MySQL: ready"
            break
        fi
        
        elapsed=$((elapsed + 5))
        log_info "Aștept MySQL... ($elapsed/$max_wait)"
        sleep 5
    done
    
    if [ $elapsed -ge $max_wait ]; then
        log_error "Timeout: MySQL nu a pornit în timp"
    fi
    
    # Wait for other services
    sleep 10
    
    log_info "Verificare status containerelor..."
    docker-compose ps
}

# ============================================================================
# AFFICHAGE INFORMAȚII
# ============================================================================

print_summary() {
    cat << EOF

╔══════════════════════════════════════════════════════════════╗
║     GLPI-LibreNMS + Nginx Proxy Manager - Instalare OK      ║
╚══════════════════════════════════════════════════════════════╝

✓ Containerele sunt RUNNING

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📍 ACCES (din rețea locală):

   Nginx Proxy Manager Admin:
      http://localhost:81/
      Adresa: http://<SERVER_IP>:81/

   GLPI:
      http://localhost:3000/
      Adresa: http://<SERVER_IP>:3000/
      Proxy: http://glpi.local/ (după configurare NPM)

   LibreNMS:
      http://localhost:8000/
      Adresa: http://<SERVER_IP>:8000/
      Proxy: http://librenms.local/ (după configurare NPM)

   MySQL:
      localhost:3306
      Root: root_secure_pass
      GLPI User: glpi / glpi_secure_pass
      LibreNMS User: librenms / librenms_secure_pass

   Redis:
      localhost:6379

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔐 LOGIN NGINX PROXY MANAGER:

   Email: admin@ernu.md
   Parola: Npm@ernu2025!

   ⚠️  SCHIMBĂ PAROLA LA PRIMA LOGARE!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔧 COMENZI UTILE:

   Vizualizare logs:
      docker-compose logs -f nginx-proxy-manager
      docker-compose logs -f glpi
      docker-compose logs -f librenms
      docker-compose logs -f npm-auto-discovery

   Stop containers:
      docker-compose down

   Restart services:
      docker-compose restart

   Status containers:
      docker-compose ps

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚙️  CONFIGURARE NGINX PROXY MANAGER:

   1. Deschide http://localhost:81/
   2. Login cu admin@ernu.md / Npm@ernu2025!
   3. Mergi la Settings → Schimbă parola
   4. Add SSL Certificate (Let's Encrypt)
   5. Auto-discovery va crea proxy hosts automat

   Labels Docker pentru aplicații noi:
      labels:
        npm.expose: "true"           # Activează auto-discovery
        npm.hostname: "app"          # Domain: app.local
        npm.port: "8080"             # Port (default: 80)
        npm.ssl: "false"             # Force SSL (default: false)
        npm.websockets: "false"      # WebSocket support

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 NEXT STEPS:

   [ ] 1. Accesează admin UI și schimbă parolele default
   [ ] 2. Configură certificat SSL (Let's Encrypt)
   [ ] 3. Inițializează GLPI (http://localhost:3000/)
   [ ] 4. Inițializează LibreNMS (http://localhost:8000/)
   [ ] 5. Configurează DNS local (.local domains)
   [ ] 6. Adaugă mai multe aplicații cu labels npm.expose

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Documentație completă: README.md

EOF
}

# ============================================================================
# MAIN
# ============================================================================

main() {
    echo -e "${BLUE}"
    cat << 'ASCII_ART'
╔═══════════════════════════════════════════════════════════════╗
║   GLPI-LibreNMS + Nginx Proxy Manager Installer v1.0         ║
║   Docker Edition                                              ║
╚═══════════════════════════════════════════════════════════════╝
ASCII_ART
    echo -e "${NC}"
    
    check_prerequisites
    build_and_start
    wait_for_services
    print_summary
    
    log_success "✓ Instalare completă!"
}

main "$@"
