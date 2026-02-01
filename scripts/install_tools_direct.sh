#!/bin/bash
# Script per installare tools direttamente nel container Open WebUI
# Questo script copia i file e li rende disponibili

cd "$(dirname "$0")"

echo "=========================================="
echo "  🔧 Installazione Diretta Tools"
echo "=========================================="
echo ""

# Verifica che il container sia attivo
if ! docker ps | grep -q open-webui; then
    echo "❌ Il container open-webui non è attivo!"
    echo "   Avvialo con: ./start.sh"
    exit 1
fi

echo "📦 Copio i tools nel container..."
echo ""

# Crea directory nel container se non esiste
docker exec open-webui mkdir -p /app/backend/data/tools

# Copia ogni file tool
for tool_file in tools/*.py; do
    if [ -f "$tool_file" ]; then
        filename=$(basename "$tool_file")
        docker cp "$tool_file" open-webui:/app/backend/data/tools/
        echo "✅ Copiato: $filename"
    fi
done

echo ""
echo "=========================================="
echo "  📋 Tools copiati nel container"
echo "=========================================="
echo ""
echo "⚠️  IMPORTANTE: Devi aggiungere i tools manualmente in Open WebUI:"
echo ""
echo "1. Apri http://localhost:3000"
echo "2. Vai su Admin Panel (⚙️) → Functions → Tools"
echo "3. Clicca '+ Create new tool'"
echo "4. Copia il contenuto di ogni file .py dalla cartella tools/"
echo ""
echo "I file sono disponibili in: $(pwd)/tools/"
echo ""
echo "Lista tools disponibili:"
ls -1 tools/*.py 2>/dev/null | while read f; do
    name=$(grep -m1 "title:" "$f" | cut -d'"' -f2)
    echo "  - $(basename $f): $name"
done
