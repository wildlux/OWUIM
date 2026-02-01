#!/bin/bash
# ======================================================================
#  Image Converter - Converte PNG/SVG per compatibilità Open WebUI
# ======================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PARENT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PARENT_DIR"

# Attiva venv se esiste
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
fi

# Se passato un file come argomento, convertilo
if [ -n "$1" ]; then
    echo ""
    echo "Conversione: $1"
    python3 image_analysis/image_converter.py "$1" -f base64
    exit 0
fi

# Menu interattivo
while true; do
    clear
    echo ""
    echo "  ======================================================================"
    echo "              IMAGE CONVERTER per Open WebUI"
    echo "  ======================================================================"
    echo ""
    echo "   Converte PNG/SVG in formato compatibile (evita bug base64 loop)"
    echo ""
    echo "   [1] Converti immagine in Base64 (per incollare in chat)"
    echo "   [2] Converti SVG in PNG"
    echo "   [3] Comprimi immagine in JPEG"
    echo "   [4] Converti tutti i PNG in una cartella"
    echo "   [5] Installa dipendenze (Pillow, cairosvg)"
    echo "   [0] Esci"
    echo ""
    echo "  ======================================================================"
    echo ""
    read -p "Seleziona opzione: " choice

    case $choice in
        1)
            echo ""
            read -p "Percorso immagine: " filepath
            [ -z "$filepath" ] && continue
            python3 image_analysis/image_converter.py "$filepath" -f base64
            echo ""
            read -p "Premi INVIO per continuare..."
            ;;
        2)
            echo ""
            read -p "Percorso SVG: " filepath
            [ -z "$filepath" ] && continue
            python3 image_analysis/image_converter.py "$filepath" -f png
            echo ""
            read -p "Premi INVIO per continuare..."
            ;;
        3)
            echo ""
            read -p "Percorso immagine: " filepath
            [ -z "$filepath" ] && continue
            read -p "Qualità JPEG (1-100, default 70): " quality
            [ -z "$quality" ] && quality=70
            python3 image_analysis/image_converter.py "$filepath" -f jpeg -q "$quality"
            echo ""
            read -p "Premi INVIO per continuare..."
            ;;
        4)
            echo ""
            read -p "Percorso cartella: " folder
            [ -z "$folder" ] && continue
            echo ""
            echo "Conversione di tutti i PNG in: $folder"
            for f in "$folder"/*.png; do
                if [ -f "$f" ]; then
                    echo "Elaborazione: $(basename "$f")"
                    python3 image_analysis/image_converter.py "$f" -f jpeg
                fi
            done
            echo ""
            echo "Completato!"
            read -p "Premi INVIO per continuare..."
            ;;
        5)
            echo ""
            echo "Installazione dipendenze..."
            pip3 install Pillow cairosvg
            echo ""
            echo "Completato!"
            read -p "Premi INVIO per continuare..."
            ;;
        0)
            exit 0
            ;;
        *)
            echo "Opzione non valida"
            sleep 2
            ;;
    esac
done
