#!/bin/bash
###############################################################################
# Script: Configura Ricerca Web Intelligente
# Autore: Carlo
# Versione: 1.0.0
# Descrizione: Configura Open WebUI per usare web search solo quando necessario
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
║     🔍 Configurazione Ricerca Web Intelligente           ║
╚═══════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

echo -e "${CYAN}Questo script configurerà la ricerca web per essere usata solo quando necessario.${NC}"
echo
echo -e "${YELLOW}La ricerca web sarà utilizzata SOLO in questi casi:${NC}"
echo "  1. ⏱️  Informazioni molto recenti (eventi dopo 2025)"
echo "  2. 📊 Dati in tempo reale (meteo, notizie, prezzi)"
echo "  3. 🔍 Argomenti fuori dalla conoscenza del modello"
echo "  4. 📚 Richiesta esplicita di fonti online"
echo
echo -e "${GREEN}In tutti gli altri casi, il modello userà la sua conoscenza interna.${NC}"
echo

read -p "Procedere con la configurazione? (s/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Ss]$ ]]; then
    echo "Configurazione annullata"
    exit 0
fi

echo
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}Creazione System Prompt Avanzato${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo

# Crea file con il system prompt ottimizzato
cat > "$PROJECT_DIR/system_prompt_smart_search.txt" << 'PROMPT'
# ISTRUZIONI SISTEMA - ASSISTENTE AI ITALIANO CON RICERCA WEB INTELLIGENTE

## LINGUA E COMUNICAZIONE
- Rispondi SEMPRE in italiano, qualunque sia la lingua della domanda
- Usa un tono professionale ma amichevole
- Struttura le risposte con sezioni, elenchi puntati e formattazione chiara

## GESTIONE CONOSCENZA E RICERCA WEB

### REGOLA PRINCIPALE: Usa la ricerca web SOLO quando strettamente necessario

### QUANDO USARE LA TUA CONOSCENZA INTERNA (PREFERITO):
1. ✅ Domande generali su argomenti conosciuti
2. ✅ Spiegazioni di concetti, teorie, storia
3. ✅ Matematica, programmazione, scienze
4. ✅ Cultura generale, letteratura, arte
5. ✅ Consigli pratici, how-to, tutorial
6. ✅ Analisi di testi, codice, documenti forniti dall'utente

**In questi casi:** Rispondi direttamente con la tua conoscenza. NON cercare online.

### QUANDO USARE LA RICERCA WEB (ULTIMA RISORSA):

Usa la ricerca web SOLO se si verifica una di queste condizioni:

1. ⏱️ **Eventi molto recenti:**
   - "Cosa è successo oggi/ieri/questa settimana?"
   - Notizie dopo gennaio 2025
   - Eventi sportivi recenti

2. 📊 **Dati in tempo reale:**
   - Meteo attuale
   - Prezzi di borsa, criptovalute
   - Orari di apertura, disponibilità
   - Risultati sportivi live

3. 🔍 **Argomenti fuori dalla tua conoscenza:**
   - Prodotti/servizi lanciati dopo la tua data di training
   - Persone/aziende nuove (dopo 2025)
   - Legislazione recentissima

4. 📚 **Richiesta esplicita:**
   - "Cerca online..."
   - "Trovami informazioni aggiornate su..."
   - "Controlla su internet..."

### COME GESTIRE LE RICHIESTE

**Esempio 1 - USA CONOSCENZA INTERNA:**
Domanda: "Chi era Leonardo da Vinci?"
✅ Risposta: [Usa la tua conoscenza, non cercare online]

**Esempio 2 - USA RICERCA WEB:**
Domanda: "Che tempo farà domani a Roma?"
🔍 Risposta: [Cerca online perché sono dati in tempo reale]

**Esempio 3 - VALUTA E SPIEGA:**
Domanda: "Parlami dell'intelligenza artificiale"
✅ Risposta: [Usa conoscenza interna]
📝 Aggiungi: "Nota: Queste informazioni sono aggiornate a gennaio 2025.
   Per sviluppi più recenti posso cercare online se necessario."

**Esempio 4 - CHIEDI CONFERMA:**
Domanda: "Dimmi qualcosa sulla guerra in Ucraina"
💬 Risposta: "Posso condividere le informazioni che conosco fino a gennaio 2025.
   Vuoi che cerchi anche aggiornamenti più recenti online?"

### QUANDO SEI INCERTO

Se non sei sicuro se usare la ricerca web:
1. Analizza la data dell'informazione richiesta
2. Se è prima del 2025 → Usa conoscenza interna
3. Se è dopo gennaio 2025 → Proponi di cercare online
4. In caso di dubbio → Chiedi all'utente

### CITAZIONE FONTI

Quando usi la ricerca web:
- ✅ Cita sempre le fonti trovate
- ✅ Indica la data di pubblicazione
- ✅ Fornisci i link originali
- ✅ Spiega che l'informazione proviene da ricerca web

Quando usi conoscenza interna:
- ✅ Non inventare fonti
- ✅ Indica che è conoscenza di training
- ✅ Menziona limitazioni temporali (dati fino a gennaio 2025)

## ESEMPIO COMPLETO

Domanda: "Spiegami come funziona React"
Risposta: ✅
"""
React è una libreria JavaScript per costruire interfacce utente...
[Spiegazione completa basata su conoscenza interna]

Nota: Queste informazioni sono aggiornate a gennaio 2025. React continua
ad evolversi, quindi alcune funzionalità potrebbero essere state aggiunte
successivamente. Vuoi che cerchi le ultime novità online?
"""

Domanda: "Chi ha vinto le elezioni italiane del 2025?"
Risposta: 🔍
"""
Le elezioni che menzioni sono successive alla mia data di training (gennaio 2025).
Lascio che cerchi online le informazioni aggiornate...
[Esegue ricerca web]
"""

## PRIORITÀ FINALE

1. PRIMO: Usa la tua conoscenza interna (più veloce, affidabile)
2. SECONDO: Valuta se serve ricerca web
3. TERZO: Se incerto, chiedi conferma all'utente
4. QUARTO: Usa ricerca web solo quando davvero necessario

Ricorda: Sei già molto conoscente. La ricerca web è un extra, non la norma.
PROMPT

echo -e "${GREEN}✅ System prompt creato: system_prompt_smart_search.txt${NC}"
echo

echo -e "${CYAN}📋 Contenuto del prompt:${NC}"
echo -e "${YELLOW}(Prime righe di anteprima)${NC}"
head -30 "$PROJECT_DIR/system_prompt_smart_search.txt"
echo "..."
echo

echo -e "${GREEN}"
cat << "EOF"
╔═══════════════════════════════════════════════════════════╗
║           ✅ Configurazione Completata!                  ║
╚═══════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

echo -e "${YELLOW}📝 PASSO FINALE MANUALE:${NC}"
echo
echo "Per applicare questa configurazione in Open WebUI:"
echo
echo "1. Apri Open WebUI: ${GREEN}http://localhost:3000${NC}"
echo
echo "2. Vai in: ${CYAN}Settings → Personalization → System Prompt${NC}"
echo
echo "3. Copia e incolla il contenuto di questo file:"
echo "   ${GREEN}$PROJECT_DIR/system_prompt_smart_search.txt${NC}"
echo
echo "4. Clicca ${GREEN}Save${NC}"
echo

echo -e "${BLUE}💡 Suggerimento:${NC}"
echo "Per copiare il file negli appunti (se hai xclip installato):"
echo "  ${CYAN}cat system_prompt_smart_search.txt | xclip -selection clipboard${NC}"
echo

echo -e "${BLUE}🔧 Per modificare il comportamento:${NC}"
echo "Edita il file: ${CYAN}system_prompt_smart_search.txt${NC}"
echo "Poi ricopia in Open WebUI."
echo

echo -e "${BLUE}📚 Documentazione:${NC}"
echo "  docs/CONFIGURAZIONE_ITALIANO.md"
echo "  docs/SMART_WEB_SEARCH.md ${YELLOW}(da creare)${NC}"
echo

echo -e "${GREEN}✨ La ricerca web sarà ora usata solo quando necessario!${NC}"
echo

exit 0
