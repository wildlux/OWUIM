#!/bin/bash

echo "================================="
echo "  Installazione Ollama"
echo "================================="

# Controlla se Ollama è già installato
if command -v ollama &> /dev/null; then
    echo "Ollama è già installato!"
    ollama --version
else
    echo "Installazione di Ollama..."
    curl -fsSL https://ollama.com/install.sh | sh
fi

echo ""
echo "Installazione completata!"
echo ""
echo "Per scaricare un modello, usa:"
echo "  ollama pull llama2"
echo "  ollama pull mistral"
echo "  ollama pull codellama"
