#!/bin/bash
cd "$(dirname "$0")"

echo "🚀 Avvio Ollama + Open WebUI..."

# Avvia Ollama se installato
if command -v ollama &> /dev/null; then
    if ! curl -s http://localhost:11434/api/version > /dev/null 2>&1; then
        echo "Avvio Ollama..."
        ollama serve &> /dev/null &
        sleep 2
    fi
    echo "✅ Ollama attivo"
fi

# Avvia Open WebUI
docker compose up -d

sleep 5
echo ""
echo "✅ Servizi avviati!"
echo "🌐 Apri: http://localhost:3000"

# Apri browser
if command -v xdg-open &> /dev/null; then
    xdg-open http://localhost:3000 &> /dev/null &
elif command -v open &> /dev/null; then
    open http://localhost:3000
fi
