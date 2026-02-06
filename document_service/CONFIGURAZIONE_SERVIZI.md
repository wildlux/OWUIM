# Configurazione Completa Servizi - Open WebUI Manager

> Riferimento parametri per tutti i servizi del sistema AI locale.
> Ultimo aggiornamento: 2026-02-06

---

## Mappa Porte

| Servizio | Porta | Protocollo | URL |
|----------|-------|------------|-----|
| Open WebUI | 3000 | HTTP | http://localhost:3000 |
| Ollama | 11434 | HTTP | http://localhost:11434 |
| Image Analysis | 5555 | HTTP | http://localhost:5555 |
| TTS (Piper) | 5556 | HTTP | http://localhost:5556 |
| Document Reader | 5557 | HTTP | http://localhost:5557 |
| MCP Bridge | 5558 | HTTP | http://localhost:5558 |
| OpenedAI Speech | 8000 | HTTP | http://localhost:8000 |

> **Da Docker** usa `http://host.docker.internal:<porta>` al posto di `localhost`.

---

## 1. Open WebUI (Docker)

### docker-compose.yml - Variabili d'Ambiente

```yaml
services:
  open-webui:
    image: ghcr.io/open-webui/open-webui:main
    ports:
      - "3000:8080"
    extra_hosts:
      - "host.docker.internal:host-gateway"
    environment:
      # === CONNESSIONE OLLAMA ===
      - OLLAMA_BASE_URL=http://host.docker.internal:11434

      # === SICUREZZA ===
      - WEBUI_SECRET_KEY=CAMBIA-QUESTA-CHIAVE-CON-UNA-RANDOM
      - ENABLE_SIGNUP=true

      # === LINGUA ===
      - DEFAULT_LOCALE=it-IT
      - WEBUI_NAME=Open WebUI

      # === MODELLI ===
      - DEFAULT_MODELS=                       # vuoto = auto-detect da Ollama

      # === SPEECH-TO-TEXT (STT) ===
      - AUDIO_STT_ENGINE=openai
      - AUDIO_STT_MODEL=whisper-1
      - WHISPER_MODEL=base                    # base | small | medium | large
      - AUDIO_STT_LANGUAGE=it

      # === TEXT-TO-SPEECH (TTS) ===
      - AUDIO_TTS_ENGINE=openai
      - AUDIO_TTS_OPENAI_API_BASE_URL=http://host.docker.internal:5556/v1
      - AUDIO_TTS_OPENAI_API_KEY=sk-local     # qualsiasi valore, non verificato
      - AUDIO_TTS_MODEL=tts-1
      - AUDIO_TTS_VOICE=paola                 # paola (F) | riccardo (M)

      # === SERVIZI LOCALI ===
      - IMAGE_SERVICE_URL=http://host.docker.internal:5555
      - DOCUMENT_SERVICE_URL=http://host.docker.internal:5557

    volumes:
      - open_webui_data:/app/backend/data
    restart: unless-stopped
```

### OpenedAI Speech (backend TTS alternativo)

```yaml
  openedai-speech:
    image: ghcr.io/matatonic/openedai-speech
    ports:
      - "8000:8000"
    environment:
      - TTS_HOME=/app/voices
      - HF_HOME=/app/voices
    volumes:
      - openedai_speech_data:/app/voices
      - openedai_speech_config:/app/config
    restart: unless-stopped
```

---

## 2. Ollama

### Parametri Base

| Parametro | Valore |
|-----------|--------|
| URL | http://localhost:11434 |
| GPU | NVIDIA (auto-detect) |
| Avvio | `ollama serve` (deve girare sull'host, NON in Docker) |

### API Endpoints

| Endpoint | Metodo | Uso |
|----------|--------|-----|
| `/api/version` | GET | Versione Ollama |
| `/api/tags` | GET | Lista modelli scaricati |
| `/api/generate` | POST | Generazione testo |
| `/api/chat` | POST | Chat con contesto |
| `/api/embed` | POST | Generazione embeddings |
| `/api/pull` | POST | Scarica modello |

### Modelli Consigliati

| Modello | Tipo | RAM | Uso |
|---------|------|-----|-----|
| `qwen2.5:7b-instruct-q4_K_M` | Testo | ~5 GB | Chat generale, codice |
| `llava` | Vision | ~5 GB | Analisi immagini (default) |
| `llama3.2-vision` | Vision | ~5 GB | Analisi immagini (alt.) |
| `bakllava` | Vision | ~4 GB | Vision leggero |
| `moondream` | Vision | ~2 GB | Vision ultra-leggero |

```bash
# Scarica modelli
ollama pull qwen2.5:7b-instruct-q4_K_M
ollama pull llava
```

---

## 3. Servizio Analisi Immagini (:5555)

### Configurazione

| Parametro | Valore Default | Env Var |
|-----------|---------------|---------|
| Porta | 5555 | `SERVICE_PORT` |
| Ollama URL | http://localhost:11434 | `OLLAMA_URL` |
| Modello Vision | llava | `VISION_MODEL` |
| Max dimensione immagine | 1024 px | - |
| Cache | 24 ore | `CACHE_EXPIRY_HOURS` |
| Cartella cache | `.image_cache/` | - |

### Modelli Vision (fallback automatico)

1. `llava` (default)
2. `llama3.2-vision`
3. `bakllava`
4. `moondream`

### API Endpoints

| Endpoint | Metodo | Parametri | Descrizione |
|----------|--------|-----------|-------------|
| `/` | GET | - | Health check |
| `/models` | GET | - | Lista modelli vision disponibili |
| `/analyze` | POST | `file`, `analysis_type`, `custom_prompt`, `use_cache` | Analisi completa |
| `/describe` | POST | `file` | Descrizione rapida |
| `/extract-text` | POST | `file` | Estrazione testo (OCR + Vision) |
| `/analyze-math` | POST | `file` | Analisi contenuto matematico |
| `/batch` | POST | `files[]` | Analisi multipla |
| `/cache` | DELETE | - | Svuota cache |

### Tipi di Analisi (`analysis_type`)

| Tipo | Descrizione |
|------|-------------|
| `complete` | Analisi completa (descrizione, oggetti, testo, colori, contesto) |
| `describe` | Solo descrizione dettagliata |
| `objects` | Elenco oggetti visibili |
| `text` | Estrazione testo visibile |
| `math` | Formule, grafici, contenuto matematico |
| `diagram` | Flowchart, UML, circuiti, schemi |
| `code` | Estrazione codice sorgente da screenshot |

### Avvio

```bash
cd image_analysis
python image_service.py
# oppure
./start_image_service.sh
```

### Test

```bash
# Health check
curl http://localhost:5555/

# Analizza immagine
curl -X POST -F "file=@foto.jpg" -F "analysis_type=complete" http://localhost:5555/analyze

# Descrizione rapida
curl -X POST -F "file=@foto.jpg" http://localhost:5555/describe

# Estrai testo
curl -X POST -F "file=@screenshot.png" http://localhost:5555/extract-text
```

---

## 4. Servizio TTS (:5556)

### Configurazione

| Parametro | Valore Default |
|-----------|---------------|
| Porta | 5556 |
| Cartella modelli Piper | `./piper_models/` |
| Cartella cache | `.tts_cache/` |
| Voce default | paola |
| Velocita default | 1.0 |
| Formato output | wav / mp3 |

### Voci Piper (Offline)

| ID | Nome | Genere | Qualita | Sample Rate |
|----|------|--------|---------|-------------|
| `paola` | Paola | F | medium | 22050 Hz |
| `riccardo` | Riccardo | M | x_low (veloce) | 22050 Hz |

### Mapping Voci OpenAI -> Piper

| Voce OpenAI | Voce Locale |
|-------------|-------------|
| alloy | paola |
| echo | riccardo |
| fable | paola |
| onyx | riccardo |
| nova | paola |
| shimmer | paola |

### Voci Edge-TTS (Online, 16 voci italiane)

| Voce | Genere | Stile |
|------|--------|-------|
| `it-IT-IsabellaNeural` | F | Naturale, caldo |
| `it-IT-ElsaNeural` | F | Standard |
| `it-IT-DiegoNeural` | M | Standard |
| `it-IT-GiuseppeNeural` | M | Maturo |
| `it-IT-BenignoNeural` | M | - |
| `it-IT-CalimeroNeural` | M | - |
| `it-IT-CataldoNeural` | M | - |
| `it-IT-FabiolaNeural` | F | - |
| `it-IT-FiammaNeural` | F | - |
| `it-IT-GianniNeural` | M | - |
| `it-IT-ImeldaNeural` | F | - |
| `it-IT-IrmaNeural` | F | - |
| `it-IT-LisandroNeural` | M | - |
| `it-IT-PalmiraNeural` | F | - |
| `it-IT-PierinaNeural` | F | - |
| `it-IT-RinaldoNeural` | M | - |

### API Endpoints

| Endpoint | Metodo | Parametri | Descrizione |
|----------|--------|-----------|-------------|
| `/` | GET | - | Health check + info sistema |
| `/system` | GET | - | Info profiler e limiti |
| `/voices` | GET | - | Lista voci disponibili |
| `/voices/check` | GET | - | Verifica voci installate |
| `/v1/audio/speech` | POST | `input`, `voice`, `model`, `speed` | Endpoint OpenAI-compatibile |
| `/v1/audio/speech/ready` | GET | - | Preflight check per Open WebUI |
| `/speak` | POST | `text`, `voice`, `speed`, `format` | Sintesi diretta |
| `/test` | POST | `voice`, `text` | Test voce |
| `/test-audio` | GET | - | Scarica ultimo audio di test |
| `/install/{voice_id}` | POST | - | Installa modello voce |
| `/install-piper` | POST | - | Installa eseguibile Piper |
| `/openwebui-config` | GET | - | Config suggerita per Open WebUI |

### Parametri Sintesi

| Parametro | Tipo | Default | Range | Descrizione |
|-----------|------|---------|-------|-------------|
| `text` / `input` | string | (obbligatorio) | - | Testo da sintetizzare |
| `voice` | string | paola | paola, riccardo | Voce da usare |
| `speed` | float | 1.0 | 0.5 - 2.0 | Velocita riproduzione |
| `format` | string | wav | wav, mp3 | Formato audio output |

### Avvio

```bash
cd tts_service
python tts_local.py
# oppure
./start_tts_service.sh
```

### Test

```bash
# Preflight
curl http://localhost:5556/v1/audio/speech/ready

# Voci disponibili
curl http://localhost:5556/voices

# Sintesi (formato OpenAI)
curl -X POST http://localhost:5556/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{"input": "Ciao mondo", "voice": "paola", "model": "tts-1"}' \
  -o output.wav

# Sintesi diretta
curl -X POST -d "text=Buongiorno" -d "voice=riccardo" http://localhost:5556/speak -o audio.mp3
```

---

## 5. Servizio Documenti (:5557)

### Configurazione

| Parametro | Valore Default |
|-----------|---------------|
| Porta | 5557 |
| Cartella cache | `.doc_cache/` |
| Cache | 24 ore |
| Max dimensione file | 50 MB |

### API Endpoints

| Endpoint | Metodo | Parametri | Descrizione |
|----------|--------|-----------|-------------|
| `/` | GET | - | Health check |
| `/formats` | GET | - | Formati supportati con disponibilita |
| `/read` | POST | `file`, `use_cache` | Leggi documento completo |
| `/extract-text` | POST | `file` | Estrai solo testo |
| `/get-metadata` | POST | `file` | Solo metadati |
| `/summary` | POST | `file`, `max_chars=2000` | Riassunto breve |
| `/batch` | POST | `files[]` | Elaborazione multipla |
| `/cache` | DELETE | - | Pulisci cache scaduta |

### Formati Supportati

#### Documenti

| Formato | Estensione | Dipendenza Python |
|---------|------------|-------------------|
| PDF | .pdf | `pypdf` |
| Word | .docx | `python-docx` |
| Word Legacy | .doc | LibreOffice |
| Excel | .xlsx | `openpyxl` |
| Excel Legacy | .xls | LibreOffice |
| PowerPoint | .pptx | `python-pptx` |
| PowerPoint Legacy | .ppt | LibreOffice |

#### OpenDocument

| Formato | Estensione |
|---------|------------|
| Testo | .odt |
| Foglio calcolo | .ods |
| Presentazione | .odp |
| Grafica | .odg |
| Database | .odb |

#### E-book

| Formato | Estensione | Dipendenza |
|---------|------------|------------|
| EPUB | .epub | `ebooklib` |
| MOBI | .mobi | Calibre |
| AZW/AZW3 | .azw, .azw3 | Calibre |
| FictionBook | .fb2 | - |

#### Testo e Markup

| Formato | Estensione |
|---------|------------|
| Testo | .txt |
| Markdown | .md |
| CSV/TSV | .csv, .tsv |
| JSON | .json |
| XML | .xml |
| HTML | .html, .htm |
| LaTeX | .tex |
| YAML | .yaml, .yml |
| TOML | .toml |
| INI | .ini |
| Log | .log |

#### Codice Sorgente (60+ linguaggi)

Python, JavaScript, TypeScript, Java, C, C++, C#, Go, Rust, Ruby, PHP, Swift, R, SQL, Shell, PowerShell, Vue, Svelte, CSS, SCSS, Lua, Dart, Scala, Haskell, Dockerfile, Makefile, Terraform, GraphQL, e altri.

#### Immagini (metadati + OCR)

| Tipo | Estensioni |
|------|------------|
| Standard | .png, .jpg, .gif, .bmp, .tiff, .webp, .ico |
| Editor | .xcf (GIMP), .psd (Photoshop), .kra (Krita) |
| RAW | .cr2, .cr3, .nef, .arw, .orf, .raf, .dng |
| Vettoriali | .svg, .svgz, .wmf, .emf |

### Avvio

```bash
cd document_service
python document_service.py
# oppure
./start_document_service.sh
```

### Test

```bash
# Formati disponibili
curl http://localhost:5557/formats

# Leggi PDF
curl -X POST -F "file=@documento.pdf" http://localhost:5557/read

# Estrai testo da Word
curl -X POST -F "file=@documento.docx" http://localhost:5557/extract-text

# Riassunto
curl -X POST -F "file=@documento.pdf" -F "max_chars=1000" http://localhost:5557/summary
```

---

## 6. MCP Bridge Service (:5558)

### Configurazione

| Parametro | Valore Default |
|-----------|---------------|
| Porta | 5558 |
| TTS URL | http://localhost:5556 |
| Image URL | http://localhost:5555 |
| Document URL | http://localhost:5557 |
| Cartella cache | `.mcp_cache/` |

### API Endpoints

| Endpoint | Metodo | Descrizione |
|----------|--------|-------------|
| `/` | GET | Health check |
| `/services` | GET | Stato di tutti i servizi locali |
| `/tools` | GET | Lista tools MCP disponibili |
| `/test/tts` | POST | Test sintesi vocale |
| `/test/image` | POST | Test analisi immagini |
| `/test/document` | POST | Test lettura documenti |

### Tools MCP Disponibili (12)

#### TTS (3 tools)

| Tool | Parametri | Descrizione |
|------|-----------|-------------|
| `tts_speak` | `text`, `voice=riccardo`, `backend=piper` | Sintetizza testo in audio |
| `tts_list_voices` | `backend=edge-tts` | Lista voci per backend |
| `tts_list_backends` | - | Lista backend TTS disponibili |

#### Immagini (4 tools)

| Tool | Parametri | Descrizione |
|------|-----------|-------------|
| `image_analyze` | `image_path`, `prompt`, `model=llava` | Analisi completa immagine |
| `image_describe` | `image_path` | Descrizione rapida |
| `image_extract_text` | `image_path` | OCR + Vision |
| `image_list_models` | - | Lista modelli vision |

#### Documenti (4 tools)

| Tool | Parametri | Descrizione |
|------|-----------|-------------|
| `document_read` | `file_path` | Leggi documento completo |
| `document_extract_text` | `file_path` | Estrai solo testo |
| `document_summary` | `file_path` | Riassunto documento |
| `document_formats` | - | Formati supportati |

#### Utility (1 tool)

| Tool | Descrizione |
|------|-------------|
| `check_services` | Verifica stato di tutti i servizi |

### Integrazione Claude Desktop

Aggiungi a `~/.config/claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "ollama-webui": {
      "command": "python",
      "args": ["/home/wildlux/Desktop/ollama-webui/mcp_service/mcp_service.py"]
    }
  }
}
```

### Avvio

```bash
cd mcp_service
python mcp_service.py
# oppure
./start_mcp_service.sh
```

### Test

```bash
# Stato servizi
curl http://localhost:5558/services

# Lista tools
curl http://localhost:5558/tools

# Test TTS via MCP
curl -X POST "http://localhost:5558/test/tts?text=Ciao"

# Test immagine via MCP
curl -X POST -F "file=@foto.jpg" http://localhost:5558/test/image
```

---

## 7. System Profiler - Limiti per Tier

Il sistema adatta automaticamente i timeout in base alla RAM disponibile.

### Tiers

| Tier | RAM | Descrizione |
|------|-----|-------------|
| MINIMAL | < 4 GB | Risorse critiche |
| LOW | 4 - 8 GB | Risorse limitate |
| MEDIUM | 8 - 16 GB | Risorse adeguate |
| HIGH | >= 16 GB | Risorse abbondanti |

> **Questo sistema**: ~8 GB RAM, **Tier LOW**, GPU NVIDIA presente.

### Timeout per Tier

| Operazione | MINIMAL | LOW | MEDIUM | HIGH |
|------------|---------|-----|--------|------|
| TTS | 15s | 30s | 60s | 120s |
| LLM | 30s | 60s | 120s | 300s |
| Analisi Immagini | 20s | 45s | 90s | 180s |
| Lettura Documenti | 15s | 30s | 60s | 120s |

### Limiti per Tier

| Limite | MINIMAL | LOW | MEDIUM | HIGH |
|--------|---------|-----|--------|------|
| Op. parallele max | 1 | 2 | 4 | 8 |
| Lunghezza testo TTS | 500 | 2000 | 10000 | 50000 |
| Soglia warning RAM | 70% | 75% | 80% | 85% |
| Soglia critica RAM | 85% | 90% | 92% | 95% |

### Memory Watchdog

- Intervallo controllo: ogni 2 secondi
- Blocca operazioni alla soglia critica
- Emette warning alla soglia di attenzione

---

## 8. Ordine di Avvio Consigliato

```bash
# 1. Ollama (deve essere gia installato sul sistema)
ollama serve

# 2. Docker (Open WebUI + OpenedAI Speech)
cd /home/wildlux/Desktop/ollama-webui
docker compose up -d

# 3. Servizi Python (in terminali separati o con GUI)
python image_analysis/image_service.py   # :5555
python tts_service/tts_local.py          # :5556
python document_service/document_service.py  # :5557
python mcp_service/mcp_service.py        # :5558

# Oppure tutto insieme tramite GUI:
./run_gui.sh
```

---

## 9. Verifica Rapida

```bash
# Ollama
curl http://localhost:11434/api/version

# Open WebUI
curl -s http://localhost:3000 | head -1

# Servizi locali
curl http://localhost:5555/          # Image
curl http://localhost:5556/          # TTS
curl http://localhost:5557/          # Document
curl http://localhost:5558/services  # MCP (stato di tutto)
```

---

## 10. Cache e Pulizia

| Servizio | Cartella | Scadenza | Comando pulizia |
|----------|----------|----------|-----------------|
| Immagini | `image_analysis/.image_cache/` | 24h | `curl -X DELETE http://localhost:5555/cache` |
| Documenti | `document_service/.doc_cache/` | 24h | `curl -X DELETE http://localhost:5557/cache` |
| TTS | `tts_service/.tts_cache/` | Manuale | Eliminare file manualmente |
| MCP | `mcp_service/.mcp_cache/` | Manuale | Eliminare file manualmente |
| Open WebUI | Volume Docker `open_webui_data` | Mai | `docker volume rm open_webui_data` |
