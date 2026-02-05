#!/bin/bash
###############################################################################
# Open WebUI Manager - GUI + Image Analysis
###############################################################################

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colori
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# Funzione per attivare venv
activate_venv() {
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
        return 0
    else
        echo -e "${YELLOW}[!] Ambiente virtuale non trovato${NC}"
        echo "Esegui: ./scripts/setup_env.sh"
        return 1
    fi
}

# Funzione per analizzare file
analyze_file() {
    local file="$1"
    echo -e "${BLUE}[*] Analisi: $(basename "$file")${NC}"
    python3 image_analysis/image_converter.py "$file" -f base64
    echo ""
}

# Funzione per analizzare cartella
analyze_folder() {
    local folder="$1"
    echo -e "${BLUE}[*] Analisi cartella: $folder${NC}"
    echo ""

    for ext in png jpg jpeg svg webp gif; do
        for file in "$folder"/*.$ext; do
            if [ -f "$file" ]; then
                analyze_file "$file"
            fi
        done
    done

    echo -e "${GREEN}[OK] Analisi completata!${NC}"
}

# Se passato un argomento, analizzalo
if [ -n "$1" ]; then
    echo ""
    echo "======================================================================"
    echo "  Analisi Immagini"
    echo "======================================================================"
    echo ""

    activate_venv || exit 1

    if [ -d "$1" ]; then
        analyze_folder "$1"
    elif [ -f "$1" ]; then
        analyze_file "$1"
    else
        echo -e "${RED}[X] File/cartella non trovato: $1${NC}"
        exit 1
    fi

    echo ""
    read -p "Premi INVIO per uscire..."
    exit 0
fi

# Menu principale
show_menu() {
    clear
    echo ""
    echo -e "${GREEN}  ======================================================================${NC}"
    echo -e "${GREEN}              OPEN WEBUI MANAGER${NC}"
    echo -e "${GREEN}  ======================================================================${NC}"
    echo ""
    echo "   [1] Avvia GUI Manager (gestione completa)"
    echo "   [2] Avvia Image Analysis Service (porta 5555)"
    echo "   [3] Avvia TTS Service (porta 5556)"
    echo "   [4] Converti immagine singola"
    echo "   [5] Converti cartella immagini"
    echo "   [6] Avvia tutto (GUI + Image + TTS)"
    echo "   [0] Esci"
    echo ""
    echo -e "${GREEN}  ======================================================================${NC}"
    echo ""
    echo -e "  ${YELLOW}TIP: Passa un file/cartella come argomento per analizzarlo!${NC}"
    echo -e "  ${YELLOW}     Esempio: ./run_gui.sh /path/to/images/${NC}"
    echo ""
}

# Avvia venv
activate_venv || exit 1

# Verifica PyQt5
if ! python3 -c "from PyQt5.QtWidgets import QApplication" 2>/dev/null; then
    echo -e "${RED}[X] PyQt5 non trovato!${NC}"
    echo "Installa con: pip install -r requirements.txt"
    exit 1
fi

# Loop menu
while true; do
    show_menu
    read -p "Seleziona opzione: " choice

    case $choice in
        1)
            echo ""
            echo -e "${BLUE}[*] Avvio GUI Manager...${NC}"
            python3 openwebui_gui.py
            ;;
        2)
            echo ""
            echo -e "${BLUE}[*] Avvio Image Analysis Service...${NC}"
            echo "[*] Porta: 5555"
            echo "[*] Premi Ctrl+C per fermare"
            echo ""
            python3 image_analysis/image_service.py
            read -p "Premi INVIO per continuare..."
            ;;
        3)
            echo ""
            echo -e "${BLUE}[*] Avvio TTS Service...${NC}"
            echo "[*] Porta: 5556"
            echo "[*] Premi Ctrl+C per fermare"
            echo ""
            python3 tts_service/tts_local.py
            read -p "Premi INVIO per continuare..."
            ;;
        4)
            echo ""
            read -p "Percorso immagine: " filepath
            if [ -n "$filepath" ]; then
                analyze_file "$filepath"
                read -p "Premi INVIO per continuare..."
            fi
            ;;
        5)
            echo ""
            read -p "Percorso cartella: " folder
            if [ -n "$folder" ]; then
                analyze_folder "$folder"
                read -p "Premi INVIO per continuare..."
            fi
            ;;
        6)
            echo ""
            echo -e "${BLUE}[*] Avvio Image Analysis Service in background...${NC}"
            python3 image_analysis/image_service.py &
            IMAGE_SERVICE_PID=$!
            sleep 2
            echo -e "${GREEN}[OK] Image Service avviato (PID: $IMAGE_SERVICE_PID)${NC}"
            echo "    URL: http://localhost:5555"

            echo ""
            echo -e "${BLUE}[*] Avvio TTS Service in background...${NC}"
            python3 tts_service/tts_local.py &
            TTS_SERVICE_PID=$!
            sleep 2
            echo -e "${GREEN}[OK] TTS Service avviato (PID: $TTS_SERVICE_PID)${NC}"
            echo "    URL: http://localhost:5556"

            echo ""
            echo -e "${BLUE}[*] Avvio GUI Manager...${NC}"
            python3 openwebui_gui.py

            # Ferma i servizi quando la GUI si chiude
            echo ""
            echo -e "${YELLOW}[*] Arresto servizi...${NC}"
            kill $IMAGE_SERVICE_PID 2>/dev/null
            kill $TTS_SERVICE_PID 2>/dev/null
            echo -e "${GREEN}[OK] Servizi arrestati${NC}"
            ;;
        0)
            echo ""
            echo -e "${GREEN}Arrivederci!${NC}"
            exit 0
            ;;
        *)
            echo -e "${RED}Opzione non valida${NC}"
            sleep 2
            ;;
    esac
done
