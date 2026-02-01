#!/bin/bash
# Image Analysis Service - Avvio

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PARENT_DIR="$(dirname "$SCRIPT_DIR")"

echo ""
echo "======================================================================"
echo "         IMAGE ANALYSIS SERVICE per Open WebUI"
echo "======================================================================"
echo ""
echo "  Cartella: $SCRIPT_DIR"
echo ""

# Vai alla cartella del servizio
cd "$SCRIPT_DIR"

# Verifica dipendenze con Python di sistema
echo "[*] Verifica dipendenze..."
MISSING=""
python3 -c "import fastapi" 2>/dev/null || MISSING="$MISSING fastapi"
python3 -c "import uvicorn" 2>/dev/null || MISSING="$MISSING uvicorn"
python3 -c "import PIL" 2>/dev/null || MISSING="$MISSING Pillow"
python3 -c "import requests" 2>/dev/null || MISSING="$MISSING requests"

if [ -n "$MISSING" ]; then
    echo "[!] Dipendenze mancanti:$MISSING"
    echo "[*] Installazione..."
    pip3 install --user fastapi uvicorn Pillow requests python-multipart
    echo ""
fi
echo "[OK] Dipendenze OK"

# Verifica Ollama
echo ""
echo "[*] Verifica Ollama..."
if ! curl -s http://localhost:11434/api/version >/dev/null 2>&1; then
    echo "[!] Ollama non in esecuzione. Avvialo prima!"
    echo "    Comando: ollama serve"
    exit 1
fi
echo "[OK] Ollama attivo"

# Verifica modello vision
echo ""
echo "[*] Verifica modello Vision..."
if ! curl -s http://localhost:11434/api/tags 2>/dev/null | grep -qi "llava\|vision\|bakllava"; then
    echo "[!] Nessun modello vision trovato."
    echo ""
    read -p "Vuoi installare llava ora? [S/n]: " install
    if [[ ! "$install" =~ ^[Nn]$ ]]; then
        echo ""
        echo "[*] Download llava in corso..."
        ollama pull llava
    fi
else
    echo "[OK] Modello vision trovato"
fi

echo ""
echo "======================================================================"
echo "  Servizio in avvio su: http://localhost:5555"
echo "  Premi Ctrl+C per fermare"
echo "======================================================================"
echo ""

# Avvia il servizio
python3 image_service.py
