#!/bin/bash
###############################################################################
# Open WebUI Manager - Launcher
###############################################################################

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colori
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# Funzione per creare/attivare venv
activate_venv() {
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
        return 0
    else
        echo -e "${YELLOW}[!] Ambiente virtuale non trovato${NC}"
        echo -e "${BLUE}[*] Creazione ambiente virtuale...${NC}"
        echo "    Questa operazione viene eseguita solo la prima volta."
        echo ""

        python3 -m venv "$SCRIPT_DIR/venv"
        if [ $? -ne 0 ]; then
            echo -e "${RED}[X] Impossibile creare l'ambiente virtuale.${NC}"
            echo "Prova: sudo apt install python3-venv"
            return 1
        fi
        echo -e "${GREEN}[OK] Ambiente virtuale creato${NC}"

        "$SCRIPT_DIR/venv/bin/pip" install --upgrade pip > /dev/null 2>&1

        echo -e "${BLUE}[*] Installazione dipendenze...${NC}"
        if [ -d "$SCRIPT_DIR/packages" ]; then
            echo "    Installazione da pacchetti locali..."
            "$SCRIPT_DIR/venv/bin/pip" install --no-index --find-links="$SCRIPT_DIR/packages" -r "$SCRIPT_DIR/requirements.txt" > /dev/null 2>&1
            if [ $? -ne 0 ]; then
                echo "    Alcuni pacchetti mancanti, scaricamento da internet..."
                "$SCRIPT_DIR/venv/bin/pip" install --find-links="$SCRIPT_DIR/packages" -r "$SCRIPT_DIR/requirements.txt"
            else
                echo -e "${GREEN}[OK] Dipendenze installate (offline)${NC}"
            fi
        else
            echo "    Scaricamento da internet..."
            "$SCRIPT_DIR/venv/bin/pip" install -r "$SCRIPT_DIR/requirements.txt"
        fi
        echo ""

        source venv/bin/activate
        return 0
    fi
}

# Avvia venv
activate_venv || exit 1

# Verifica PyQt5
if ! python3 -c "from PyQt5.QtWidgets import QApplication" 2>/dev/null; then
    echo -e "${RED}[X] PyQt5 non trovato!${NC}"
    echo "Installa con: pip install -r requirements.txt"
    exit 1
fi

# Menu principale
show_menu() {
    clear
    echo ""
    echo -e "${GREEN}  ======================================================================${NC}"
    echo -e "${GREEN}              OPEN WEBUI MANAGER${NC}"
    echo -e "${GREEN}  ======================================================================${NC}"
    echo ""
    echo "   [1] Avvia GUI Manager"
    echo "   [2] Avvia tutto (GUI + servizi in background)"
    echo "   [0] Esci"
    echo ""
    echo -e "${GREEN}  ======================================================================${NC}"
    echo ""
    echo -e "  ${YELLOW}I servizi (TTS, Immagini, Documenti) si gestiscono dal tab MCP.${NC}"
    echo ""
}

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
            # Usa il Python del venv per i servizi
            VENV_PYTHON="$SCRIPT_DIR/venv/bin/python"
            if [ ! -f "$VENV_PYTHON" ]; then
                VENV_PYTHON="python3"
            fi

            echo ""
            echo -e "${BLUE}[*] Avvio Image Analysis Service in background...${NC}"
            "$VENV_PYTHON" "$SCRIPT_DIR/image_analysis/image_service.py" &
            IMAGE_SERVICE_PID=$!
            sleep 2
            echo -e "${GREEN}[OK] Image Service avviato (PID: $IMAGE_SERVICE_PID)${NC}"
            echo "    URL: http://localhost:5555"

            echo ""
            echo -e "${BLUE}[*] Avvio TTS Service in background...${NC}"
            "$VENV_PYTHON" "$SCRIPT_DIR/tts_service/tts_local.py" &
            TTS_SERVICE_PID=$!
            sleep 2
            echo -e "${GREEN}[OK] TTS Service avviato (PID: $TTS_SERVICE_PID)${NC}"
            echo "    URL: http://localhost:5556"

            echo ""
            echo -e "${BLUE}[*] Avvio GUI Manager...${NC}"
            "$VENV_PYTHON" "$SCRIPT_DIR/openwebui_gui.py"

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
