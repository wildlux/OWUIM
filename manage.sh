#!/bin/bash
###############################################################################
# Open WebUI Manager - Script Unificato
# Autore: Carlo
# Versione: 2.0.0
# Descrizione: Gestione completa di Open WebUI con menu interattivo
###############################################################################

set -e

# Colori
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
BOLD='\033[1m'
NC='\033[0m'

# Directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPTS_DIR="$SCRIPT_DIR/scripts"

# Funzioni di utilità
print_header() {
    clear
    echo -e "${BLUE}"
    cat << "EOF"
    ___                    _    _      _     _   _ ___
   / _ \ _ __   ___ _ __  | |  | | ___| |__ | | | |_ _|
  | | | | '_ \ / _ \ '_ \ | |/\| |/ _ \ '_ \| | | || |
  | |_| | |_) |  __/ | | ||  /\  /  __/ |_) | |_| || |
   \___/| .__/ \___|_| |_| \/  \/ \___|_.__/ \___/|___|
        |_|                                Manager v2.0
EOF
    echo -e "${NC}"
    echo
}

print_status() {
    echo -e "${CYAN}Stato Servizi:${NC}"

    # Ollama
    if curl -s http://localhost:11434/api/version > /dev/null 2>&1; then
        echo -e "  Ollama:     ${GREEN}Attivo${NC}"
    else
        echo -e "  Ollama:     ${RED}Non attivo${NC}"
    fi

    # Open WebUI
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 2>/dev/null || echo "000")
    if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "302" ]; then
        echo -e "  Open WebUI: ${GREEN}Attivo${NC} (http://localhost:3000)"
    else
        echo -e "  Open WebUI: ${RED}Non attivo${NC}"
    fi

    echo
}

docker_cmd() {
    if docker compose version &> /dev/null; then
        docker compose "$@"
    else
        docker-compose "$@"
    fi
}

# ============================================================================
# FUNZIONI PRINCIPALI
# ============================================================================

do_start() {
    echo -e "${GREEN}Avvio servizi...${NC}"
    echo

    # Controlla Ollama
    if ! curl -s http://localhost:11434/api/version > /dev/null 2>&1; then
        echo "Avvio Ollama..."
        if command -v ollama &> /dev/null; then
            ollama serve &> /dev/null &
            sleep 3
        fi
    fi

    # Avvia container
    cd "$SCRIPT_DIR"
    docker_cmd up -d

    echo
    echo -e "${GREEN}Servizi avviati!${NC}"
    echo -e "Open WebUI: ${CYAN}http://localhost:3000${NC}"

    # Apri browser
    sleep 2
    if command -v xdg-open &> /dev/null; then
        xdg-open http://localhost:3000 &> /dev/null &
    fi
}

do_stop() {
    echo -e "${YELLOW}Arresto servizi...${NC}"
    cd "$SCRIPT_DIR"
    docker_cmd down
    echo -e "${GREEN}Servizi arrestati${NC}"
}

do_restart() {
    echo -e "${YELLOW}Riavvio servizi...${NC}"
    cd "$SCRIPT_DIR"
    docker_cmd restart
    echo -e "${GREEN}Servizi riavviati${NC}"
}

do_logs() {
    echo -e "${CYAN}Log in tempo reale (Ctrl+C per uscire):${NC}"
    echo
    cd "$SCRIPT_DIR"
    docker_cmd logs -f
}

do_update() {
    echo -e "${YELLOW}Aggiornamento Open WebUI...${NC}"
    echo

    cd "$SCRIPT_DIR"

    # Stop
    docker_cmd stop open-webui
    docker rm -f open-webui 2>/dev/null || true

    # Pull nuova immagine
    echo "Download ultima versione..."
    docker pull ghcr.io/open-webui/open-webui:main

    # Riavvia
    docker_cmd up -d open-webui

    echo
    echo -e "${GREEN}Aggiornamento completato!${NC}"
}

do_fix() {
    echo -e "${YELLOW}Riparazione Open WebUI...${NC}"
    echo

    cd "$SCRIPT_DIR"

    # Stop e rimuovi
    docker_cmd stop open-webui
    docker rm -f open-webui 2>/dev/null || true
    docker rmi ghcr.io/open-webui/open-webui:main 2>/dev/null || true

    # Pulisci cache
    docker system prune -f > /dev/null 2>&1

    # Scarica e avvia
    echo "Download immagine fresca..."
    docker pull ghcr.io/open-webui/open-webui:main
    docker_cmd up -d open-webui

    echo
    echo -e "${GREEN}Riparazione completata!${NC}"
}

do_configure_italian() {
    echo -e "${CYAN}Configurazione Italiano${NC}"
    echo

    # Mostra modelli
    echo "Modelli disponibili:"
    if command -v ollama &> /dev/null; then
        ollama list 2>/dev/null || docker exec ollama ollama list 2>/dev/null || echo "Nessun modello"
    fi

    echo
    echo -e "${YELLOW}Configurazioni da applicare manualmente in Open WebUI:${NC}"
    echo
    echo "1. Settings -> Interface -> Language -> Italiano"
    echo
    echo "2. Settings -> Personalization -> System Prompt:"
    echo -e "${CYAN}"
    cat << 'PROMPT'
Sei un assistente AI che risponde SEMPRE in italiano.
Non importa la lingua della domanda, rispondi sempre in italiano.
Usa un linguaggio chiaro, professionale e amichevole.
PROMPT
    echo -e "${NC}"
    echo
    echo "3. Settings -> Models -> Default Model -> scegli il modello"
    echo
}

do_lan_access() {
    echo -e "${CYAN}Configurazione Accesso LAN${NC}"
    echo

    LOCAL_IP=$(hostname -I | awk '{print $1}')
    echo "IP locale: $LOCAL_IP"
    echo

    echo "Opzioni:"
    echo "  1) Abilita accesso LAN (0.0.0.0)"
    echo "  2) Disabilita accesso LAN (127.0.0.1)"
    echo "  0) Annulla"
    echo
    read -p "Scelta: " choice

    cd "$SCRIPT_DIR"

    case $choice in
        1)
            sed -i 's/127\.0\.0\.1:3000/0.0.0.0:3000/g' docker-compose.yml
            sed -i 's/127\.0\.0\.1:11434/0.0.0.0:11434/g' docker-compose.yml
            docker_cmd down && docker_cmd up -d
            echo
            echo -e "${GREEN}Accesso LAN abilitato!${NC}"
            echo -e "Accedi da altri dispositivi: ${CYAN}http://$LOCAL_IP:3000${NC}"
            ;;
        2)
            sed -i 's/0\.0\.0\.0:3000/127.0.0.1:3000/g' docker-compose.yml
            sed -i 's/0\.0\.0\.0:11434/127.0.0.1:11434/g' docker-compose.yml
            docker_cmd down && docker_cmd up -d
            echo
            echo -e "${GREEN}Accesso LAN disabilitato${NC}"
            echo "Accessibile solo da localhost"
            ;;
        *)
            echo "Annullato"
            ;;
    esac
}

do_https() {
    echo -e "${CYAN}Configurazione HTTPS${NC}"
    echo
    echo "HTTPS richiede nginx e un certificato SSL."
    echo "Questo permette l'uso del microfono da dispositivi mobili."
    echo

    if [ -f "$SCRIPTS_DIR/enable_https.sh" ]; then
        read -p "Eseguire configurazione HTTPS? (s/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Ss]$ ]]; then
            bash "$SCRIPTS_DIR/enable_https.sh"
        fi
    else
        echo -e "${YELLOW}Script HTTPS non trovato in scripts/${NC}"
    fi
}

do_backup() {
    echo -e "${CYAN}Backup su USB${NC}"
    echo

    if [ -f "$SCRIPTS_DIR/backup_to_usb.sh" ]; then
        bash "$SCRIPTS_DIR/backup_to_usb.sh"
    else
        echo -e "${YELLOW}Script backup non trovato in scripts/${NC}"
    fi
}

do_install_tools() {
    echo -e "${CYAN}Installazione Tools${NC}"
    echo

    if [ -f "$SCRIPTS_DIR/install_tools.py" ]; then
        python3 "$SCRIPTS_DIR/install_tools.py"
    elif [ -f "$SCRIPT_DIR/install_tools.py" ]; then
        python3 "$SCRIPT_DIR/install_tools.py"
    else
        echo -e "${YELLOW}Script install_tools.py non trovato${NC}"
    fi
}

do_models() {
    echo -e "${CYAN}Gestione Modelli Ollama${NC}"
    echo

    echo "Modelli installati:"
    ollama list 2>/dev/null || docker exec ollama ollama list 2>/dev/null || echo "Errore"
    echo

    echo "Opzioni:"
    echo "  1) Scarica nuovo modello"
    echo "  2) Rimuovi modello"
    echo "  0) Indietro"
    echo
    read -p "Scelta: " choice

    case $choice in
        1)
            echo
            echo "Modelli consigliati:"
            echo "  - mistral:7b-instruct (buon italiano)"
            echo "  - qwen2.5:7b-instruct (multilingua)"
            echo "  - llama3:8b (versatile)"
            echo
            read -p "Nome modello da scaricare: " model
            if [ -n "$model" ]; then
                ollama pull "$model" 2>/dev/null || docker exec -it ollama ollama pull "$model"
            fi
            ;;
        2)
            read -p "Nome modello da rimuovere: " model
            if [ -n "$model" ]; then
                ollama rm "$model" 2>/dev/null || docker exec ollama ollama rm "$model"
            fi
            ;;
    esac
}

show_info() {
    echo -e "${CYAN}Informazioni Sistema${NC}"
    echo
    echo "Directory progetto: $SCRIPT_DIR"
    echo "Docker Compose: $(docker compose version 2>/dev/null || docker-compose --version 2>/dev/null)"
    echo

    echo "Container:"
    docker ps --format "  {{.Names}}: {{.Status}}" --filter "name=open-webui" --filter "name=ollama" 2>/dev/null
    echo

    echo "Volumi Docker:"
    docker volume ls --format "  {{.Name}}" | grep -E "open-webui|ollama" 2>/dev/null || echo "  Nessuno"
    echo

    echo "Spazio disco:"
    df -h "$SCRIPT_DIR" | tail -1 | awk '{print "  Usato: "$3" / "$2" ("$5" usato)"}'
}

# ============================================================================
# MENU PRINCIPALE
# ============================================================================

show_menu() {
    print_header
    print_status

    echo -e "${BOLD}Menu Principale${NC}"
    echo
    echo -e "${GREEN}  Servizi${NC}"
    echo "    1) Avvia"
    echo "    2) Ferma"
    echo "    3) Riavvia"
    echo "    4) Visualizza log"
    echo
    echo -e "${YELLOW}  Manutenzione${NC}"
    echo "    5) Aggiorna Open WebUI"
    echo "    6) Ripara (fix errori)"
    echo "    7) Backup su USB"
    echo
    echo -e "${CYAN}  Configurazione${NC}"
    echo "    8) Configura italiano"
    echo "    9) Accesso LAN"
    echo "   10) HTTPS (per microfono mobile)"
    echo
    echo -e "${MAGENTA}  Extra${NC}"
    echo "   11) Gestione modelli"
    echo "   12) Installa tools"
    echo "   13) Info sistema"
    echo
    echo "    0) Esci"
    echo
}

# ============================================================================
# GESTIONE ARGOMENTI CLI
# ============================================================================

case "${1:-}" in
    start)
        do_start
        exit 0
        ;;
    stop)
        do_stop
        exit 0
        ;;
    restart)
        do_restart
        exit 0
        ;;
    logs)
        do_logs
        exit 0
        ;;
    update)
        do_update
        exit 0
        ;;
    fix)
        do_fix
        exit 0
        ;;
    status)
        print_status
        exit 0
        ;;
    help|--help|-h)
        echo "Uso: $0 [comando]"
        echo
        echo "Comandi disponibili:"
        echo "  start    - Avvia i servizi"
        echo "  stop     - Ferma i servizi"
        echo "  restart  - Riavvia i servizi"
        echo "  logs     - Mostra i log"
        echo "  update   - Aggiorna Open WebUI"
        echo "  fix      - Ripara Open WebUI"
        echo "  status   - Mostra stato servizi"
        echo
        echo "Senza argomenti: mostra menu interattivo"
        exit 0
        ;;
esac

# ============================================================================
# LOOP MENU INTERATTIVO
# ============================================================================

while true; do
    show_menu
    read -p "Scelta [0-13]: " choice
    echo

    case $choice in
        1)  do_start ;;
        2)  do_stop ;;
        3)  do_restart ;;
        4)  do_logs ;;
        5)  do_update ;;
        6)  do_fix ;;
        7)  do_backup ;;
        8)  do_configure_italian ;;
        9)  do_lan_access ;;
        10) do_https ;;
        11) do_models ;;
        12) do_install_tools ;;
        13) show_info ;;
        0|q|Q)
            echo -e "${GREEN}Arrivederci!${NC}"
            exit 0
            ;;
        *)
            echo -e "${RED}Scelta non valida${NC}"
            ;;
    esac

    echo
    read -p "Premi INVIO per continuare..."
done
