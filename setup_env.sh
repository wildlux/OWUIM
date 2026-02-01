#!/bin/bash
# Setup Ambiente Python - Open WebUI Manager

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo ""
echo "======================================================================"
echo "       SETUP AMBIENTE PYTHON - Open WebUI Manager"
echo "======================================================================"
echo ""

# Verifica Python
echo "[1/4] Verifica Python..."
if ! command -v python3 &> /dev/null; then
    echo "[X] Python3 non trovato!"
    echo "    Installa con: sudo apt install python3 python3-venv python3-pip"
    exit 1
fi
echo "[OK] Python3 trovato: $(python3 --version)"

# Verifica python3-venv
if ! python3 -m venv --help &> /dev/null; then
    echo "[X] python3-venv non installato!"
    echo "    Installa con: sudo apt install python3-venv"
    exit 1
fi

# Crea ambiente virtuale
echo ""
echo "[2/4] Creazione ambiente virtuale..."
if [ -d "venv" ]; then
    echo "[!] Ambiente virtuale esistente trovato"
    read -p "Vuoi ricrearlo? [s/N]: " choice
    if [[ "$choice" =~ ^[sS]$ ]]; then
        rm -rf venv
        python3 -m venv venv
        echo "[OK] Ambiente virtuale ricreato"
    else
        echo "[OK] Ambiente virtuale esistente mantenuto"
    fi
else
    python3 -m venv venv
    echo "[OK] Ambiente virtuale creato"
fi

# Attiva venv e aggiorna pip
echo ""
echo "[3/4] Aggiornamento pip..."
source venv/bin/activate
pip install --upgrade pip > /dev/null 2>&1
echo "[OK] pip aggiornato"

# Installa dipendenze
echo ""
echo "[4/4] Installazione dipendenze..."
pip install -r requirements.txt

echo ""
echo "======================================================================"
echo " [OK] SETUP COMPLETATO!"
echo "======================================================================"
echo ""
echo " Per avviare la GUI:"
echo "   ./run_gui.sh          (GUI completa PyQt5)"
echo "   ./run_gui_lite.sh     (GUI leggera Tkinter)"
echo ""
echo " Per attivare manualmente l'ambiente:"
echo "   source venv/bin/activate"
echo ""
echo "======================================================================"
