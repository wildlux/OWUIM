# 🚀 Guida Completa - Open WebUI + Scientific Council

**Autore:** Carlo | **Versione:** 1.0.0 | **Data:** 2026-01-22

Sistema completo di LLM locali con 11 tools specializzati, concilio multi-modello, accesso LAN e backup automatico.

---

## 📋 INDICE RAPIDO

1. [Installazione e Avvio](#1-installazione-e-avvio)
2. [Configurazione Italiana](#2-configurazione-italiana)
3. [Modalità Vocale](#3-modalità-vocale)
4. [Ricerca Web Intelligente](#4-ricerca-web-intelligente)
5. [Scientific Council](#5-scientific-council)
6. [Accesso da Cellulare](#6-accesso-da-cellulare-lan)
7. [Backup su USB](#7-backup-su-usb)
8. [Tools Disponibili](#8-tools-disponibili)
9. [Gestione Modelli](#9-gestione-modelli)
10. [Troubleshooting](#10-troubleshooting)

---

## 1. INSTALLAZIONE E AVVIO

### Avvio Servizi
```bash
./start.sh              # Avvia Open WebUI + Ollama
./stop.sh               # Ferma i servizi
```

### Prima Configurazione
1. Apri `http://localhost:3000`
2. Crea account (primo utente = admin)
3. Scarica modelli: `ollama pull mistral:7b-instruct`

---

## 2. CONFIGURAZIONE ITALIANA

### Script Automatico
```bash
./configure_italian.sh
```

### Configurazione Manuale

**Settings → Interface → Language:** `Italiano`

**Settings → Personalization → System Prompt:**
```
Sei un assistente AI che risponde SEMPRE in italiano.
Non importa la lingua della domanda, rispondi sempre in italiano.
Usa un linguaggio chiaro, professionale e amichevole.
Fornisci risposte ben strutturate con elenchi e sezioni quando appropriato.
```

**Settings → Models → Default Model:** `mistral:7b-instruct`

---

## 3. MODALITÀ VOCALE

### Problema: "Autorizzazione Negata"

**Soluzione PC:**
1. Usa `http://localhost:3000` (non IP)
2. Clicca "Consenti" per microfono
3. Se bloccato: 🔒 → Autorizzazioni → Microfono → Consenti

**Soluzione Cellulare** (richiede HTTPS):
```bash
./enable_https.sh
```
Poi accedi da: `https://192.168.1.X` (accetta certificato)

### Configurazione Lingua Vocale

Già configurato automaticamente:
- Riconoscimento: Italiano (`it`)
- Modello risposta: `mistral:7b-instruct`

---

## 4. RICERCA WEB INTELLIGENTE

### Configurazione

```bash
./configure_smart_websearch.sh
```

Copia il contenuto di `system_prompt_smart_search.txt` in:
**Settings → Personalization → System Prompt**

### Quando Usa Ricerca Web

**SÌ (ricerca online):**
- Eventi dopo gennaio 2025
- Meteo, notizie, prezzi in tempo reale
- Richiesta esplicita ("cerca online...")

**NO (usa conoscenza):**
- Storia, scienza, cultura
- Programmazione generale
- Spiegazioni concetti
- Matematica

---

## 5. SCIENTIFIC COUNCIL

### Descrizione
Consulta 3-5 modelli LLM in parallelo con votazione intelligente.

### Funzionalità

| Funzione | Descrizione |
|----------|-------------|
| `consult_council()` | Consultazione multi-LLM con consenso |
| `generate_latex_formula()` | LaTeX da linguaggio naturale |
| `verify_proof()` | Verifica dimostrazioni matematiche |
| `generate_bibliography()` | BibTeX/APA/IEEE |
| `create_exercises()` | Esercizi + soluzioni step-by-step |
| `plot_mathematical()` | Grafici 2D/3D interattivi |

### Esempio Uso
```python
consult_council(
    domanda="Teorema di Pitagora",
    dominio="matematica",
    strategia="comparative"
)
```

### Modelli Consigliati
```bash
ollama pull qwen2-math          # Matematica
ollama pull mistral:7b-instruct # Italiano
ollama pull qwen2.5-coder:7b    # Codice
ollama pull gemma2:9b           # Generale
```

---

## 6. ACCESSO DA CELLULARE (LAN)

### Attivazione
```bash
./enable_lan_access.sh    # Abilita
./disable_lan_access.sh   # Disabilita
```

### Connessione
1. Cellulare sulla stessa WiFi del PC
2. Apri: `http://192.168.1.X:3000` (IP mostrato dallo script)
3. Per microfono: serve HTTPS → `./enable_https.sh`

---

## 7. BACKUP SU USB

### Creazione Backup
```bash
./backup_to_usb.sh
```

Lo script:
1. Rileva automaticamente chiavette USB
2. Chiede se includere modelli LLM
3. Verifica spazio disponibile
4. Crea backup completo
5. Genera script ripristino automatico

### Ripristino
```bash
cd /media/usb/openwebui_backup_XXXXXX
./RESTORE.sh
```

### Dimensioni Tipiche

| Componente | Dimensione |
|------------|------------|
| Config + Tools | ~20MB |
| Dati utente | ~50-500MB |
| Modello 7B | ~4-5GB |
| Backup completo (5 modelli) | ~25-30GB |

---

## 8. TOOLS DISPONIBILI

### Installazione
```bash
python3 install_tools.py
```

### Lista Tools

1. **Text Assistant** - Scrittura, editing
2. **Math Assistant** - Matematica, calcoli
3. **Code Assistant** - Programmazione
4. **Book Assistant** - Creazione libri
5. **Study Assistant** - Studio, riassunti
6. **Creative Writing** - Scrittura creativa
7. **Research Assistant** - Ricerca scientifica
8. **Book Publishing** - Pubblicazione
9. **Productivity Assistant** - Produttività
10. **Finance Italian** - Finanza personale
11. **Scientific Council** 🆕 - Concilio multi-LLM

### Attivazione
**Admin Panel → Functions → Tools → Toggle**

---

## 9. GESTIONE MODELLI

### Comandi Base
```bash
ollama list                    # Lista modelli
ollama pull <modello>          # Scarica
ollama rm <modello>            # Rimuovi
ollama ps                      # Modelli in uso
```

### Modelli Essenziali

| Modello | Scopo | Dimensione |
|---------|-------|------------|
| `mistral:7b-instruct` | Italiano generale | ~4.1GB |
| `qwen2.5:7b-instruct` | Multilingua | ~4.7GB |
| `qwen2-math` | Matematica | ~4.7GB |
| `qwen2.5-coder:7b` | Codice | ~4.7GB |
| `gemma2:9b` | Analisi complessa | ~5.4GB |

---

## 10. TROUBLESHOOTING

### Open WebUI Non Carica (404 JS)
```bash
./update_openwebui.sh    # Aggiorna versione
# oppure
./fix_openwebui.sh       # Fix errori 404
```

### Porta Occupata
```bash
sudo lsof -i :3000
# Cambia porta in docker-compose.yml
```

### Tools Non Compaiono
```bash
python3 install_tools.py  # Reinstalla
# Admin Panel → Functions → Tools → Attiva
```

### Modelli Lenti
- Usa versioni quantizzate (q4_K_M)
- Chiudi app pesanti
- Riduci modelli nel concilio (3 invece di 5)

---

## 📂 STRUTTURA PROGETTO

```
ollama-webui/
├── start.sh                          # Avvia servizi
├── stop.sh                           # Ferma servizi
├── update_openwebui.sh               # Aggiorna Open WebUI
├── fix_openwebui.sh                  # Risolve errori
│
├── configure_italian.sh              # Configura italiano
├── configure_smart_websearch.sh      # Ricerca web smart
├── system_prompt_smart_search.txt    # Prompt generato
│
├── enable_lan_access.sh              # Abilita LAN
├── disable_lan_access.sh             # Disabilita LAN
├── enable_https.sh                   # Abilita HTTPS
├── backup_to_usb.sh                  # Backup USB
│
├── install_tools.py                  # Installa tools
├── docker-compose.yml                # Config Docker
│
├── tools/
│   ├── scientific_council.py         # Tool principale
│   └── [10 altri tools...]
│
└── docs/
    ├── CONFIGURAZIONE_ITALIANO.md    # Guida italiana
    ├── VOICE_MODE_PERMISSIONS.md     # Guida microfono
    ├── SMART_WEB_SEARCH.md           # Guida ricerca
    ├── LAN_ACCESS.md                 # Guida LAN
    └── QUICK_FIX_MICROFONO.md        # Fix rapido
```

---

## 🎯 WORKFLOW CONSIGLIATO

### Setup Iniziale (Una Volta)
```bash
1. ./start.sh                     # Avvia
2. Crea account su localhost:3000
3. ollama pull mistral:7b-instruct
4. ./configure_italian.sh         # Italiano
5. python3 install_tools.py       # Tools
```

### Uso Quotidiano
```bash
./start.sh                        # All'avvio PC
# Usa Open WebUI normalmente
./stop.sh                         # A fine giornata
```

### Uso da Cellulare (Setup Una Volta)
```bash
./enable_lan_access.sh            # Abilita LAN
./enable_https.sh                 # Per microfono
# Poi: https://192.168.1.X da cellulare
```

### Backup Settimanale
```bash
./backup_to_usb.sh                # Ogni settimana
# Escludi modelli (veloce) o includili (completo)
```

---

## ⚙️ CONFIGURAZIONI CHIAVE

### docker-compose.yml
```yaml
environment:
  - DEFAULT_LOCALE=it-IT                # Italiano
  - AUDIO_STT_LANGUAGE=it               # Vocale italiano
  - WEBUI_NAME=Open WebUI
```

### System Prompt (Minimo)
```
Rispondi SEMPRE in italiano.
Usa la ricerca web solo quando strettamente necessario
(eventi recenti, dati tempo reale, richiesta esplicita).
Per tutto il resto usa la tua conoscenza interna.
```

### Modello Predefinito
```
mistral:7b-instruct
```

---

## 📊 REQUISITI SISTEMA

| Componente | Minimo | Raccomandato |
|------------|--------|--------------|
| **RAM** | 8GB | 16GB |
| **CPU** | 4 core | 8 core |
| **Disco** | 50GB | 100GB |
| **OS** | Linux/Windows+WSL2 | Linux |

---

## 🔗 LINK UTILI

### Locali
- Open WebUI: `http://localhost:3000`
- Ollama API: `http://localhost:11434`

### Documentazione Estesa
- `docs/CONFIGURAZIONE_ITALIANO.md` - Setup italiano completo
- `docs/VOICE_MODE_PERMISSIONS.md` - Microfono dettagliato
- `docs/SMART_WEB_SEARCH.md` - Ricerca web avanzata
- `docs/LAN_ACCESS.md` - Accesso LAN completo

### Online
- [Open WebUI](https://github.com/open-webui/open-webui)
- [Ollama](https://ollama.ai/)
- [Modelli Disponibili](https://ollama.ai/library)

---

## 🆘 SUPPORTO RAPIDO

| Problema | Soluzione | Script |
|----------|-----------|--------|
| Errori 404 JS | Aggiorna/Fix | `./update_openwebui.sh` |
| Microfono bloccato | Fix permessi | Vedi sezione 3 |
| Slow responses | Ottimizza modelli | Usa q4_K_M |
| Troppa ricerca web | Smart search | `./configure_smart_websearch.sh` |
| No accesso mobile | Abilita LAN | `./enable_lan_access.sh` |
| Backup completo | USB backup | `./backup_to_usb.sh` |

---

## ✅ CHECKLIST SETUP COMPLETO

- [ ] Servizi avviati (`./start.sh`)
- [ ] Account creato
- [ ] Almeno 3 modelli scaricati
- [ ] Configurazione italiana (`./configure_italian.sh`)
- [ ] System prompt configurato
- [ ] Tools installati (`install_tools.py`)
- [ ] Scientific Council attivato
- [ ] Ricerca web smart configurata
- [ ] Accesso LAN (opzionale)
- [ ] HTTPS per microfono mobile (opzionale)
- [ ] Primo backup creato

---

## 📝 NOTE FINALI

### Manutenzione
- **Settimanale:** Backup su USB
- **Mensile:** Aggiorna Open WebUI (`./update_openwebui.sh`)
- **Trimestrale:** Rivedi modelli installati, rimuovi inutilizzati

### Performance
- Usa max 3-4 modelli attivi contemporaneamente
- Chiudi app pesanti quando usi Scientific Council
- Quantizzazione q4_K_M ottima per 8GB RAM

### Sicurezza
- Password forti per account
- Non esporre su Internet senza VPN
- Backup regolari
- HTTPS solo su LAN domestica

---

**Guida creata:** 2026-01-22
**Mantieni aggiornata:** Rivedi ogni 3 mesi

**Buon utilizzo! 🚀**
