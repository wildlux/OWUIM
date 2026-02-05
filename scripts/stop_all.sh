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

echo -e "${BOLD}[1/4] Arresto container Docker...${NC}"
$COMPOSE_CMD down &> /dev/null
echo -e "      ${GREEN}[OK]${NC}"

echo ""
echo -e "${BOLD}[2/4] Arresto Ollama...${NC}"
pkill -f "ollama serve" 2>/dev/null
echo -e "      ${GREEN}[OK]${NC}"

echo ""
echo -e "${BOLD}[3/4] Arresto servizi ausiliari...${NC}"
# MCP Bridge
pkill -f "mcp_service.py" 2>/dev/null && echo -e "      ${GREEN}[OK]${NC} MCP Bridge fermato" || echo "      MCP Bridge non attivo"
# TTS Service
pkill -f "tts_service.py" 2>/dev/null && echo -e "      ${GREEN}[OK]${NC} TTS Service fermato" || echo "      TTS Service non attivo"
# Document Service
pkill -f "document_service.py" 2>/dev/null && echo -e "      ${GREEN}[OK]${NC} Document Service fermato" || echo "      Document Service non attivo"

echo ""
echo -e "${BOLD}[4/4] Verifica...${NC}"

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

# Verifica servizi ausiliari
for port in 5558 5556 5557; do
    if ! curl -s -o /dev/null "http://localhost:${port}/" 2>/dev/null; then
        echo -e "      ${GREEN}[OK]${NC} Porta ${port} libera"
    fi
done

echo ""
echo "======================================================================"
echo -e " ${GREEN}[OK] Servizi arrestati${NC}"
echo "======================================================================"
echo ""
