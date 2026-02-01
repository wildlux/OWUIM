#!/bin/bash
###############################################################################
# Open WebUI + Ollama - Arresto Servizi (Linux)
###############################################################################

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colori
GREEN='\033[0;32m'
NC='\033[0m'
BOLD='\033[1m'

echo ""
echo "======================================================================"
echo "       OPEN WEBUI + OLLAMA - Arresto Servizi"
echo "======================================================================"
echo ""

# Usa docker compose (nuovo) o docker-compose (vecchio)
if docker compose version &> /dev/null; then
    COMPOSE_CMD="docker compose"
else
    COMPOSE_CMD="docker-compose"
fi

echo -e "${BOLD}[1/3] Arresto container Docker...${NC}"
$COMPOSE_CMD down &> /dev/null
echo -e "      ${GREEN}[OK]${NC}"

echo ""
echo -e "${BOLD}[2/3] Arresto Ollama...${NC}"
pkill -f "ollama serve" 2>/dev/null
echo -e "      ${GREEN}[OK]${NC}"

echo ""
echo -e "${BOLD}[3/3] Verifica...${NC}"

if ! curl -s http://localhost:3000 &> /dev/null; then
    echo -e "      ${GREEN}[OK]${NC} Open WebUI fermato"
else
    echo "      [!] Open WebUI ancora attivo"
fi

if ! curl -s http://localhost:11434/api/version &> /dev/null; then
    echo -e "      ${GREEN}[OK]${NC} Ollama fermato"
else
    echo "      [!] Ollama ancora attivo"
fi

echo ""
echo "======================================================================"
echo -e " ${GREEN}[OK] Servizi arrestati${NC}"
echo "======================================================================"
echo ""
