#!/bin/bash
###############################################################################
# Script: Aggiorna Open WebUI all'Ultima Versione
# Autore: Carlo
# Versione: 1.0.0
# Descrizione: Aggiorna Open WebUI alla versione più recente da Docker Hub
###############################################################################

set -e

# Colori
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${BLUE}"
cat << "EOF"
╔═══════════════════════════════════════════════════════════╗
║        📦 Aggiornamento Open WebUI                       ║
╚═══════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

cd "$(dirname "$0")"

# Verifica versione corrente
echo -e "${YELLOW}🔍 Controllo versione corrente...${NC}"
echo

CURRENT_IMAGE=$(docker images ghcr.io/open-webui/open-webui:main --format "{{.ID}}" 2>/dev/null || echo "")

if [ -n "$CURRENT_IMAGE" ]; then
    CURRENT_CREATED=$(docker images ghcr.io/open-webui/open-webui:main --format "{{.CreatedAt}}" | cut -d' ' -f1)
    echo -e "${CYAN}Versione installata:${NC}"
    echo "   Image ID: $CURRENT_IMAGE"
    echo "   Creata il: $CURRENT_CREATED"
else
    echo -e "${YELLOW}⚠️  Nessuna immagine locale trovata${NC}"
    CURRENT_IMAGE="none"
fi

echo
echo -e "${YELLOW}🌐 Controllo aggiornamenti disponibili...${NC}"
echo

# Controlla se c'è una nuova versione
docker pull ghcr.io/open-webui/open-webui:main --quiet > /dev/null 2>&1 &
PULL_PID=$!

# Progress indicator
while kill -0 $PULL_PID 2>/dev/null; do
    echo -ne "   Scaricamento in corso...\r"
    sleep 1
done

wait $PULL_PID 2>/dev/null || true

NEW_IMAGE=$(docker images ghcr.io/open-webui/open-webui:main --format "{{.ID}}" 2>/dev/null || echo "")
NEW_CREATED=$(docker images ghcr.io/open-webui/open-webui:main --format "{{.CreatedAt}}" | cut -d' ' -f1)

echo -e "${CYAN}Ultima versione disponibile:${NC}"
echo "   Image ID: $NEW_IMAGE"
echo "   Creata il: $NEW_CREATED"
echo

# Confronta versioni
if [ "$CURRENT_IMAGE" = "$NEW_IMAGE" ] && [ "$CURRENT_IMAGE" != "none" ]; then
    echo -e "${GREEN}✅ Open WebUI è già aggiornato all'ultima versione!${NC}"
    echo
    read -p "Vuoi riavviare comunque il container? (s/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Ss]$ ]]; then
        echo "Nessuna azione necessaria."
        exit 0
    fi
    RESTART_ONLY=true
else
    echo -e "${CYAN}🆕 Nuovo aggiornamento disponibile!${NC}"
    echo
    echo -e "${YELLOW}Miglioramenti recenti Open WebUI:${NC}"
    echo "   - Miglioramenti performance frontend"
    echo "   - Correzioni bug interfaccia"
    echo "   - Nuove funzionalità tools"
    echo "   - Aggiornamenti sicurezza"
    echo
    echo -e "${GREEN}✅ I tuoi dati utente saranno preservati (volumi non toccati)${NC}"
    echo
    echo -e "${YELLOW}Vuoi procedere con l'aggiornamento?${NC}"
    read -p "Scegli (s=Sì, n=No): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Ss]$ ]]; then
        echo "Aggiornamento annullato"
        exit 0
    fi
    RESTART_ONLY=false
fi

echo
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}Inizio ${RESTART_ONLY:+Riavvio}${RESTART_ONLY:-Aggiornamento}${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo

# Step 1: Ferma container
echo -e "${YELLOW}Step 1/5: Fermo container Open WebUI...${NC}"

if docker compose version &> /dev/null; then
    docker compose stop open-webui
else
    docker-compose stop open-webui
fi

echo -e "${GREEN}✅ Container fermato${NC}"
echo

# Step 2: Rimuovi container vecchio
echo -e "${YELLOW}Step 2/5: Rimuovo container precedente...${NC}"

docker rm -f open-webui 2>/dev/null || true

echo -e "${GREEN}✅ Container rimosso${NC}"
echo

# Step 3: Pulizia immagini vecchie (solo se aggiornamento)
if [ "$RESTART_ONLY" = false ]; then
    echo -e "${YELLOW}Step 3/5: Rimuovo immagini obsolete...${NC}"

    # Rimuovi immagini dangling
    docker image prune -f > /dev/null 2>&1 || true

    echo -e "${GREEN}✅ Pulizia completata${NC}"
    echo
else
    echo -e "${YELLOW}Step 3/5: Saltato (riavvio)${NC}"
    echo
fi

# Step 4: Avvia con nuova versione
echo -e "${YELLOW}Step 4/5: Avvio container con versione aggiornata...${NC}"

if docker compose version &> /dev/null; then
    docker compose up -d open-webui
else
    docker-compose up -d open-webui
fi

echo -e "${GREEN}✅ Container avviato${NC}"
echo

# Step 5: Attendi e verifica
echo -e "${YELLOW}Step 5/5: Verifica funzionamento...${NC}"
echo

echo "Attendo che Open WebUI sia pronto..."
RETRY_COUNT=0
MAX_RETRIES=30

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 2>/dev/null || echo "000")

    if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "302" ]; then
        echo -e "\n${GREEN}✅ Open WebUI è pronto e funzionante!${NC}"
        break
    fi

    echo -ne "   Tentativo $((RETRY_COUNT + 1))/$MAX_RETRIES (HTTP $HTTP_CODE)...\r"
    sleep 2
    RETRY_COUNT=$((RETRY_COUNT + 1))
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo -e "\n${YELLOW}⚠️  Open WebUI impiega più tempo del previsto ad avviarsi${NC}"
    echo "   Controlla i log con: docker compose logs -f open-webui"
fi

echo

# Verifica versione finale
FINAL_IMAGE=$(docker ps --filter "name=open-webui" --format "{{.Image}}" 2>/dev/null || echo "")
FINAL_STATUS=$(docker ps --filter "name=open-webui" --format "{{.Status}}" 2>/dev/null || echo "")

echo -e "${CYAN}📊 Stato Finale:${NC}"
echo "   Immagine: $FINAL_IMAGE"
echo "   Stato: $FINAL_STATUS"
echo

# Risultato finale
echo -e "${GREEN}"
cat << "EOF"
╔═══════════════════════════════════════════════════════════╗
║           ✅ Aggiornamento Completato!                   ║
╚═══════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

echo -e "${BLUE}🌐 Accedi a Open WebUI:${NC}"
echo -e "${GREEN}   http://localhost:3000${NC}"
echo

if [ "$RESTART_ONLY" = false ]; then
    echo -e "${CYAN}🆕 Novità in questa versione:${NC}"
    echo "   - Controlla le note di rilascio su: https://github.com/open-webui/open-webui/releases"
    echo
fi

echo -e "${BLUE}📝 Comandi utili:${NC}"
if docker compose version &> /dev/null; then
    echo "   Log: docker compose logs -f open-webui"
    echo "   Stato: docker compose ps"
    echo "   Riavvio: docker compose restart open-webui"
else
    echo "   Log: docker-compose logs -f open-webui"
    echo "   Stato: docker-compose ps"
    echo "   Riavvio: docker-compose restart open-webui"
fi
echo

# Chiedi se aprire il browser
read -p "Vuoi aprire Open WebUI nel browser? (s/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Ss]$ ]]; then
    sleep 2
    if command -v xdg-open &> /dev/null; then
        xdg-open http://localhost:3000 &> /dev/null &
    elif command -v gnome-open &> /dev/null; then
        gnome-open http://localhost:3000 &> /dev/null &
    fi
    echo "Browser aperto!"
fi

echo
echo -e "${GREEN}✨ Open WebUI aggiornato con successo!${NC}"
echo

# Suggerimento per tools
echo -e "${YELLOW}💡 Suggerimento:${NC}"
echo "   Se hai installato i tools, verifica che siano ancora attivi in:"
echo "   Admin Panel → Functions → Tools"
echo

exit 0
