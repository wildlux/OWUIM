#!/bin/bash
###############################################################################
# Script: Backup Completo Open WebUI su Chiavetta USB
# Autore: Carlo
# Versione: 1.0.0
# Descrizione: Crea un backup completo di Open WebUI (configurazioni, tools,
#              dati, e opzionalmente modelli LLM) su chiavetta USB
###############################################################################

set -e  # Exit on error

# Colori per output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# Banner
echo -e "${BLUE}"
cat << "EOF"
╔═══════════════════════════════════════════════════════════╗
║      💾 Backup Open WebUI su Chiavetta USB               ║
╚═══════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

# Variabili globali
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKUP_DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="openwebui_backup_$BACKUP_DATE"
INCLUDE_MODELS=false
USB_MOUNT_POINT=""
BACKUP_DIR=""

# Funzione: Converti bytes in formato leggibile
human_readable_size() {
    local bytes=$1
    if [ $bytes -lt 1024 ]; then
        echo "${bytes}B"
    elif [ $bytes -lt 1048576 ]; then
        echo "$((bytes / 1024))KB"
    elif [ $bytes -lt 1073741824 ]; then
        echo "$((bytes / 1048576))MB"
    else
        echo "$((bytes / 1073741824))GB"
    fi
}

# Funzione: Calcola dimensione directory
get_dir_size() {
    du -sb "$1" 2>/dev/null | awk '{print $1}' || echo "0"
}

# Funzione: Rileva chiavette USB montate
detect_usb_drives() {
    echo -e "${YELLOW}🔍 Ricerca chiavette USB...${NC}"
    echo

    # Array per dispositivi USB
    USB_DEVICES=()
    USB_MOUNTPOINTS=()
    USB_SIZES=()
    USB_LABELS=()

    # Trova dispositivi USB montati
    while IFS= read -r line; do
        DEVICE=$(echo "$line" | awk '{print $1}')
        MOUNTPOINT=$(echo "$line" | awk '{print $3}')

        # Verifica se è un dispositivo USB
        if [[ $DEVICE == /dev/sd* ]] || [[ $DEVICE == /dev/mmcblk* ]]; then
            # Controlla se è su bus USB
            USB_PATH=$(udevadm info --query=property --name="$DEVICE" 2>/dev/null | grep "ID_BUS=usb" || echo "")

            if [ -n "$USB_PATH" ] || [[ $MOUNTPOINT == /media/* ]] || [[ $MOUNTPOINT == /run/media/* ]]; then
                # Ottieni informazioni
                AVAILABLE=$(df -h "$MOUNTPOINT" 2>/dev/null | tail -1 | awk '{print $4}')
                LABEL=$(lsblk -no LABEL "$DEVICE" 2>/dev/null || echo "Senza etichetta")

                USB_DEVICES+=("$DEVICE")
                USB_MOUNTPOINTS+=("$MOUNTPOINT")
                USB_SIZES+=("$AVAILABLE")
                USB_LABELS+=("$LABEL")
            fi
        fi
    done < <(mount | grep -E "/dev/sd|/dev/mmcblk")

    # Mostra dispositivi trovati
    if [ ${#USB_DEVICES[@]} -eq 0 ]; then
        echo -e "${RED}❌ Nessuna chiavetta USB rilevata${NC}"
        echo
        echo "Suggerimenti:"
        echo "1. Inserisci una chiavetta USB"
        echo "2. Attendi qualche secondo per il montaggio automatico"
        echo "3. Verifica con: lsblk"
        echo
        exit 1
    fi

    echo -e "${GREEN}✅ Trovate ${#USB_DEVICES[@]} chiavette USB:${NC}"
    echo

    for i in "${!USB_DEVICES[@]}"; do
        echo -e "${CYAN}[$((i+1))]${NC} ${USB_DEVICES[$i]}"
        echo "    Etichetta: ${USB_LABELS[$i]}"
        echo "    Mount: ${USB_MOUNTPOINTS[$i]}"
        echo "    Disponibile: ${USB_SIZES[$i]}"
        echo
    done
}

# Funzione: Seleziona chiavetta USB
select_usb_drive() {
    detect_usb_drives

    if [ ${#USB_DEVICES[@]} -eq 1 ]; then
        echo -e "${YELLOW}Trovata una sola chiavetta USB${NC}"
        read -p "Usare ${USB_DEVICES[0]} (${USB_MOUNTPOINTS[0]})? (s/n): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Ss]$ ]]; then
            echo "Operazione annullata"
            exit 0
        fi
        USB_MOUNT_POINT="${USB_MOUNTPOINTS[0]}"
    else
        echo -e "${YELLOW}Seleziona la chiavetta USB per il backup:${NC}"
        read -p "Inserisci il numero [1-${#USB_DEVICES[@]}]: " -r SELECTION

        if [[ ! $SELECTION =~ ^[0-9]+$ ]] || [ $SELECTION -lt 1 ] || [ $SELECTION -gt ${#USB_DEVICES[@]} ]; then
            echo -e "${RED}❌ Selezione non valida${NC}"
            exit 1
        fi

        USB_MOUNT_POINT="${USB_MOUNTPOINTS[$((SELECTION-1))]}"
    fi

    echo -e "${GREEN}✅ Selezionata: $USB_MOUNT_POINT${NC}"
    echo
}

# Funzione: Chiedi se includere modelli LLM
ask_include_models() {
    echo -e "${YELLOW}❓ Vuoi includere i modelli LLM nel backup?${NC}"
    echo
    echo -e "${CYAN}Modelli Ollama disponibili:${NC}"

    # Lista modelli
    if docker ps | grep -q ollama; then
        MODELS_LIST=$(docker exec ollama ollama list 2>/dev/null || echo "")
        if [ -n "$MODELS_LIST" ]; then
            echo "$MODELS_LIST"
            echo

            # Calcola dimensione approssimativa
            MODELS_COUNT=$(echo "$MODELS_LIST" | tail -n +2 | wc -l)
            echo -e "${YELLOW}⚠️  Modelli rilevati: $MODELS_COUNT${NC}"
            echo "   Dimensione stimata: $((MODELS_COUNT * 5))GB - $((MODELS_COUNT * 10))GB"
            echo "   Tempo backup: 10-30 minuti (dipende da velocità USB)"
        else
            echo "   Nessun modello trovato"
        fi
    else
        echo "   ⚠️  Container Ollama non in esecuzione"
    fi

    echo
    echo -e "${CYAN}Opzioni:${NC}"
    echo "  [s] Sì - Includi modelli (backup completo, più lento)"
    echo "  [n] No  - Solo configurazioni e dati (backup veloce)"
    echo
    read -p "Scelta [s/n]: " -n 1 -r
    echo

    if [[ $REPLY =~ ^[Ss]$ ]]; then
        INCLUDE_MODELS=true
        echo -e "${GREEN}✅ I modelli LLM saranno inclusi nel backup${NC}"
    else
        INCLUDE_MODELS=false
        echo -e "${YELLOW}⚠️  I modelli LLM NON saranno inclusi${NC}"
        echo "   Dovrai scaricarli nuovamente dopo il ripristino"
    fi
    echo
}

# Funzione: Calcola spazio necessario
calculate_space_needed() {
    echo -e "${YELLOW}📊 Calcolo spazio necessario...${NC}"

    SPACE_NEEDED=0

    # 1. Configurazioni e tools (~10MB)
    CONFIG_SIZE=$(get_dir_size "$PROJECT_DIR")
    SPACE_NEEDED=$((SPACE_NEEDED + CONFIG_SIZE))
    echo "   Configurazioni: $(human_readable_size $CONFIG_SIZE)"

    # 2. Dati Open WebUI (volume docker)
    VOLUME_NAME=$(docker volume ls | grep open-webui | awk '{print $2}' | head -1)
    if [ -n "$VOLUME_NAME" ]; then
        VOLUME_PATH=$(docker volume inspect "$VOLUME_NAME" | grep Mountpoint | awk -F'"' '{print $4}')
        if [ -d "$VOLUME_PATH" ]; then
            DATA_SIZE=$(sudo du -sb "$VOLUME_PATH" 2>/dev/null | awk '{print $1}' || echo "100000000")
            SPACE_NEEDED=$((SPACE_NEEDED + DATA_SIZE))
            echo "   Dati Open WebUI: $(human_readable_size $DATA_SIZE)"
        fi
    fi

    # 3. Modelli Ollama (se richiesto)
    if [ "$INCLUDE_MODELS" = true ]; then
        OLLAMA_VOLUME=$(docker volume ls | grep ollama | awk '{print $2}' | head -1)
        if [ -n "$OLLAMA_VOLUME" ]; then
            OLLAMA_PATH=$(docker volume inspect "$OLLAMA_VOLUME" | grep Mountpoint | awk -F'"' '{print $4}')
            if [ -d "$OLLAMA_PATH" ]; then
                MODELS_SIZE=$(sudo du -sb "$OLLAMA_PATH" 2>/dev/null | awk '{print $1}' || echo "5000000000")
                SPACE_NEEDED=$((SPACE_NEEDED + MODELS_SIZE))
                echo "   Modelli LLM: $(human_readable_size $MODELS_SIZE)"
            fi
        fi
    fi

    # Margine di sicurezza 10%
    SPACE_NEEDED=$((SPACE_NEEDED + SPACE_NEEDED / 10))

    echo
    echo -e "${CYAN}Spazio totale necessario: $(human_readable_size $SPACE_NEEDED)${NC}"

    # Verifica spazio disponibile
    USB_AVAILABLE=$(df -B1 "$USB_MOUNT_POINT" | tail -1 | awk '{print $4}')
    echo -e "${CYAN}Spazio disponibile su USB: $(human_readable_size $USB_AVAILABLE)${NC}"
    echo

    if [ $SPACE_NEEDED -gt $USB_AVAILABLE ]; then
        echo -e "${RED}❌ Spazio insufficiente sulla chiavetta USB!${NC}"
        echo
        echo "Opzioni:"
        echo "1. Usa una chiavetta più grande"
        echo "2. Escludi i modelli LLM (riavvia lo script)"
        echo "3. Libera spazio sulla chiavetta"
        exit 1
    fi

    echo -e "${GREEN}✅ Spazio sufficiente disponibile${NC}"
    echo
}

# Funzione: Crea directory di backup
create_backup_dir() {
    BACKUP_DIR="$USB_MOUNT_POINT/$BACKUP_NAME"

    echo -e "${YELLOW}📁 Creazione directory di backup...${NC}"
    mkdir -p "$BACKUP_DIR"/{config,data,tools,models,scripts}

    echo -e "${GREEN}✅ Directory creata: $BACKUP_DIR${NC}"
    echo
}

# Funzione: Backup configurazioni
backup_configs() {
    echo -e "${YELLOW}📋 Backup configurazioni...${NC}"

    # docker-compose.yml
    if [ -f "$PROJECT_DIR/docker-compose.yml" ]; then
        cp "$PROJECT_DIR/docker-compose.yml" "$BACKUP_DIR/config/"
        echo "   ✓ docker-compose.yml"
    fi

    # .env se presente
    if [ -f "$PROJECT_DIR/.env" ]; then
        cp "$PROJECT_DIR/.env" "$BACKUP_DIR/config/"
        echo "   ✓ .env"
    fi

    # Script Python
    if [ -f "$PROJECT_DIR/install_tools.py" ]; then
        cp "$PROJECT_DIR/install_tools.py" "$BACKUP_DIR/config/"
        echo "   ✓ install_tools.py"
    fi

    # Script bash
    for script in enable_lan_access.sh disable_lan_access.sh backup_to_usb.sh; do
        if [ -f "$PROJECT_DIR/$script" ]; then
            cp "$PROJECT_DIR/$script" "$BACKUP_DIR/config/"
            echo "   ✓ $script"
        fi
    done

    # Documentazione
    if [ -d "$PROJECT_DIR/docs" ]; then
        cp -r "$PROJECT_DIR/docs" "$BACKUP_DIR/config/"
        echo "   ✓ docs/"
    fi

    echo -e "${GREEN}✅ Configurazioni salvate${NC}"
    echo
}

# Funzione: Backup tools
backup_tools() {
    echo -e "${YELLOW}🔧 Backup tools...${NC}"

    if [ -d "$PROJECT_DIR/tools" ]; then
        cp -r "$PROJECT_DIR/tools" "$BACKUP_DIR/"
        TOOLS_COUNT=$(ls -1 "$PROJECT_DIR/tools"/*.py 2>/dev/null | wc -l)
        echo "   ✓ $TOOLS_COUNT tools copiati"
        echo -e "${GREEN}✅ Tools salvati${NC}"
    else
        echo -e "${YELLOW}⚠️  Directory tools non trovata${NC}"
    fi
    echo
}

# Funzione: Backup dati Open WebUI
backup_data() {
    echo -e "${YELLOW}💾 Backup dati Open WebUI...${NC}"

    VOLUME_NAME=$(docker volume ls | grep open-webui | awk '{print $2}' | head -1)

    if [ -z "$VOLUME_NAME" ]; then
        echo -e "${YELLOW}⚠️  Volume Open WebUI non trovato${NC}"
        echo
        return
    fi

    echo "   Volume: $VOLUME_NAME"
    echo "   Backup in corso (può richiedere alcuni minuti)..."

    # Backup volume usando docker run
    docker run --rm \
        -v "$VOLUME_NAME":/source:ro \
        -v "$BACKUP_DIR/data":/backup \
        alpine \
        sh -c "cd /source && cp -a . /backup/" 2>/dev/null

    if [ $? -eq 0 ]; then
        DATA_SIZE=$(du -sh "$BACKUP_DIR/data" | awk '{print $1}')
        echo "   ✓ Dati copiati: $DATA_SIZE"
        echo -e "${GREEN}✅ Dati Open WebUI salvati${NC}"
    else
        echo -e "${RED}❌ Errore durante il backup dei dati${NC}"
    fi
    echo
}

# Funzione: Backup modelli Ollama
backup_models() {
    if [ "$INCLUDE_MODELS" = false ]; then
        echo -e "${YELLOW}⏭️  Backup modelli saltato (non richiesto)${NC}"
        echo
        return
    fi

    echo -e "${YELLOW}🤖 Backup modelli LLM...${NC}"
    echo "   ⚠️  Questa operazione può richiedere 10-30 minuti"
    echo

    OLLAMA_VOLUME=$(docker volume ls | grep ollama | awk '{print $2}' | head -1)

    if [ -z "$OLLAMA_VOLUME" ]; then
        echo -e "${YELLOW}⚠️  Volume Ollama non trovato${NC}"
        echo
        return
    fi

    echo "   Volume: $OLLAMA_VOLUME"
    echo "   Backup in corso..."

    # Progress bar simulata
    docker run --rm \
        -v "$OLLAMA_VOLUME":/source:ro \
        -v "$BACKUP_DIR/models":/backup \
        alpine \
        sh -c "cd /source && cp -a . /backup/" &

    BACKUP_PID=$!

    # Mostra progresso
    while kill -0 $BACKUP_PID 2>/dev/null; do
        CURRENT_SIZE=$(du -sh "$BACKUP_DIR/models" 2>/dev/null | awk '{print $1}' || echo "0")
        echo -ne "   Copiati: $CURRENT_SIZE\r"
        sleep 2
    done

    wait $BACKUP_PID

    if [ $? -eq 0 ]; then
        MODELS_SIZE=$(du -sh "$BACKUP_DIR/models" | awk '{print $1}')
        echo
        echo "   ✓ Modelli copiati: $MODELS_SIZE"
        echo -e "${GREEN}✅ Modelli LLM salvati${NC}"
    else
        echo -e "${RED}❌ Errore durante il backup dei modelli${NC}"
    fi
    echo
}

# Funzione: Crea script di ripristino
create_restore_script() {
    echo -e "${YELLOW}📝 Creazione script di ripristino...${NC}"

    cat > "$BACKUP_DIR/RESTORE.sh" << 'RESTORE_SCRIPT_EOF'
#!/bin/bash
###############################################################################
# Script: Ripristino Backup Open WebUI
# Generato automaticamente da backup_to_usb.sh
###############################################################################

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}"
cat << "EOF"
╔═══════════════════════════════════════════════════════════╗
║         🔄 Ripristino Backup Open WebUI                  ║
╚═══════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

BACKUP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo -e "${YELLOW}📁 Directory backup: $BACKUP_DIR${NC}"
echo

# Chiedi directory destinazione
read -p "Inserisci directory di installazione (default: ~/ollama-webui): " INSTALL_DIR
INSTALL_DIR=${INSTALL_DIR:-~/ollama-webui}
INSTALL_DIR=$(eval echo "$INSTALL_DIR")

echo
echo -e "${YELLOW}📂 Directory destinazione: $INSTALL_DIR${NC}"
mkdir -p "$INSTALL_DIR"

# Ripristina configurazioni
echo -e "${YELLOW}📋 Ripristino configurazioni...${NC}"
cp -r "$BACKUP_DIR/config/"* "$INSTALL_DIR/"
echo -e "${GREEN}✅ Configurazioni ripristinate${NC}"
echo

# Ripristina tools
if [ -d "$BACKUP_DIR/tools" ]; then
    echo -e "${YELLOW}🔧 Ripristino tools...${NC}"
    cp -r "$BACKUP_DIR/tools" "$INSTALL_DIR/"
    echo -e "${GREEN}✅ Tools ripristinati${NC}"
    echo
fi

# Avvia servizi
echo -e "${YELLOW}🚀 Avvio servizi Docker...${NC}"
cd "$INSTALL_DIR"
docker-compose up -d

echo "Attendo avvio servizi..."
sleep 10

# Ripristina dati
if [ -d "$BACKUP_DIR/data" ] && [ "$(ls -A $BACKUP_DIR/data)" ]; then
    echo -e "${YELLOW}💾 Ripristino dati Open WebUI...${NC}"

    VOLUME_NAME=$(docker volume ls | grep open-webui | awk '{print $2}' | head -1)

    if [ -n "$VOLUME_NAME" ]; then
        docker run --rm \
            -v "$BACKUP_DIR/data":/source:ro \
            -v "$VOLUME_NAME":/target \
            alpine \
            sh -c "cd /target && rm -rf * && cp -a /source/. ."

        echo -e "${GREEN}✅ Dati ripristinati${NC}"
    fi
    echo
fi

# Ripristina modelli
if [ -d "$BACKUP_DIR/models" ] && [ "$(ls -A $BACKUP_DIR/models)" ]; then
    echo -e "${YELLOW}🤖 Ripristino modelli LLM...${NC}"
    echo "   ⚠️  Questa operazione può richiedere 10-30 minuti"

    OLLAMA_VOLUME=$(docker volume ls | grep ollama | awk '{print $2}' | head -1)

    if [ -n "$OLLAMA_VOLUME" ]; then
        docker run --rm \
            -v "$BACKUP_DIR/models":/source:ro \
            -v "$OLLAMA_VOLUME":/target \
            alpine \
            sh -c "cd /target && rm -rf * && cp -a /source/. ."

        echo -e "${GREEN}✅ Modelli ripristinati${NC}"
    fi
    echo
else
    echo -e "${YELLOW}⚠️  Modelli LLM non presenti nel backup${NC}"
    echo "   Scaricali manualmente con: docker exec -it ollama ollama pull <model>"
    echo
fi

# Riavvia servizi
echo -e "${YELLOW}🔄 Riavvio servizi...${NC}"
docker-compose restart

echo
echo -e "${GREEN}"
cat << "EOF"
╔═══════════════════════════════════════════════════════════╗
║           ✅ Ripristino Completato!                      ║
╚═══════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

echo -e "${BLUE}🌐 Accedi a Open WebUI:${NC}"
echo -e "${GREEN}   http://localhost:3000${NC}"
echo

RESTORE_SCRIPT_EOF

    chmod +x "$BACKUP_DIR/RESTORE.sh"
    echo -e "${GREEN}✅ Script di ripristino creato: RESTORE.sh${NC}"
    echo
}

# Funzione: Crea file informazioni
create_info_file() {
    echo -e "${YELLOW}📄 Creazione file informazioni...${NC}"

    cat > "$BACKUP_DIR/BACKUP_INFO.txt" << EOF
╔═══════════════════════════════════════════════════════════╗
║           BACKUP OPEN WEBUI - INFORMAZIONI               ║
╚═══════════════════════════════════════════════════════════╝

Data backup: $(date '+%Y-%m-%d %H:%M:%S')
Hostname: $(hostname)
Sistema: $(uname -s) $(uname -r)
Utente: $USER

╔═══════════════════════════════════════════════════════════╗
║                    CONTENUTO BACKUP                       ║
╚═══════════════════════════════════════════════════════════╝

✅ Configurazioni Docker (docker-compose.yml, .env)
✅ Script di gestione (enable/disable LAN, backup)
✅ Tools Open WebUI ($(ls -1 "$PROJECT_DIR/tools"/*.py 2>/dev/null | wc -l) files)
✅ Dati utente e conversazioni
$([ "$INCLUDE_MODELS" = true ] && echo "✅ Modelli LLM Ollama" || echo "❌ Modelli LLM (non inclusi - dovranno essere riscaricati)")

╔═══════════════════════════════════════════════════════════╗
║                  ISTRUZIONI RIPRISTINO                    ║
╚═══════════════════════════════════════════════════════════╝

1. Copia l'intera cartella di backup su un PC con Docker installato

2. Apri un terminale nella cartella di backup

3. Esegui lo script di ripristino:
   chmod +x RESTORE.sh
   ./RESTORE.sh

4. Segui le istruzioni a video

5. Al termine, Open WebUI sarà accessibile su http://localhost:3000

╔═══════════════════════════════════════════════════════════╗
║                    NOTE IMPORTANTI                        ║
╚═══════════════════════════════════════════════════════════╝

⚠️  REQUISITI SISTEMA:
   - Docker e Docker Compose installati
   - Almeno 8GB RAM (16GB raccomandati)
   - Spazio disco: $(du -sh "$BACKUP_DIR" | awk '{print $1}')

$([ "$INCLUDE_MODELS" = false ] && cat << MODELS_NOTE
⚠️  MODELLI LLM NON INCLUSI:
   Dopo il ripristino, scarica i modelli manualmente:

   docker exec -it ollama ollama pull qwen2.5:7b-instruct-q4_K_M
   docker exec -it ollama ollama pull mistral:7b-instruct
   docker exec -it ollama ollama pull qwen2-math:latest
MODELS_NOTE
)

📚 DOCUMENTAZIONE:
   Consulta docs/LAN_ACCESS.md per configurazione accesso LAN

🔧 SUPPORTO:
   Per problemi, controlla i log:
   docker-compose logs -f

╔═══════════════════════════════════════════════════════════╗
║                    STRUTTURA BACKUP                       ║
╚═══════════════════════════════════════════════════════════╝

$BACKUP_NAME/
├── config/              Configurazioni Docker e script
├── tools/               Tools Open WebUI
├── data/                Dati utente e conversazioni
$([ "$INCLUDE_MODELS" = true ] && echo "├── models/              Modelli LLM Ollama")
├── RESTORE.sh           Script di ripristino
└── BACKUP_INFO.txt      Questo file

Backup creato con: backup_to_usb.sh v1.0.0
Autore: Carlo
EOF

    echo -e "${GREEN}✅ File informazioni creato: BACKUP_INFO.txt${NC}"
    echo
}

# Funzione principale
main() {
    echo -e "${CYAN}Questo script creerà un backup completo di Open WebUI su chiavetta USB${NC}"
    echo

    # Step 1: Seleziona USB
    select_usb_drive

    # Step 2: Chiedi se includere modelli
    ask_include_models

    # Step 3: Calcola e verifica spazio
    calculate_space_needed

    # Conferma finale
    echo -e "${YELLOW}╔═══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${YELLOW}║               RIEPILOGO BACKUP                            ║${NC}"
    echo -e "${YELLOW}╚═══════════════════════════════════════════════════════════╝${NC}"
    echo
    echo "Destinazione: $USB_MOUNT_POINT"
    echo "Nome backup: $BACKUP_NAME"
    echo "Modelli LLM: $([ "$INCLUDE_MODELS" = true ] && echo "SÌ" || echo "NO")"
    echo
    read -p "Procedere con il backup? (s/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Ss]$ ]]; then
        echo "Backup annullato"
        exit 0
    fi
    echo

    # Inizio backup
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}               INIZIO BACKUP                               ${NC}"
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo

    START_TIME=$(date +%s)

    # Step 4: Crea directory backup
    create_backup_dir

    # Step 5: Backup configurazioni
    backup_configs

    # Step 6: Backup tools
    backup_tools

    # Step 7: Backup dati
    backup_data

    # Step 8: Backup modelli (se richiesto)
    backup_models

    # Step 9: Crea script ripristino
    create_restore_script

    # Step 10: Crea file informazioni
    create_info_file

    END_TIME=$(date +%s)
    DURATION=$((END_TIME - START_TIME))

    # Risultato finale
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}               BACKUP COMPLETATO!                          ${NC}"
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo

    BACKUP_SIZE=$(du -sh "$BACKUP_DIR" | awk '{print $1}')

    echo -e "${CYAN}📊 Statistiche Backup:${NC}"
    echo "   Tempo impiegato: $((DURATION / 60))m $((DURATION % 60))s"
    echo "   Dimensione totale: $BACKUP_SIZE"
    echo "   Posizione: $BACKUP_DIR"
    echo

    echo -e "${BLUE}📋 File creati:${NC}"
    echo "   ✓ Configurazioni e tools"
    echo "   ✓ Dati utente"
    $([ "$INCLUDE_MODELS" = true ] && echo "   ✓ Modelli LLM")
    echo "   ✓ Script di ripristino (RESTORE.sh)"
    echo "   ✓ File informazioni (BACKUP_INFO.txt)"
    echo

    echo -e "${YELLOW}📖 Per ripristinare il backup:${NC}"
    echo "   1. Su un PC con Docker installato"
    echo "   2. cd $USB_MOUNT_POINT/$BACKUP_NAME"
    echo "   3. ./RESTORE.sh"
    echo

    echo -e "${GREEN}✨ Backup completato con successo!${NC}"
    echo -e "${YELLOW}Non rimuovere la chiavetta USB fino alla visualizzazione di questo messaggio.${NC}"
    echo

    # Sincronizza filesystem
    echo -e "${YELLOW}🔄 Sincronizzazione filesystem...${NC}"
    sync
    echo -e "${GREEN}✅ Sicuro rimuovere la chiavetta USB${NC}"
}

# Esegui main
main

exit 0
