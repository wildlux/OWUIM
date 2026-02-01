#!/bin/bash
# ============================================================================
# Document Reader Service - Script di avvio per Linux/macOS
# ============================================================================
# Questo script avvia il servizio di lettura documenti.
# Installa automaticamente le dipendenze mancanti.
#
# Uso:
#   chmod +x start_document_service.sh
#   ./start_document_service.sh
# ============================================================================

# Vai nella cartella dello script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colori per output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║         DOCUMENT READER SERVICE - Avvio                      ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# ----------------------------------------------------------------------------
# Funzione per verificare se un comando esiste
# ----------------------------------------------------------------------------
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# ----------------------------------------------------------------------------
# Verifica Python
# ----------------------------------------------------------------------------
echo "[*] Verifica Python..."

if command_exists python3; then
    PYTHON="python3"
elif command_exists python; then
    PYTHON="python"
else
    echo -e "${RED}[X] Python non trovato!${NC}"
    echo "    Installa Python 3.8+ da: https://www.python.org/downloads/"
    exit 1
fi

PYTHON_VERSION=$($PYTHON --version 2>&1 | cut -d' ' -f2)
echo -e "${GREEN}[OK] Python $PYTHON_VERSION${NC}"

# ----------------------------------------------------------------------------
# Verifica pip
# ----------------------------------------------------------------------------
if ! $PYTHON -m pip --version >/dev/null 2>&1; then
    echo -e "${RED}[X] pip non trovato!${NC}"
    echo "    Installa con: $PYTHON -m ensurepip --upgrade"
    exit 1
fi

# ----------------------------------------------------------------------------
# Installa dipendenze mancanti
# ----------------------------------------------------------------------------
echo ""
echo "[*] Verifica dipendenze..."

install_if_missing() {
    local module=$1
    local package=$2

    if ! $PYTHON -c "import $module" 2>/dev/null; then
        echo -e "${YELLOW}[!] Installazione $package...${NC}"
        $PYTHON -m pip install --quiet "$package"
    fi
}

# Dipendenze obbligatorie
install_if_missing "fastapi" "fastapi"
install_if_missing "uvicorn" "uvicorn"
install_if_missing "multipart" "python-multipart"

# Dipendenze per formati documenti
install_if_missing "pypdf" "pypdf"
install_if_missing "docx" "python-docx"
install_if_missing "openpyxl" "openpyxl"
install_if_missing "pptx" "python-pptx"
install_if_missing "PIL" "Pillow"
install_if_missing "markdown" "markdown"
install_if_missing "bs4" "beautifulsoup4"
install_if_missing "yaml" "PyYAML"
install_if_missing "ebooklib" "ebooklib"
install_if_missing "lxml" "lxml"

echo -e "${GREEN}[OK] Dipendenze verificate${NC}"

# ----------------------------------------------------------------------------
# Verifica programmi esterni (opzionali)
# ----------------------------------------------------------------------------
echo ""
echo "[*] Programmi esterni (opzionali):"

if command_exists soffice || command_exists libreoffice; then
    echo -e "  ${GREEN}[OK] LibreOffice${NC}"
else
    echo -e "  ${YELLOW}[  ] LibreOffice (installa con: sudo apt install libreoffice)${NC}"
fi

if command_exists gimp; then
    echo -e "  ${GREEN}[OK] GIMP${NC}"
else
    echo -e "  ${YELLOW}[  ] GIMP (installa con: sudo apt install gimp)${NC}"
fi

if command_exists convert || command_exists magick; then
    echo -e "  ${GREEN}[OK] ImageMagick${NC}"
else
    echo -e "  ${YELLOW}[  ] ImageMagick (installa con: sudo apt install imagemagick)${NC}"
fi

if command_exists ebook-convert; then
    echo -e "  ${GREEN}[OK] Calibre${NC}"
else
    echo -e "  ${YELLOW}[  ] Calibre (installa con: sudo apt install calibre)${NC}"
fi

# ----------------------------------------------------------------------------
# Avvia il servizio
# ----------------------------------------------------------------------------
echo ""
echo "[*] Avvio servizio su http://localhost:5557"
echo "[*] Documentazione: http://localhost:5557/docs"
echo "[*] Premi Ctrl+C per fermare"
echo ""

$PYTHON document_service.py
