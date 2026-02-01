#!/bin/bash

cd "$(dirname "$0")"

echo "================================="
echo "  Avvio Ollama + Open WebUI"
echo "================================="
echo ""

# Controlla se Docker è installato
if ! command -v docker &> /dev/null; then
    echo "ERRORE: Docker non è installato!"
    echo "Installa Docker da: https://docs.docker.com/get-docker/"
    exit 1
fi

# Controlla se Docker Compose è installato
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "ERRORE: Docker Compose non è installato!"
    echo "Installa Docker Compose da: https://docs.docker.com/compose/install/"
    exit 1
fi

# Controlla se Ollama è attivo
echo "Controllo stato Ollama..."
if curl -s http://localhost:11434/api/version > /dev/null 2>&1; then
    echo "✓ Ollama è attivo e funzionante"
else
    echo "⚠ Ollama non risponde sulla porta 11434"
    echo "Tento di avviare Ollama..."
    if command -v ollama &> /dev/null; then
        ollama serve &> /dev/null &
        sleep 3
        if curl -s http://localhost:11434/api/version > /dev/null 2>&1; then
            echo "✓ Ollama avviato con successo"
        else
            echo "ERRORE: Impossibile avviare Ollama"
            echo "Prova ad avviarlo manualmente con: ollama serve"
            exit 1
        fi
    else
        echo "ERRORE: Ollama non è installato!"
        echo "Installa Ollama da: https://ollama.ai"
        exit 1
    fi
fi
echo ""

echo "Avvio dei container Docker..."
echo ""

# Controlla se i container sono già in esecuzione
OPEN_WEBUI_RUNNING=$(docker ps -q -f name=open-webui)

if [ -n "$OPEN_WEBUI_RUNNING" ]; then
    echo "⚠️  Open WebUI è già in esecuzione (container: $OPEN_WEBUI_RUNNING)"
    read -p "Vuoi riavviarlo? (s/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Ss]$ ]]; then
        echo "✓ Mantengo i container attivi"
        echo ""
        echo "================================="
        echo "  Servizi già attivi!"
        echo "================================="
        echo ""
        echo "Open WebUI: http://localhost:3000"
        echo "Ollama API: http://localhost:11434"
        echo ""
        exit 0
    fi
    echo "Riavvio container..."
fi

# Usa docker compose o docker-compose in base alla versione
if docker compose version &> /dev/null; then
    docker compose up -d
else
    docker-compose up -d
fi

echo ""
echo "================================="
echo "  Servizi avviati!"
echo "================================="
echo ""
echo "Open WebUI: http://localhost:3000"
echo "Ollama API: http://localhost:11434"
echo ""
echo "Per vedere i log:"
if docker compose version &> /dev/null; then
    echo "  docker compose logs -f"
else
    echo "  docker-compose logs -f"
fi
echo ""
echo "Per fermare i servizi:"
if docker compose version &> /dev/null; then
    echo "  docker compose down"
else
    echo "  docker-compose down"
fi
echo ""

# Apri il browser dopo qualche secondo
sleep 3
if command -v xdg-open &> /dev/null; then
    xdg-open http://localhost:3000 &> /dev/null &
elif command -v gnome-open &> /dev/null; then
    gnome-open http://localhost:3000 &> /dev/null &
fi
