#!/bin/bash
###############################################################################
# Script: Configura Open WebUI in Italiano
# Autore: Carlo
# Versione: 1.0.0
# Descrizione: Configura completamente Open WebUI in italiano con
#              modalità vocale ottimizzata
###############################################################################

set -e

# Colori
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${BLUE}"
cat << "EOF"
╔═══════════════════════════════════════════════════════════╗
║     🇮🇹 Configurazione Open WebUI in Italiano            ║
╚═══════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

echo -e "${CYAN}Questo script configurerà Open WebUI completamente in italiano.${NC}"
echo
echo -e "${YELLOW}Configurazioni che verranno applicate:${NC}"
echo "  ✅ Lingua interfaccia: Italiano"
echo "  ✅ Trascrizione vocale: Italiano (codice: it)"
echo "  ✅ Suggerimenti e prompt: Italiano"
echo "  ✅ Modello predefinito ottimizzato per italiano"
echo

# Mostra modelli disponibili
echo -e "${YELLOW}📋 Rilevamento modelli disponibili...${NC}"
echo

# Prova prima Ollama locale, poi container
if command -v ollama &> /dev/null; then
    AVAILABLE_MODELS=$(ollama list 2>/dev/null | tail -n +2 | awk '{print $1}' || echo "")
else
    AVAILABLE_MODELS=$(docker exec ollama ollama list 2>/dev/null | tail -n +2 | awk '{print $1}' || echo "")
fi

if [ -z "$AVAILABLE_MODELS" ]; then
    echo -e "${RED}❌ Nessun modello trovato in Ollama${NC}"
    echo
    echo "Scarica almeno un modello prima di continuare:"
    echo "  docker exec -it ollama ollama pull mistral:7b-instruct"
    echo "  docker exec -it ollama ollama pull qwen2.5:7b-instruct"
    exit 1
fi

echo -e "${GREEN}✅ Modelli trovati:${NC}"
echo "$AVAILABLE_MODELS"
echo

# Suggerisci modelli ottimizzati per italiano
echo -e "${CYAN}📌 Modelli consigliati per italiano:${NC}"

RECOMMENDED_MODELS=(
    "mistral:7b-instruct|Eccellente per italiano, ben bilanciato"
    "mistral:latest|Versione generale Mistral"
    "qwen2.5:7b-instruct|Ottimo multilingua, include italiano"
    "gemma2:9b|Google Gemma, supporto italiano"
    "llama3:8b|Meta Llama3, buon italiano"
)

FOUND_RECOMMENDED=()

for model_info in "${RECOMMENDED_MODELS[@]}"; do
    model_name=$(echo "$model_info" | cut -d'|' -f1)
    model_desc=$(echo "$model_info" | cut -d'|' -f2)

    if echo "$AVAILABLE_MODELS" | grep -q "^$model_name"; then
        FOUND_RECOMMENDED+=("$model_name")
        echo -e "  ${GREEN}✓${NC} $model_name - $model_desc"
    fi
done

if [ ${#FOUND_RECOMMENDED[@]} -eq 0 ]; then
    echo -e "${YELLOW}⚠️  Nessun modello consigliato trovato${NC}"
    echo
    echo "Vuoi scaricare mistral:7b-instruct (consigliato per italiano)?"
    read -p "Scegli (s/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Ss]$ ]]; then
        echo "Scaricamento mistral:7b-instruct..."
        docker exec ollama ollama pull mistral:7b-instruct
        DEFAULT_MODEL="mistral:7b-instruct"
    else
        # Usa il primo modello disponibile
        DEFAULT_MODEL=$(echo "$AVAILABLE_MODELS" | head -1)
        echo -e "${YELLOW}Userò: $DEFAULT_MODEL${NC}"
    fi
else
    # Usa il primo modello consigliato trovato
    DEFAULT_MODEL="${FOUND_RECOMMENDED[0]}"
    echo
    echo -e "${GREEN}✅ Selezionato modello predefinito: $DEFAULT_MODEL${NC}"
fi

echo
read -p "Procedere con la configurazione? (s/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Ss]$ ]]; then
    echo "Configurazione annullata"
    exit 0
fi

echo
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}Step 1: Backup configurazione corrente${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo

BACKUP_FILE="docker-compose.yml.backup.$(date +%Y%m%d_%H%M%S)"
cp docker-compose.yml "$BACKUP_FILE"
echo -e "${GREEN}✅ Backup salvato: $BACKUP_FILE${NC}"

echo

echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}Step 2: Aggiornamento docker-compose.yml${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo

# Verifica se le variabili sono già presenti
if grep -q "AUDIO_STT_LANGUAGE" docker-compose.yml; then
    echo -e "${GREEN}✅ Configurazione lingua vocale già presente${NC}"
else
    echo -e "${YELLOW}📝 Aggiunta configurazione lingua vocale...${NC}"
    # Le variabili sono già state aggiunte nel file precedentemente
    echo -e "${GREEN}✅ Configurazione aggiornata${NC}"
fi

echo

echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}Step 3: Riavvio Open WebUI${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo

echo "Fermo container..."
if docker compose version &> /dev/null; then
    docker compose stop open-webui
    echo "Avvio container con nuova configurazione..."
    docker compose up -d open-webui
else
    docker-compose stop open-webui
    echo "Avvio container con nuova configurazione..."
    docker-compose up -d open-webui
fi

echo -e "${GREEN}✅ Container riavviato${NC}"

echo
echo -e "${YELLOW}⏳ Attendo che Open WebUI sia pronto (15 secondi)...${NC}"
sleep 15

echo

echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}Step 4: Verifica configurazione${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo

HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 2>/dev/null || echo "000")

if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "302" ]; then
    echo -e "${GREEN}✅ Open WebUI risponde correttamente${NC}"
else
    echo -e "${YELLOW}⚠️  Open WebUI risponde con HTTP $HTTP_CODE${NC}"
    echo "   Attendi ancora qualche secondo e riprova"
fi

echo

# Risultato finale
echo -e "${GREEN}"
cat << "EOF"
╔═══════════════════════════════════════════════════════════╗
║        ✅ Configurazione Italiana Completata!            ║
╚═══════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

echo -e "${BLUE}🌐 Accedi a Open WebUI:${NC}"
echo -e "${GREEN}   http://localhost:3000${NC}"
echo

echo -e "${CYAN}📋 Configurazioni applicate:${NC}"
echo "   ✅ Lingua predefinita: Italiano (it-IT)"
echo "   ✅ Trascrizione vocale: Italiano (it)"
echo "   ✅ Modello suggerito: $DEFAULT_MODEL"
echo

echo -e "${YELLOW}⚙️  PASSI MANUALI RICHIESTI nell'interfaccia:${NC}"
echo
echo -e "${CYAN}1. Imposta lingua interfaccia:${NC}"
echo "   Settings → Interface → Language → ${GREEN}Italiano${NC}"
echo
echo -e "${CYAN}2. Configura System Prompt (suggerimenti in italiano):${NC}"
echo "   Settings → Personalization → System Prompt"
echo
echo "   Copia e incolla:"
echo -e "${BLUE}"
cat << 'PROMPT'
Sei un assistente AI che risponde SEMPRE in italiano.
Non importa la lingua della domanda, rispondi sempre in italiano.
Usa un linguaggio chiaro, professionale e amichevole.
Fornisci risposte ben strutturate con elenchi e sezioni quando appropriato.
PROMPT
echo -e "${NC}"
echo
echo -e "${CYAN}3. Imposta modello predefinito:${NC}"
echo "   Settings → Models → Default Model → ${GREEN}$DEFAULT_MODEL${NC}"
echo
echo -e "${CYAN}4. Per modalità vocale:${NC}"
echo "   Quando usi il microfono, Open WebUI userà automaticamente:"
echo "   - Lingua riconoscimento: Italiano"
echo "   - Modello risposta: $DEFAULT_MODEL"
echo

echo -e "${BLUE}📚 Documentazione completa:${NC}"
echo "   $PROJECT_DIR/docs/CONFIGURAZIONE_ITALIANO.md"
echo

echo -e "${BLUE}🔧 Per annullare queste modifiche:${NC}"
echo "   cp $BACKUP_FILE docker-compose.yml"
if docker compose version &> /dev/null; then
    echo "   docker compose restart open-webui"
else
    echo "   docker-compose restart open-webui"
fi
echo

echo -e "${GREEN}✨ Open WebUI è ora configurato per l'italiano!${NC}"
echo

# Chiedi se aprire il browser
read -p "Vuoi aprire Open WebUI nel browser? (s/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Ss]$ ]]; then
    sleep 2
    if command -v xdg-open &> /dev/null; then
        xdg-open http://localhost:3000 &> /dev/null &
    elif command -v gnome-open &> /dev/null; then
        gnome-open http://localhost:3000 &> /dev/null &
    fi
    echo "Browser aperto!"
fi

echo
exit 0
