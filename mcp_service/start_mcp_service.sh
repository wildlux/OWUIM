#!/bin/bash
#
# MCP Bridge Service - Script di avvio Linux/macOS
#

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."

echo "============================================================"
echo "  MCP Bridge Service - Avvio"
echo "============================================================"
echo

# Colori
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Helper functions
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

check_python_module() {
    $PYTHON -c "import $1" 2>/dev/null
}

install_if_missing() {
    local module=$1
    local package=${2:-$1}
    if ! check_python_module "$module"; then
        echo -e "${YELLOW}[*] Installazione $package...${NC}"
        $PYTHON -m pip install "$package"
    fi
}

# Trova Python
if command_exists python3; then
    PYTHON="python3"
elif command_exists python; then
    PYTHON="python"
else
    echo -e "${RED}[!] Python non trovato. Installa Python 3.8+${NC}"
    exit 1
fi

echo "[*] Usando: $($PYTHON --version)"

# Attiva venv se esiste
if [ -f "venv/bin/activate" ]; then
    echo "[*] Attivazione ambiente virtuale..."
    source venv/bin/activate
fi

# Verifica dipendenze base
echo "[*] Verifica dipendenze..."
install_if_missing "fastapi" "fastapi"
install_if_missing "uvicorn" "uvicorn"
install_if_missing "requests" "requests"
install_if_missing "sse_starlette" "sse-starlette"

# Verifica MCP SDK
if ! check_python_module "mcp"; then
    echo
    echo -e "${YELLOW}[!] MCP SDK non installato.${NC}"
    echo "    Il servizio funzionerà anche senza, ma non sarà"
    echo "    possibile usare il protocollo MCP nativo."
    echo
    read -p "Installare MCP SDK? (s/n): " install_mcp
    if [[ "$install_mcp" =~ ^[Ss]$ ]]; then
        echo "[*] Installazione MCP SDK..."
        $PYTHON -m pip install mcp
    fi
fi

echo
echo "[*] Avvio MCP Bridge Service sulla porta 5558..."
echo

$PYTHON mcp_service/mcp_service.py
