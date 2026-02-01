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
echo -e "${BOLD}[1/5] Verifica Docker...${NC}"

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
echo -e "${BOLD}[2/5] Verifica Ollama...${NC}"

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
echo -e "${BOLD}[3/5] Avvio container Open WebUI...${NC}"

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
#  [4] ATTESA SERVIZIO PRONTO
# ======================================================================
echo ""
echo -e "${BOLD}[4/5] Attesa che Open WebUI sia pronto...${NC}"

for i in {1..30}; do
    sleep 2
    if curl -s http://localhost:3000 &> /dev/null; then
        echo -e "      ${GREEN}[OK]${NC} Open WebUI pronto"
        break
    fi
    echo "      Attesa... [$i/30]"
done

# ======================================================================
#  [5] APRI BROWSER
# ======================================================================
echo ""
echo -e "${BOLD}[5/5] Apertura browser...${NC}"
sleep 2

# Prova diversi browser
if command -v xdg-open &> /dev/null; then
    xdg-open http://localhost:3000 &> /dev/null &
elif command -v open &> /dev/null; then
    open http://localhost:3000
fi

echo ""
echo "======================================================================"
echo -e " ${GREEN}[OK] TUTTO AVVIATO!${NC}"
echo "======================================================================"
echo ""
echo "  Open WebUI:  http://localhost:3000"
echo "  Ollama API:  http://localhost:11434"
echo ""
echo "  Per fermare: ./stop_all.sh"
echo "  Per la GUI:  ./run_gui.sh"
echo ""
echo "======================================================================"
