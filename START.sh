#!/bin/bash

################################################################################
# START.sh - Entry Point
#
# Rulează aceasta pentru prima dată
# Ghidează prin opțiuni de setup
################################################################################

set -euo pipefail

readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly CYAN='\033[0;36m'
readonly NC='\033[0m'

clear

cat << 'ASCII_ART'
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║    GLPI-LibreNMS + Nginx Proxy Manager                        ║
║    Docker Edition v1.0                                        ║
║                                                               ║
║    IT Asset Management + Network Monitoring +                 ║
║    Automatic Service Publishing                              ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
ASCII_ART

cat << EOF

$(echo -e "${BLUE}================== WELCOME! ==================${NC}")

Ai primit un stack complet Docker cu:

  ✅ GLPI (IT Asset Management)
  ✅ LibreNMS (Network Monitoring)
  ✅ Nginx Proxy Manager (Reverse Proxy)
  ✅ Auto-Discovery Service (Publicare automată)
  ✅ MySQL + Redis

$(echo -e "${BLUE}================= QUICK START =================   ${NC}")

Alege o opțiune:

  $(echo -e "${CYAN}1. Setup Interactiv (RECOMMENDED)${NC}")
     - Cere domain, hostname-uri, credentiale
     - Best for: Première dată, vrei setup corect
     - Timp: ~2-3 minute
     
     ${GREEN}./install.sh${NC}

  $(echo -e "${CYAN}2. Setup cu Parametri Direct${NC}")
     - Rapid, non-interactiv
     - Best for: Scripting, CI/CD
     - Exemplu: ./configure.sh local glpi librenms npm admin@ernu.md Pass123!
     
     ${GREEN}./configure.sh${NC}

  $(echo -e "${CYAN}3. Setup Manual${NC}")
     - Full control, editare .env manual
     - Best for: Production, custom config
     
     ${GREEN}cp .env.example .env && nano .env && docker-compose up -d${NC}

  $(echo -e "${CYAN}4. Citire Documentație${NC}")
     - README.md - Overview + quick start
     - CONFIGURATION.md - Opțiuni detaliate
     - 00-SUMMARY.md - Rezumat complet

  $(echo -e "${CYAN}0. Exit${NC}")

EOF

read -p "$(echo -e "${CYAN}Selectează (1-4 sau 0):${NC} ")" choice

case $choice in
    1)
        clear
        echo -e "${BLUE}======= SETUP INTERACTIV =======${NC}"
        echo ""
        echo "Lansare installer interactiv..."
        echo "(Vei fi ghidat prin toți pașii)"
        echo ""
        sleep 2
        
        if [ ! -f install.sh ]; then
            echo -e "${RED}[ERROR]${NC} install.sh nu găsit"
            exit 1
        fi
        
        chmod +x install.sh
        ./install.sh
        ;;
    
    2)
        clear
        echo -e "${BLUE}======= SETUP CU PARAMETRI =======${NC}"
        echo ""
        echo "Exemplu sintaxă:"
        echo ""
        echo "  ./configure.sh <DOMAIN> <GLPI> <LIBRENMS> <NPM> <EMAIL> <PASSWORD>"
        echo ""
        echo "Exemplu:"
        echo "  ./configure.sh local glpi librenms npm admin@ernu.md MyPass123!"
        echo ""
        
        if [ ! -f configure.sh ]; then
            echo -e "${RED}[ERROR]${NC} configure.sh nu găsit"
            exit 1
        fi
        
        chmod +x configure.sh
        ;;
    
    3)
        clear
        echo -e "${BLUE}======= SETUP MANUAL =======${NC}"
        echo ""
        echo "Pași:"
        echo "  1. Copy .env.example → .env"
        echo "  2. Edit .env cu valorile tale"
        echo "  3. Start: docker-compose up -d"
        echo ""
        echo "Comenzi:"
        echo ""
        echo "  $(echo -e "${GREEN}cp .env.example .env${NC}")"
        echo "  $(echo -e "${GREEN}nano .env${NC}") (sau VSCode, etc)"
        echo "  $(echo -e "${GREEN}docker-compose up -d${NC}")"
        echo ""
        ;;
    
    4)
        echo ""
        echo -e "${BLUE}Deschide cu favoritul text editor:${NC}"
        echo ""
        echo "  - 00-SUMMARY.md (Overview complet)"
        echo "  - README.md (Documentation completă)"
        echo "  - CONFIGURATION.md (Setup options detaliat)"
        echo ""
        echo "Sau citește din terminal:"
        echo ""
        echo "  $(echo -e "${GREEN}less README.md${NC}")"
        echo "  $(echo -e "${GREEN}less CONFIGURATION.md${NC}")"
        echo ""
        ;;
    
    0)
        echo "Goodbye! 👋"
        exit 0
        ;;
    
    *)
        echo -e "${RED}Invalid option${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}════════════════════════════════════════${NC}"
echo -e "${GREEN}  NEXT STEPS:${NC}"
echo -e "${GREEN}════════════════════════════════════════${NC}"
echo ""
echo "1. Configurează DNS local (.local domains)"
echo "   - Instrucțiuni vor apărea după installer"
echo ""
echo "2. Accesează serviciile:"
echo "   - http://npm.local:81/  (Admin UI)"
echo "   - http://glpi.local/    (GLPI)"
echo "   - http://librenms.local/ (LibreNMS)"
echo ""
echo "3. Schimbă parolele default"
echo "   - NPM: admin@ernu.md / Npm@ernu2025!"
echo "   - GLPI: admin / admin"
echo ""
echo "4. Testează auto-discovery"
echo "   - Adaugă container cu npm.expose=true"
echo "   - Observă logs: docker-compose logs -f npm-auto-discovery"
echo ""
echo -e "${GREEN}════════════════════════════════════════${NC}"
echo ""
echo -e "${CYAN}Ready to deploy! 🚀${NC}"
echo ""
