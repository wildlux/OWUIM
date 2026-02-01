#!/bin/bash
#
# Open WebUI + Ollama - Gestore Unificato Linux
# Docker nativo (prestazioni ottimali)
# Include: OpenedAI Speech (TTS locale)
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Colori
G='\033[0;32m' Y='\033[1;33m' R='\033[0;31m' B='\033[0;34m' N='\033[0m' BOLD='\033[1m'

case "${1:-menu}" in
    start)
        echo -e "\n${B}══════════════════════════════════════════════════════════════${N}"
        echo -e "${BOLD}                    AVVIO SERVIZI${N}"
        echo -e "${B}══════════════════════════════════════════════════════════════${N}\n"

        if ! docker info &>/dev/null; then
            echo -e "${R}✗ Docker non disponibile${N}"
            echo "  Avvia con: sudo systemctl start docker"
            exit 1
        fi

        echo "[1/4] Avvio Ollama..."
        pgrep -x ollama >/dev/null || { ollama serve &>/dev/null & sleep 2; }
        echo -e "  ${G}✓${N} Ollama"

        echo "[2/4] Avvio container (Open WebUI + TTS)..."
        cd "$PROJECT_DIR" && docker compose up -d
        echo -e "  ${G}✓${N} Container"

        echo "[3/4] Attesa Open WebUI..."
        for i in {1..30}; do curl -s http://localhost:3000 >/dev/null && break; sleep 1; done
        echo -e "  ${G}✓${N} Open WebUI pronto"

        echo "[4/4] Attesa TTS (OpenedAI Speech)..."
        for i in {1..20}; do curl -s http://localhost:8000/v1/models >/dev/null && break; sleep 1; done
        if curl -s http://localhost:8000/v1/models >/dev/null 2>&1; then
            echo -e "  ${G}✓${N} TTS pronto"
        else
            echo -e "  ${Y}!${N} TTS non ancora pronto (attendi qualche secondo)"
        fi

        echo -e "\n${G}══════════════════════════════════════════════════════════════${N}"
        echo -e "  ${G}✓${N} AVVIATO"
        echo -e "  ${G}●${N} Open WebUI:  http://localhost:3000"
        echo -e "  ${G}●${N} Ollama API:  http://localhost:11434"
        echo -e "  ${G}●${N} TTS API:     http://localhost:8000"
        echo -e "${G}══════════════════════════════════════════════════════════════${N}\n"

        command -v xdg-open &>/dev/null && xdg-open http://localhost:3000 &>/dev/null &
        ;;

    stop)
        echo -e "\n${B}══════════════════════════════════════════════════════════════${N}"
        echo -e "${BOLD}                   ARRESTO SERVIZI${N}"
        echo -e "${B}══════════════════════════════════════════════════════════════${N}\n"

        cd "$PROJECT_DIR" && docker compose down 2>/dev/null
        echo -e "  ${G}✓${N} Container (Open WebUI + TTS)"

        pkill -f "ollama serve" 2>/dev/null || true
        echo -e "  ${G}✓${N} Ollama"

        echo -e "\n${G}✓ Servizi arrestati${N}\n"
        ;;

    status)
        echo -e "\n${B}══════════════════════════════════════════════════════════════${N}"
        echo -e "${BOLD}                    STATO SERVIZI${N}"
        echo -e "${B}══════════════════════════════════════════════════════════════${N}\n"

        docker info &>/dev/null && echo -e "Docker:      ${G}✓ Attivo${N}" || echo -e "Docker:      ${R}✗ Non attivo${N}"
        curl -s http://localhost:11434/api/version >/dev/null && echo -e "Ollama:      ${G}✓ Attivo (11434)${N}" || echo -e "Ollama:      ${R}✗ Non attivo${N}"
        curl -s http://localhost:3000 >/dev/null && echo -e "Open WebUI:  ${G}✓ Attivo (3000)${N}" || echo -e "Open WebUI:  ${R}✗ Non attivo${N}"
        curl -s http://localhost:8000/v1/models >/dev/null && echo -e "TTS (Speech):${G}✓ Attivo (8000)${N}" || echo -e "TTS (Speech):${R}✗ Non attivo${N}"
        echo ""
        ;;

    logs)
        echo -e "\n${B}══════════════════════════════════════════════════════════════${N}"
        echo -e "${BOLD}                    LOG SERVIZI${N}"
        echo -e "${B}══════════════════════════════════════════════════════════════${N}\n"
        cd "$PROJECT_DIR" && docker compose logs -f --tail=50
        ;;

    logs-tts)
        echo -e "\n${B}══════════════════════════════════════════════════════════════${N}"
        echo -e "${BOLD}                    LOG TTS${N}"
        echo -e "${B}══════════════════════════════════════════════════════════════${N}\n"
        cd "$PROJECT_DIR" && docker compose logs -f openedai-speech --tail=50
        ;;

    test-tts)
        echo -e "\n${B}══════════════════════════════════════════════════════════════${N}"
        echo -e "${BOLD}                    TEST TTS${N}"
        echo -e "${B}══════════════════════════════════════════════════════════════${N}\n"

        echo "Generazione audio di test..."
        curl -s http://localhost:8000/v1/audio/speech \
            -H "Content-Type: application/json" \
            -d '{"input":"Ciao! Il sistema text to speech funziona correttamente.","voice":"alloy","model":"tts-1"}' \
            -o /tmp/test_tts.mp3

        if file /tmp/test_tts.mp3 | grep -q "Audio"; then
            echo -e "${G}✓${N} Audio generato: /tmp/test_tts.mp3"
            echo ""
            echo "Riproduzione..."
            command -v mpv &>/dev/null && mpv /tmp/test_tts.mp3 2>/dev/null || \
            command -v aplay &>/dev/null && aplay /tmp/test_tts.mp3 2>/dev/null || \
            command -v paplay &>/dev/null && paplay /tmp/test_tts.mp3 2>/dev/null || \
            echo -e "${Y}!${N} Nessun player trovato. File salvato in /tmp/test_tts.mp3"
        else
            echo -e "${R}✗${N} Errore generazione audio"
        fi
        echo ""
        ;;

    install)
        echo -e "\n${B}══════════════════════════════════════════════════════════════${N}"
        echo -e "${BOLD}                   INSTALLAZIONE${N}"
        echo -e "${B}══════════════════════════════════════════════════════════════${N}\n"

        # Docker
        if ! command -v docker &>/dev/null; then
            echo -e "${Y}Docker non trovato. Installa con:${N}"
            echo "  Ubuntu: sudo apt install docker.io docker-compose"
            echo "  Fedora: sudo dnf install docker docker-compose"
            echo "  Poi: sudo usermod -aG docker \$USER && newgrp docker"
            exit 1
        fi
        echo -e "${G}✓${N} Docker installato"

        # Ollama
        if ! command -v ollama &>/dev/null; then
            echo -e "\n${Y}Installazione Ollama...${N}"
            curl -fsSL https://ollama.com/install.sh | sh
        fi
        echo -e "${G}✓${N} Ollama installato"

        # Desktop entry
        mkdir -p ~/.local/share/applications
        cat > ~/.local/share/applications/openwebui.desktop << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Open WebUI
Comment=Sistema AI Locale con TTS
Exec=$SCRIPT_DIR/openwebui.sh start
Icon=$PROJECT_DIR/ICONA/ICONA_Trasparente.png
Terminal=true
Categories=Development;Utility;
EOF
        echo -e "${G}✓${N} Collegamento desktop creato"

        echo -e "\n${G}══════════════════════════════════════════════════════════════${N}"
        echo -e "  ${G}✓${N} Installazione completata"
        echo -e "  Esegui: ./openwebui.sh start"
        echo -e "${G}══════════════════════════════════════════════════════════════${N}\n"
        ;;

    menu|*)
        echo -e "\n${B}══════════════════════════════════════════════════════════════${N}"
        echo -e "${BOLD}         OPEN WEBUI + OLLAMA - Sistema AI Locale${N}"
        echo -e "${B}══════════════════════════════════════════════════════════════${N}\n"
        echo "Uso: $0 {start|stop|status|install|logs|logs-tts|test-tts}"
        echo ""
        echo "  start    - Avvia servizi (Open WebUI + Ollama + TTS)"
        echo "  stop     - Ferma servizi"
        echo "  status   - Verifica stato"
        echo "  install  - Installa dipendenze"
        echo "  logs     - Mostra log (tutti i container)"
        echo "  logs-tts - Mostra log TTS"
        echo "  test-tts - Test sintesi vocale"
        echo ""
        ;;
esac
