#!/bin/bash
# =============================================================
# Avvia Commit - Open WebUI Manager
# Script interattivo per creare commit Git
# =============================================================

cd "$(dirname "$0")"

# Colori
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

echo ""
echo -e "${CYAN}${BOLD}=== Open WebUI Manager - Commit Tool ===${NC}"
echo ""

# 1. Mostra stato
echo -e "${YELLOW}File modificati:${NC}"
git status --short
echo ""

# Controlla se ci sono modifiche
if git status --porcelain | grep -q '^'; then
    :
else
    echo -e "${GREEN}Nessuna modifica da committare.${NC}"
    exit 0
fi

# 2. Mostra diff breve
echo -e "${YELLOW}Riepilogo modifiche:${NC}"
git diff --stat
git diff --cached --stat 2>/dev/null
echo ""

# 3. Chiedi quali file aggiungere
echo -e "${BOLD}Cosa vuoi committare?${NC}"
echo "  1) Tutti i file modificati (consigliato)"
echo "  2) Solo file specifici (scelgo io)"
echo "  3) Annulla"
echo ""
read -p "Scelta [1/2/3]: " scelta

case $scelta in
    1)
        # Aggiungi tutto tranne file sensibili
        git add openwebui_gui.py translations.py scripts/system_profiler.py dist/export_manager.py mcp_service/mcp_service.py 2>/dev/null
        # Aggiungi anche altri file tracciati modificati
        git add -u 2>/dev/null
        # Aggiungi file nuovi non sensibili (escludi cache, .env, ecc.)
        git add --ignore-errors *.py *.sh *.md 2>/dev/null
        echo -e "${GREEN}File aggiunti allo staging.${NC}"
        ;;
    2)
        echo ""
        echo -e "${CYAN}File disponibili:${NC}"
        git status --short
        echo ""
        echo "Scrivi i nomi dei file separati da spazio:"
        read -p "> " files
        if [ -n "$files" ]; then
            git add $files
            echo -e "${GREEN}File aggiunti: $files${NC}"
        else
            echo -e "${RED}Nessun file specificato. Annullato.${NC}"
            exit 1
        fi
        ;;
    3|*)
        echo -e "${YELLOW}Annullato.${NC}"
        exit 0
        ;;
esac

echo ""

# 4. Mostra cosa verra' committato
echo -e "${YELLOW}File pronti per il commit:${NC}"
git diff --cached --stat
echo ""

# 5. Tipo di commit
echo -e "${BOLD}Tipo di modifica:${NC}"
echo "  1) feat     - Nuova funzionalita'"
echo "  2) fix      - Correzione bug"
echo "  3) refactor - Riorganizzazione codice"
echo "  4) docs     - Documentazione"
echo "  5) style    - Formattazione/UI"
echo "  6) perf     - Miglioramento prestazioni"
echo "  7) custom   - Scrivo io il prefisso"
echo ""
read -p "Scelta [1-7]: " tipo

case $tipo in
    1) prefix="feat" ;;
    2) prefix="fix" ;;
    3) prefix="refactor" ;;
    4) prefix="docs" ;;
    5) prefix="style" ;;
    6) prefix="perf" ;;
    7)
        read -p "Prefisso: " prefix
        ;;
    *)
        prefix="feat"
        ;;
esac

# 6. Messaggio di commit
echo ""
read -p "Descrizione commit: " messaggio

if [ -z "$messaggio" ]; then
    echo -e "${RED}Messaggio vuoto. Annullato.${NC}"
    git reset HEAD -- . >/dev/null 2>&1
    exit 1
fi

# 7. Conferma
echo ""
echo -e "${CYAN}--- Riepilogo ---${NC}"
echo -e "Commit: ${BOLD}${prefix}: ${messaggio}${NC}"
echo -e "File:"
git diff --cached --name-only
echo ""
read -p "Confermi il commit? [S/n]: " conferma

if [ "$conferma" = "n" ] || [ "$conferma" = "N" ]; then
    git reset HEAD -- . >/dev/null 2>&1
    echo -e "${YELLOW}Annullato.${NC}"
    exit 0
fi

# 8. Esegui commit
git commit -m "$(cat <<EOF
${prefix}: ${messaggio}

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
EOF
)"

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}${BOLD}Commit creato con successo!${NC}"
    echo ""
    git log --oneline -1
    echo ""

    # 9. Chiedi se pushare
    read -p "Vuoi fare push su origin? [s/N]: " push_choice
    if [ "$push_choice" = "s" ] || [ "$push_choice" = "S" ]; then
        git push
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}Push completato!${NC}"
        else
            echo -e "${RED}Errore durante il push.${NC}"
        fi
    else
        echo -e "${YELLOW}Push non eseguito. Fai 'git push' quando vuoi.${NC}"
    fi
else
    echo -e "${RED}Errore durante il commit.${NC}"
    exit 1
fi

echo ""
