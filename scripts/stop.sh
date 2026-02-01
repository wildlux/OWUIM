#!/bin/bash

cd "$(dirname "$0")"

echo "================================="
echo "  Arresto Ollama + Open WebUI"
echo "================================="
echo ""

# Usa docker compose o docker-compose in base alla versione
if docker compose version &> /dev/null; then
    docker compose down
else
    docker-compose down
fi

echo ""
echo "Servizi arrestati!"
