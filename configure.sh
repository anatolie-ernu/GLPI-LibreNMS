#!/bin/bash

################################################################################
# Configuration Script - Manual Setup
#
# Folosi: ./configure.sh domain.name glpi librenms npm admin@email.com password
# Sau: ./configure.sh --interactive
################################################################################

set -euo pipefail

readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m'

log_info() {
    echo -e "${BLUE}[INFO]${NC} $*"
}

log_success() {
    echo -e "${GREEN}[✓]${NC} $*"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $*"
    exit 1
}

show_usage() {
    cat << EOF
Utilizare:

  ./configure.sh --interactive
    - Configurare interactivă

  ./configure.sh domain glpi_host librenms_host npm_host admin_email admin_password
    - Configurare directă cu parametri
    
    Exemplu:
    ./configure.sh local glpi librenms npm admin@ernu.md MyPassword123!

  ./configure.sh --help
    - Afișează acest mesaj

EOF
}

generate_env() {
    local domain="$1"
    local glpi_host="$2"
    local librenms_host="$3"
    local npm_host="$4"
    local npm_email="$5"
    local npm_pass="$6"
    
    log_info "Generare .env file cu parametrii..."
    
    cat > .env << EOF
# ============================================================================
# GLPI-LibreNMS + Nginx Proxy Manager Configuration
# ============================================================================
# Generated: $(date)
# ============================================================================

# Domain Configuration
DOMAIN_NAME=$domain
GLPI_HOSTNAME=$glpi_host
LIBRENMS_HOSTNAME=$librenms_host
NPM_HOSTNAME=$npm_host

# Nginx Proxy Manager
NPM_ADMIN_EMAIL=$npm_email
NPM_ADMIN_PASSWORD=$npm_pass

# Database Credentials (CHANGE IN PRODUCTION!)
MYSQL_ROOT_PASSWORD=root_secure_pass
GLPI_DB_PASSWORD=glpi_secure_pass
LIBRENMS_DB_PASSWORD=librenms_secure_pass

# Application Settings
GLPI_DOMAIN=$glpi_host.$domain
LIBRENMS_URL=http://$librenms_host.$domain
TZ=Europe/Bucharest
EOF
    
    log_success ".env file generat"
    
    cat << EOF

════════════════════════════════════════════════════════════════
  CONFIGURARE SALVATĂ
════════════════════════════════════════════════════════════════

Domain Name:          $domain

GLPI:                 $glpi_host.$domain
LibreNMS:             $librenms_host.$domain
Nginx Proxy Manager:  $npm_host.$domain

NPM Email:            $npm_email
NPM Password:         ••••••••••••••

════════════════════════════════════════════════════════════════

Următorul pas:
  docker-compose up -d

EOF
}

main() {
    echo -e "${BLUE}"
    cat << 'ASCII_ART'
╔═══════════════════════════════════════════════════════════════╗
║             Configuration Script v1.0                         ║
╚═══════════════════════════════════════════════════════════════╝
ASCII_ART
    echo -e "${NC}"
    
    if [ $# -eq 0 ]; then
        show_usage
        exit 1
    fi
    
    case "$1" in
        --help)
            show_usage
            ;;
        --interactive)
            # Run install.sh interactive mode
            if [ ! -f install.sh ]; then
                log_error "install.sh nu găsit"
            fi
            log_info "Lansare installer interactiv..."
            bash install.sh
            ;;
        *)
            # Direct configuration with parameters
            if [ $# -ne 6 ]; then
                log_error "Parametri lipsa. Rulează: ./configure.sh --help"
            fi
            
            generate_env "$1" "$2" "$3" "$4" "$5" "$6"
            ;;
    esac
}

main "$@"
