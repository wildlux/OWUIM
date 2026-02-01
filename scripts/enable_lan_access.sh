#!/bin/bash
###############################################################################
# Script: Abilita Accesso LAN a Open WebUI
# Autore: Carlo
# Versione: 1.0.0
# Descrizione: Configura Open WebUI per l'accesso da dispositivi sulla rete locale
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
║         🌐 Abilita Accesso LAN a Open WebUI              ║
╚═══════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

# Verifica esecuzione come utente normale
if [ "$EUID" -eq 0 ]; then
    echo -e "${RED}❌ Non eseguire questo script come root!${NC}"
    echo "Eseguilo come utente normale. Lo script chiederà sudo quando necessario."
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

# Backup del file originale
echo -e "${YELLOW}💾 Creazione backup: $(basename $BACKUP_FILE)${NC}"
cp "$COMPOSE_FILE" "$BACKUP_FILE"
echo -e "${GREEN}✅ Backup creato${NC}"
echo

# Trova IP locale
echo -e "${YELLOW}🔍 Rilevamento indirizzo IP locale...${NC}"
LOCAL_IP=$(hostname -I | awk '{print $1}')

if [ -z "$LOCAL_IP" ]; then
    echo -e "${RED}❌ Impossibile rilevare IP locale${NC}"
    exit 1
fi

echo -e "${GREEN}✅ IP locale rilevato: $LOCAL_IP${NC}"
echo

# Modifica docker-compose.yml
echo -e "${YELLOW}🔧 Modifica configurazione docker-compose.yml...${NC}"

# Sostituisci 127.0.0.1 con 0.0.0.0 per le porte
sed -i 's/127\.0\.0\.1:3000/0.0.0.0:3000/g' "$COMPOSE_FILE"
sed -i 's/127\.0\.0\.1:11434/0.0.0.0:11434/g' "$COMPOSE_FILE"

# Verifica modifiche
if grep -q "0.0.0.0:3000" "$COMPOSE_FILE" && grep -q "0.0.0.0:11434" "$COMPOSE_FILE"; then
    echo -e "${GREEN}✅ Configurazione modificata correttamente${NC}"
else
    echo -e "${RED}❌ Errore nella modifica del file${NC}"
    echo "Ripristino backup..."
    cp "$BACKUP_FILE" "$COMPOSE_FILE"
    exit 1
fi
echo

# Configura firewall
echo -e "${YELLOW}🔥 Configurazione firewall...${NC}"
echo "Potrebbero essere richieste credenziali sudo"
echo

# Rileva sistema firewall
FIREWALL_CONFIGURED=false

# Prova firewalld
if command -v firewall-cmd &> /dev/null; then
    echo "Rilevato: firewalld"
    sudo firewall-cmd --add-port=3000/tcp --permanent 2>/dev/null && \
    sudo firewall-cmd --add-port=11434/tcp --permanent 2>/dev/null && \
    sudo firewall-cmd --reload 2>/dev/null && \
    FIREWALL_CONFIGURED=true && \
    echo -e "${GREEN}✅ Firewalld configurato${NC}"
fi

# Prova ufw
if command -v ufw &> /dev/null && [ "$FIREWALL_CONFIGURED" = false ]; then
    echo "Rilevato: ufw"
    sudo ufw allow 3000/tcp 2>/dev/null && \
    sudo ufw allow 11434/tcp 2>/dev/null && \
    FIREWALL_CONFIGURED=true && \
    echo -e "${GREEN}✅ UFW configurato${NC}"
fi

# Prova iptables
if command -v iptables &> /dev/null && [ "$FIREWALL_CONFIGURED" = false ]; then
    echo "Rilevato: iptables"
    sudo iptables -C INPUT -p tcp --dport 3000 -j ACCEPT 2>/dev/null || \
        sudo iptables -A INPUT -p tcp --dport 3000 -j ACCEPT
    sudo iptables -C INPUT -p tcp --dport 11434 -j ACCEPT 2>/dev/null || \
        sudo iptables -A INPUT -p tcp --dport 11434 -j ACCEPT

    # Salva regole (Debian/Ubuntu)
    if [ -d "/etc/iptables" ]; then
        sudo iptables-save | sudo tee /etc/iptables/rules.v4 > /dev/null
    fi

    FIREWALL_CONFIGURED=true
    echo -e "${GREEN}✅ IPTables configurato${NC}"
fi

if [ "$FIREWALL_CONFIGURED" = false ]; then
    echo -e "${YELLOW}⚠️  Nessun firewall rilevato o già configurato${NC}"
    echo "Se hai problemi di connessione, configura manualmente il firewall."
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

echo "Avvio servizi in modalità LAN..."
if docker-compose up -d; then
    echo -e "${GREEN}✅ Servizi avviati${NC}"
else
    echo -e "${RED}❌ Errore durante l'avvio dei servizi${NC}"
    echo "Ripristino configurazione originale..."
    cp "$BACKUP_FILE" "$COMPOSE_FILE"
    docker-compose up -d
    exit 1
fi
echo

# Attendi che i servizi siano pronti
echo -e "${YELLOW}⏳ Attendo che i servizi siano pronti...${NC}"
sleep 5

# Verifica porte aperte
echo -e "${YELLOW}🔍 Verifica porte...${NC}"
if sudo ss -tulpn | grep -E ":3000|:11434" | grep "0.0.0.0" > /dev/null; then
    echo -e "${GREEN}✅ Porte aperte correttamente su 0.0.0.0${NC}"
else
    echo -e "${YELLOW}⚠️  Verifica manualmente con: sudo ss -tulpn | grep -E ':3000|:11434'${NC}"
fi
echo

# Test connettività locale
echo -e "${YELLOW}🧪 Test connettività locale...${NC}"
if curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 | grep -q "200\|301\|302"; then
    echo -e "${GREEN}✅ Open WebUI risponde correttamente${NC}"
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

echo -e "${BLUE}📱 Accedi da dispositivi mobili:${NC}"
echo -e "${GREEN}   http://$LOCAL_IP:3000${NC}"
echo
echo -e "${BLUE}🔗 Accedi da questo PC:${NC}"
echo -e "${GREEN}   http://localhost:3000${NC}"
echo -e "${GREEN}   http://$LOCAL_IP:3000${NC}"
echo
echo -e "${BLUE}📋 Istruzioni per dispositivi mobili:${NC}"
echo "   1. Connetti il dispositivo alla stessa WiFi"
echo "   2. Apri il browser"
echo "   3. Vai a: http://$LOCAL_IP:3000"
echo "   4. Effettua il login con le tue credenziali"
echo
echo -e "${YELLOW}🔒 Nota sulla sicurezza:${NC}"
echo "   - Usa solo su reti domestiche private"
echo "   - Non esporre direttamente su Internet"
echo "   - Usa password forti per gli account"
echo
echo -e "${BLUE}📚 Documentazione completa:${NC}"
echo "   $PROJECT_DIR/docs/LAN_ACCESS.md"
echo
echo -e "${YELLOW}💾 Backup originale salvato in:${NC}"
echo "   $(basename $BACKUP_FILE)"
echo
echo -e "${BLUE}🔄 Per disabilitare l'accesso LAN:${NC}"
echo "   ./disable_lan_access.sh"
echo

# Chiedi se aprire la documentazione
read -p "Vuoi aprire la documentazione completa? (s/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Ss]$ ]]; then
    if command -v xdg-open &> /dev/null; then
        xdg-open "$PROJECT_DIR/docs/LAN_ACCESS.md" 2>/dev/null || cat "$PROJECT_DIR/docs/LAN_ACCESS.md"
    else
        less "$PROJECT_DIR/docs/LAN_ACCESS.md"
    fi
fi

echo -e "${GREEN}✨ Configurazione completata con successo!${NC}"
exit 0
