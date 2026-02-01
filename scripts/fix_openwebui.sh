#!/bin/bash
###############################################################################
# Script: Fix Open WebUI (Risolve errori 404 file JS)
# Autore: Carlo
# Versione: 1.0.0
# Descrizione: Ricostruisce Open WebUI da zero con immagine pulita
###############################################################################

set -e

# Colori
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}"
cat << "EOF"
╔═══════════════════════════════════════════════════════════╗
║           🔧 Fix Open WebUI - Errori 404 JS              ║
╚═══════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

cd "$(dirname "$0")"

echo -e "${YELLOW}Questo script risolverà gli errori 404 per file JavaScript.${NC}"
echo
echo "Operazioni che verranno eseguite:"
echo "1. Ferma container Open WebUI"
echo "2. Rimuove container e immagine corrotti"
echo "3. Scarica immagine fresca da Docker Hub"
echo "4. Riavvia con immagine pulita"
echo
echo -e "${RED}⚠️  ATTENZIONE: I dati utente saranno preservati (volumi non toccati)${NC}"
echo

read -p "Procedere? (s/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Ss]$ ]]; then
    echo "Operazione annullata"
    exit 0
fi

echo
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}Step 1: Fermo container Open WebUI${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo

if docker compose version &> /dev/null; then
    docker compose stop open-webui
else
    docker-compose stop open-webui
fi

echo -e "${GREEN}✅ Container fermato${NC}"
echo

echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}Step 2: Rimuovo container e immagine corrotti${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo

# Rimuovi container
docker rm -f open-webui 2>/dev/null || true
echo "   ✓ Container rimosso"

# Rimuovi immagine corrotta
docker rmi ghcr.io/open-webui/open-webui:main 2>/dev/null || true
echo "   ✓ Immagine rimossa"

echo -e "${GREEN}✅ Pulizia completata${NC}"
echo

echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}Step 3: Pulisco cache Docker${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo

docker system prune -f > /dev/null 2>&1
echo -e "${GREEN}✅ Cache pulita${NC}"
echo

echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}Step 4: Scarico immagine fresca${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo

echo "Questo può richiedere qualche minuto..."
docker pull ghcr.io/open-webui/open-webui:main

echo -e "${GREEN}✅ Immagine scaricata${NC}"
echo

echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}Step 5: Avvio con immagine pulita${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo

if docker compose version &> /dev/null; then
    docker compose up -d open-webui
else
    docker-compose up -d open-webui
fi

echo -e "${GREEN}✅ Container avviato${NC}"
echo

echo -e "${YELLOW}⏳ Attendo che Open WebUI sia pronto (30 secondi)...${NC}"
for i in {1..30}; do
    echo -ne "   [$i/30]\r"
    sleep 1
done
echo

echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}Step 6: Verifica funzionamento${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo

HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 2>/dev/null || echo "000")

if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "302" ]; then
    echo -e "${GREEN}✅ Open WebUI risponde correttamente (HTTP $HTTP_CODE)${NC}"
else
    echo -e "${YELLOW}⚠️  Open WebUI risponde con HTTP $HTTP_CODE${NC}"
    echo "   Attendi ancora qualche secondo e riprova"
fi

echo

echo -e "${GREEN}"
cat << "EOF"
╔═══════════════════════════════════════════════════════════╗
║              ✅ Fix Completato!                          ║
╚═══════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

echo -e "${BLUE}🌐 Accedi a Open WebUI:${NC}"
echo -e "${GREEN}   http://localhost:3000${NC}"
echo
echo -e "${BLUE}📝 Verifica log (se necessario):${NC}"
if docker compose version &> /dev/null; then
    echo "   docker compose logs -f open-webui"
else
    echo "   docker-compose logs -f open-webui"
fi
echo

# Chiedi se aprire il browser
read -p "Vuoi aprire Open WebUI nel browser? (s/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Ss]$ ]]; then
    if command -v xdg-open &> /dev/null; then
        xdg-open http://localhost:3000 &> /dev/null &
    elif command -v gnome-open &> /dev/null; then
        gnome-open http://localhost:3000 &> /dev/null &
    fi
    echo "Browser aperto!"
fi

echo
echo -e "${GREEN}✨ Open WebUI è stato riparato con successo!${NC}"
exit 0
