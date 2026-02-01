#!/bin/bash
# ============================================
#  🚀 Installazione Ollama + Open WebUI
#  Con tutti i tools preconfigurati!
# ============================================

set -e
cd "$(dirname "$0")"

echo ""
echo "=========================================="
echo "  🚀 Installazione Ollama + Open WebUI"
echo "=========================================="
echo ""

# Controlla se Docker è installato
if ! command -v docker &> /dev/null; then
    echo "❌ Docker non è installato!"
    echo ""
    echo "Installa Docker:"
    echo "  Ubuntu/Debian: sudo apt install docker.io docker-compose"
    echo "  Oppure: https://docs.docker.com/get-docker/"
    exit 1
fi

echo "✅ Docker trovato"

# Controlla se Ollama è installato localmente
if command -v ollama &> /dev/null; then
    echo "✅ Ollama trovato"

    # Verifica se è attivo
    if ! curl -s http://localhost:11434/api/version > /dev/null 2>&1; then
        echo "⚠️  Ollama non è attivo, lo avvio..."
        ollama serve &> /dev/null &
        sleep 3
    fi
    echo "✅ Ollama attivo"
else
    echo "⚠️  Ollama non trovato localmente"
    echo ""
    echo "Installa Ollama da: https://ollama.ai"
    echo "Oppure esegui: curl -fsSL https://ollama.ai/install.sh | sh"
    echo ""
    read -p "Vuoi continuare senza Ollama locale? (s/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Ss]$ ]]; then
        exit 1
    fi
fi

# Crea directory per i dati
mkdir -p data

# Se esiste il database preconfigurato, usalo
if [ -f "webui.db" ]; then
    echo "📦 Database con tools trovato, lo uso..."
    cp webui.db data/
fi

# Avvia i container
echo ""
echo "🐳 Avvio Open WebUI..."
docker compose up -d

echo ""
echo "⏳ Attendo avvio servizi..."
sleep 10

# Verifica che sia attivo
if curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo ""
    echo "=========================================="
    echo "  ✅ INSTALLAZIONE COMPLETATA!"
    echo "=========================================="
    echo ""
    echo "🌐 Apri nel browser: http://localhost:3000"
    echo ""
    echo "📋 Al primo accesso:"
    echo "   1. Registra un nuovo account"
    echo "   2. I tools sono già preinstallati!"
    echo "   3. Nelle chat, clicca + per usare i tools"
    echo ""
    echo "🛑 Per fermare: ./stop.sh"
    echo "🚀 Per riavviare: ./start.sh"
    echo ""

    # Apri browser
    if command -v xdg-open &> /dev/null; then
        xdg-open http://localhost:3000 &> /dev/null &
    elif command -v open &> /dev/null; then
        open http://localhost:3000
    fi
else
    echo "❌ Errore nell'avvio. Controlla i log con: docker compose logs"
fi
