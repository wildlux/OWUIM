#!/bin/bash
# TTS Service - Sintesi Vocale Italiana

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PARENT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PARENT_DIR"

echo ""
echo "======================================================================"
echo "         TTS SERVICE - Sintesi Vocale Italiana"
echo "======================================================================"
echo ""

# Cerca venv del progetto
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
if [ -f "$PROJECT_ROOT/venv/bin/python" ]; then
    PYTHON="$PROJECT_ROOT/venv/bin/python"
    echo "[OK] Ambiente virtuale trovato: $PYTHON"
elif [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    PYTHON="python3"
    echo "[OK] Ambiente virtuale attivato"
else
    PYTHON="python3"
    echo "[!] Ambiente virtuale non trovato, uso Python di sistema"
fi

# Verifica dipendenze
echo ""
echo "[*] Verifica dipendenze..."
if ! "$PYTHON" -c "import fastapi, uvicorn, requests" 2>/dev/null; then
    echo "[!] Dipendenze base mancanti. Installazione..."
    "$PYTHON" -m pip install fastapi uvicorn requests
fi

# Verifica edge-tts
if ! "$PYTHON" -c "import edge_tts" 2>/dev/null; then
    echo "[!] edge-tts non installato (consigliato per migliore qualità)"
    read -p "Vuoi installarlo ora? [S/n]: " install
    if [[ ! "$install" =~ ^[Nn]$ ]]; then
        "$PYTHON" -m pip install edge-tts
    fi
fi

echo ""
echo "======================================================================"
echo "  Servizio TTS in avvio su: http://localhost:5556"
echo ""
echo "  Endpoint principali:"
echo "    POST /speak    - Sintetizza testo"
echo "    POST /test     - Test voce"
echo "    GET /backends  - Lista backend"
echo "    GET /voices/{backend}  - Lista voci"
echo ""
echo "  Premi Ctrl+C per fermare"
echo "======================================================================"
echo ""

"$PYTHON" tts_service/tts_local.py
