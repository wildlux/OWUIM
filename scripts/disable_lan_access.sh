#!/bin/bash
###############################################################################
# Script: Disabilita Accesso LAN a Open WebUI
# Autore: Carlo
# Versione: 1.0.0
# Descrizione: Ripristina Open WebUI a modalità localhost-only (127.0.0.1)
###############################################################################

set -e  # Exit on error

# Colori per output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Banner
echo -e "${BLUE}"
cat << "EOF"
╔═══════════════════════════════════════════════════════════╗
║        🔒 Disabilita Accesso LAN a Open WebUI            ║
╚═══════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

# Verifica esecuzione come utente normale
if [ "$EUID" -eq 0 ]; then
    echo -e "${RED}❌ Non eseguire questo script come root!${NC}"
    exit 1
fi

# Directory del progetto
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPOSE_FILE="$PROJECT_DIR/docker-compose.yml"
BACKUP_FILE="$COMPOSE_FILE.backup.$(date +%Y%m%d_%H%M%S)"

echo -e "${YELLOW}📁 Directory progetto: $PROJECT_DIR${NC}"
echo

# Verifica esistenza docker-compose.yml
if [ ! -f "$COMPOSE_FILE" ]; then
    echo -e "${RED}❌ File docker-compose.yml non trovato in: $PROJECT_DIR${NC}"
    exit 1
fi

echo -e "${GREEN}✅ File docker-compose.yml trovato${NC}"

# Backup del file corrente
echo -e "${YELLOW}💾 Creazione backup: $(basename $BACKUP_FILE)${NC}"
cp "$COMPOSE_FILE" "$BACKUP_FILE"
echo -e "${GREEN}✅ Backup creato${NC}"
echo

# Modifica docker-compose.yml
echo -e "${YELLOW}🔧 Ripristino configurazione localhost-only...${NC}"

# Sostituisci 0.0.0.0 con 127.0.0.1 per le porte
sed -i 's/0\.0\.0\.0:3000/127.0.0.1:3000/g' "$COMPOSE_FILE"
sed -i 's/0\.0\.0\.0:11434/127.0.0.1:11434/g' "$COMPOSE_FILE"

# Verifica modifiche
if grep -q "127.0.0.1:3000" "$COMPOSE_FILE" && grep -q "127.0.0.1:11434" "$COMPOSE_FILE"; then
    echo -e "${GREEN}✅ Configurazione ripristinata a localhost-only${NC}"
else
    echo -e "${RED}❌ Errore nella modifica del file${NC}"
    echo "Ripristino backup..."
    cp "$BACKUP_FILE" "$COMPOSE_FILE"
    exit 1
fi
echo

# Opzionale: rimuovi regole firewall
echo -e "${YELLOW}🔥 Vuoi rimuovere le regole firewall per le porte 3000 e 11434?${NC}"
read -p "Questo aumenterà la sicurezza ma impedirà l'accesso LAN (s/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Ss]$ ]]; then
    echo "Rimozione regole firewall..."
    echo "Potrebbero essere richieste credenziali sudo"
    echo

    # Prova firewalld
    if command -v firewall-cmd &> /dev/null; then
        sudo firewall-cmd --remove-port=3000/tcp --permanent 2>/dev/null
        sudo firewall-cmd --remove-port=11434/tcp --permanent 2>/dev/null
        sudo firewall-cmd --reload 2>/dev/null
        echo -e "${GREEN}✅ Regole firewalld rimosse${NC}"
    fi

    # Prova ufw
    if command -v ufw &> /dev/null; then
        sudo ufw delete allow 3000/tcp 2>/dev/null
        sudo ufw delete allow 11434/tcp 2>/dev/null
        echo -e "${GREEN}✅ Regole UFW rimosse${NC}"
    fi

    # Prova iptables
    if command -v iptables &> /dev/null; then
        sudo iptables -D INPUT -p tcp --dport 3000 -j ACCEPT 2>/dev/null || true
        sudo iptables -D INPUT -p tcp --dport 11434 -j ACCEPT 2>/dev/null || true

        # Salva regole
        if [ -d "/etc/iptables" ]; then
            sudo iptables-save | sudo tee /etc/iptables/rules.v4 > /dev/null
        fi
        echo -e "${GREEN}✅ Regole IPTables rimosse${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Regole firewall mantenute${NC}"
    echo "Le porte rimarranno aperte ma non saranno accessibili (binding 127.0.0.1)"
fi
echo

# Riavvia servizi Docker
echo -e "${YELLOW}🔄 Riavvio servizi Docker...${NC}"
cd "$PROJECT_DIR"

if docker-compose down; then
    echo -e "${GREEN}✅ Servizi fermati${NC}"
else
    echo -e "${RED}❌ Errore durante l'arresto dei servizi${NC}"
    exit 1
fi

echo "Avvio servizi in modalità localhost-only..."
if docker-compose up -d; then
    echo -e "${GREEN}✅ Servizi avviati${NC}"
else
    echo -e "${RED}❌ Errore durante l'avvio dei servizi${NC}"
    echo "Ripristino configurazione precedente..."
    cp "$BACKUP_FILE" "$COMPOSE_FILE"
    docker-compose up -d
    exit 1
fi
echo

# Attendi che i servizi siano pronti
echo -e "${YELLOW}⏳ Attendo che i servizi siano pronti...${NC}"
sleep 5

# Verifica porte
echo -e "${YELLOW}🔍 Verifica porte...${NC}"
if sudo ss -tulpn | grep -E ":3000|:11434" | grep "127.0.0.1" > /dev/null; then
    echo -e "${GREEN}✅ Porte configurate correttamente su 127.0.0.1 (localhost-only)${NC}"
else
    echo -e "${YELLOW}⚠️  Verifica manualmente con: sudo ss -tulpn | grep -E ':3000|:11434'${NC}"
fi
echo

# Test connettività locale
echo -e "${YELLOW}🧪 Test connettività locale...${NC}"
if curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 | grep -q "200\|301\|302"; then
    echo -e "${GREEN}✅ Open WebUI risponde correttamente su localhost${NC}"
else
    echo -e "${YELLOW}⚠️  Open WebUI potrebbe essere ancora in fase di avvio${NC}"
fi
echo

# Informazioni finali
echo -e "${GREEN}"
cat << "EOF"
╔═══════════════════════════════════════════════════════════╗
║              ✅ Configurazione Completata!                ║
╚═══════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

echo -e "${BLUE}🔒 Modalità: Localhost-Only${NC}"
echo -e "${GREEN}   http://localhost:3000${NC}"
echo
echo -e "${YELLOW}⚠️  Accesso LAN disabilitato${NC}"
echo "   I dispositivi mobili non potranno più connettersi"
echo
echo -e "${BLUE}🔓 Per riabilitare l'accesso LAN:${NC}"
echo "   ./enable_lan_access.sh"
echo
echo -e "${YELLOW}💾 Backup configurazione precedente salvato in:${NC}"
echo "   $(basename $BACKUP_FILE)"
echo

echo -e "${GREEN}✨ Open WebUI è ora accessibile solo da questo PC!${NC}"
exit 0
