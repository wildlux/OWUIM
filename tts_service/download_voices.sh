#!/bin/bash
# Download Voci Italiane per TTS Locale
# Scarica Piper TTS + voci Paola e Riccardo

echo ""
echo "===================================================="
echo "   DOWNLOAD VOCI ITALIANE - Piper TTS"
echo "===================================================="
echo ""

cd "$(dirname "$0")"

# Verifica Python
if ! command -v python3 &> /dev/null; then
    echo "[X] Python3 non trovato!"
    echo "    Installa con: sudo apt install python3 python3-pip"
    exit 1
fi

# Verifica requests
if ! python3 -c "import requests" &> /dev/null; then
    echo "[*] Installazione dipendenze..."
    pip3 install requests
fi

# Esegui script
python3 download_voices.py

echo ""
read -p "Premi INVIO per uscire..."
