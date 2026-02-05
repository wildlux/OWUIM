#!/bin/bash
###############################################################################
# Open WebUI + Ollama - Avvio Completo (Linux)
###############################################################################

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colori
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'
BOLD='\033[1m'

echo ""
echo "======================================================================"
echo "       OPEN WEBUI + OLLAMA - Avvio Completo"
echo "======================================================================"
echo ""

# ======================================================================
#  [1] VERIFICA DOCKER
# ======================================================================
echo -e "${BOLD}[1/7] Verifica Docker...${NC}"

if ! docker info &> /dev/null; then
    echo -e "      ${YELLOW}[!]${NC} Docker non risponde"

    # Prova ad avviare Docker
    if systemctl is-active --quiet docker 2>/dev/null; then
        echo -e "      ${GREEN}[OK]${NC} Docker daemon attivo"
    else
        echo "      Tento di avviare Docker..."
        sudo systemctl start docker 2>/dev/null || sudo service docker start 2>/dev/null
        sleep 3

        if ! docker info &> /dev/null; then
            echo -e "      ${RED}[X] Docker non disponibile!${NC}"
            echo ""
            echo "      Installa Docker:"
            echo "        curl -fsSL https://get.docker.com | sh"
            echo "        sudo usermod -aG docker \$USER"
            exit 1
        fi
    fi
fi
echo -e "      ${GREEN}[OK]${NC} Docker attivo"

# ======================================================================
#  [2] VERIFICA/AVVIA OLLAMA
# ======================================================================
echo ""
echo -e "${BOLD}[2/7] Verifica Ollama...${NC}"

if ! curl -s http://localhost:11434/api/version &> /dev/null; then
    echo -e "      ${YELLOW}[!]${NC} Ollama non risponde"

    if ! command -v ollama &> /dev/null; then
        echo -e "      ${RED}[X] Ollama non trovato!${NC}"
        echo "      Installa con: curl -fsSL https://ollama.ai/install.sh | sh"
        exit 1
    fi

    echo "      Avvio Ollama..."
    ollama serve &> /dev/null &

    # Attendi che Ollama sia pronto
    for i in {1..15}; do
        sleep 2
        if curl -s http://localhost:11434/api/version &> /dev/null; then
            break
        fi
        echo "      Attesa Ollama... [$i/15]"
    done

    if ! curl -s http://localhost:11434/api/version &> /dev/null; then
        echo -e "      ${RED}[X] Ollama non si avvia!${NC}"
        exit 1
    fi
fi
echo -e "      ${GREEN}[OK]${NC} Ollama attivo (porta 11434)"

# ======================================================================
#  [3] AVVIA CONTAINER DOCKER
# ======================================================================
echo ""
echo -e "${BOLD}[3/7] Avvio container Open WebUI...${NC}"

# Usa docker compose (nuovo) o docker-compose (vecchio)
if docker compose version &> /dev/null; then
    COMPOSE_CMD="docker compose"
else
    COMPOSE_CMD="docker-compose"
fi

$COMPOSE_CMD up -d
if [ $? -ne 0 ]; then
    echo -e "      ${YELLOW}[!]${NC} Errore avvio container"
    echo "      Provo a scaricare l'immagine..."
    $COMPOSE_CMD pull
    $COMPOSE_CMD up -d
    if [ $? -ne 0 ]; then
        echo -e "      ${RED}[X] Impossibile avviare i container${NC}"
        exit 1
    fi
fi
echo -e "      ${GREEN}[OK]${NC} Container avviato"

# ======================================================================
#  [4] AVVIA SERVIZI AUSILIARI (MCP, TTS, Document)
# ======================================================================
echo ""
echo -e "${BOLD}[4/7] Avvio servizi ausiliari...${NC}"

# Funzione per avviare un servizio Python in background
start_service() {
    local name=$1
    local dir=$2
    local script=$3
    local port=$4
    local logfile="/tmp/${name}_service.log"

    # Controlla se già attivo
    if curl -s -o /dev/null -w "%{http_code}" "http://localhost:${port}/" 2>/dev/null | grep -q "200"; then
        echo -e "      ${GREEN}[OK]${NC} ${name} già attivo (porta ${port})"
        return 0
    fi

    # Controlla se la directory esiste
    if [ ! -d "${SCRIPT_DIR}/${dir}" ]; then
        echo -e "      ${YELLOW}[!]${NC} ${name}: directory ${dir} non trovata, salto"
        return 1
    fi

    # Avvia il servizio
    echo -n "      Avvio ${name}..."
    cd "${SCRIPT_DIR}/${dir}"
    nohup python3 "${script}" > "${logfile}" 2>&1 &
    local pid=$!
    cd "$SCRIPT_DIR"

    # Attendi che sia pronto (max 10 secondi)
    for i in {1..10}; do
        sleep 1
        if curl -s -o /dev/null -w "%{http_code}" "http://localhost:${port}/" 2>/dev/null | grep -q "200"; then
            echo -e " ${GREEN}[OK]${NC} (porta ${port}, PID ${pid})"
            return 0
        fi
    done

    echo -e " ${YELLOW}[!]${NC} timeout (controlla ${logfile})"
    return 1
}

# Avvia i servizi
start_service "MCP Bridge" "mcp_service" "mcp_service.py" 5558
start_service "TTS" "tts_service" "tts_service.py" 5556
start_service "Document" "document_service" "document_service.py" 5557

# ======================================================================
#  [5] ATTESA SERVIZIO PRONTO
# ======================================================================
echo ""
echo -e "${BOLD}[5/7] Attesa che Open WebUI sia pronto...${NC}"

for i in {1..30}; do
    sleep 2
    if curl -s http://localhost:3000 &> /dev/null; then
        echo -e "      ${GREEN}[OK]${NC} Open WebUI pronto"
        break
    fi
    echo "      Attesa... [$i/30]"
done

# ======================================================================
#  [6] APRI BROWSER
# ======================================================================
echo ""
echo -e "${BOLD}[6/7] Apertura browser...${NC}"
sleep 2

# Prova diversi browser
if command -v xdg-open &> /dev/null; then
    xdg-open http://localhost:3000 &> /dev/null &
elif command -v open &> /dev/null; then
    open http://localhost:3000
fi

# ======================================================================
#  [7] RIEPILOGO FINALE
# ======================================================================
echo ""
echo -e "${BOLD}[7/7] Verifica stato servizi...${NC}"

# Verifica tutti i servizi
check_service() {
    local name=$1
    local port=$2
    if curl -s -o /dev/null -w "%{http_code}" "http://localhost:${port}/" 2>/dev/null | grep -q "200"; then
        echo -e "      ${GREEN}✓${NC} ${name}: http://localhost:${port}"
    else
        echo -e "      ${YELLOW}✗${NC} ${name}: non attivo"
    fi
}

check_service "Open WebUI" 3000
check_service "Ollama API" 11434
check_service "MCP Bridge" 5558
check_service "TTS Service" 5556
check_service "Document Service" 5557

echo ""
echo "======================================================================"
echo -e " ${GREEN}[OK] TUTTO AVVIATO!${NC}"
echo "======================================================================"
echo ""
echo "  Servizi principali:"
echo "    Open WebUI:  http://localhost:3000"
echo "    Ollama API:  http://localhost:11434"
echo ""
echo "  Servizi ausiliari:"
echo "    MCP Bridge:  http://localhost:5558"
echo "    TTS:         http://localhost:5556"
echo "    Document:    http://localhost:5557"
echo ""
echo "  Per fermare: ./stop_all.sh"
echo "  Per la GUI:  ./run_gui.sh"
echo ""
echo "======================================================================"
