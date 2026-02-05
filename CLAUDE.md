# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Panoramica

Sistema AI locale basato su **Open WebUI + Ollama** con 14 tools specializzati, Scientific Council (multi-LLM), localizzazione italiana.

**Stack:** Docker, Open WebUI (:3000), Ollama (:11434), Python 3.8+, PyQt5

## Struttura

```
ollama-webui/
├── openwebui_gui.py         # GUI principale (PyQt5)
├── openwebui_gui_lite.py    # GUI leggera (Tkinter)
├── run_gui.sh / .bat        # Launcher GUI
├── run_gui_lite.sh / .bat   # Launcher GUI lite
├── docker-compose.yml       # Config Docker
├── requirements.txt         # Dipendenze Python
│
├── Tools OWUI/              # 14 tools Python per Open WebUI
├── scripts/                 # Cassetta attrezzi (setup, backup, build, etc.)
├── docs/                    # Documentazione
├── ICONA/                   # Icone + screenshots
├── dist/                    # Build output + installer
│
├── image_analysis/          # Servizio analisi immagini (:5555)
├── document_service/        # Servizio lettura documenti (:5557)
├── tts_service/             # Servizio sintesi vocale (:5556)
└── mcp_service/             # Servizio MCP Bridge (:5558)
```

## Avvio Rapido

### GUI (Consigliato)
```bash
# Linux
./run_gui.sh

# Windows
run_gui.bat
```

### Versione Lite (Tkinter, no dipendenze)
```bash
# Linux
./run_gui_lite.sh

# Windows
run_gui_lite.bat
```

## Build e Distribuzione

```bash
# Dalla cartella dist/
python build.py              # Crea eseguibile
```

## Setup Ambiente Python

```bash
# Linux
./scripts/setup_env.sh

# Windows
scripts\setup_env.bat
```

## Comandi Manuali

```bash
# Linux
./scripts/start_all.sh       # Avvia tutti i servizi
./scripts/stop_all.sh        # Ferma tutti i servizi

# Windows
scripts\start_all.bat
scripts\stop_all.bat
```

### Tools
```bash
python3 scripts/install_tools.py   # Installa tools in Open WebUI
ollama pull qwen2.5:7b-instruct-q4_K_M  # Scarica modello
```

## Tools Pattern

```python
"""
title: Nome Tool
author: Carlo
version: 1.0.0
description: Descrizione
"""
from pydantic import BaseModel, Field

class Tools:
    def metodo(self, param: str = Field(..., description="...")) -> str:
        return risultato
```

## Scientific Council

`Tools OWUI/scientific_council.py` - Consulta 3-5 LLM in parallelo con votazione pesata.

- `OllamaCouncil` con `ThreadPoolExecutor`
- Domini: matematica, codice, italiano, sicurezza, generale
- Metodi: `consult_council()`, `generate_latex_formula()`, `verify_proof()`, `plot_mathematical()`

## Docker + Ollama

Il `docker-compose.yml` e' configurato per comunicare con Ollama installato sul sistema host:
- `OLLAMA_BASE_URL=http://host.docker.internal:11434`
- `extra_hosts: host.docker.internal:host-gateway`

Ollama deve essere installato e in esecuzione sul sistema (non in container) per sfruttare la GPU.

## Gestione Immagini

Open WebUI ha un bug noto con immagini base64 troppo grandi (causa loop ciclico).

### Soluzione 1: Image Analysis Service (Consigliata)

Servizio locale che analizza immagini e restituisce **solo testo/JSON**, evitando completamente il problema base64.

```bash
# Avvia servizio (porta 5555) - dalla cartella image_analysis/
cd image_analysis
start_image_service.bat    # Windows
./start_image_service.sh   # Linux

# Requisiti
pip install fastapi uvicorn Pillow requests
ollama pull llava          # Modello vision
```

**Architettura:**
```
[Immagine] → [Image Service :5555] → [JSON/Testo] → [Open WebUI]
                    ↓
            [Ollama LLaVA]
```

**API Endpoints:**
- `POST /analyze` - Analisi completa
- `POST /describe` - Descrizione veloce
- `POST /extract-text` - OCR + Vision
- `POST /analyze-math` - Contenuto matematico

**Tool Open WebUI:** `Tools OWUI/image_analyzer.py`

### Soluzione 2: Conversione Immagini

**GUI (tab Immagini):** Drag & drop per convertire PNG/SVG

**CLI:**
```bash
convert_image.bat          # Windows
./convert_image.sh         # Linux
python image_converter.py immagine.png -f base64
```

**Tool Open WebUI:** `Tools OWUI/image_handler.py`

### Limiti Open WebUI
- Base64 max ~40.000 caratteri
- SVG non supportato (convertire in PNG)
- Immagini grandi causano loop

## Sintesi Vocale (TTS)

Servizio locale per sintesi vocale italiana OFFLINE con Piper TTS.

### Download Voci (Prima Installazione)

```bash
# Scarica Piper + voci italiane (~75 MB totali)
cd tts_service
./download_voices.sh     # Linux
download_voices.bat      # Windows

# Oppure dalla GUI: Tab Voce -> "Scarica Tutte le Voci"
```

### Avvio Servizio

```bash
cd tts_service
./start_tts_service.sh   # Linux
start_tts_service.bat    # Windows

# Requisiti
pip install fastapi uvicorn requests
```

### Voci Italiane Disponibili (edge-tts)

| Voce | Genere | Stile |
|------|--------|-------|
| it-IT-IsabellaNeural | F | Naturale, caldo |
| it-IT-ElsaNeural | F | Standard |
| it-IT-DiegoNeural | M | Standard |
| it-IT-GiuseppeNeural | M | Maturo |

### Configurazione Open WebUI

Aggiungi al `docker-compose.yml`:

```yaml
environment:
  - AUDIO_TTS_ENGINE=openai
  - AUDIO_TTS_OPENAI_API_BASE_URL=http://host.docker.internal:5556/v1
  - AUDIO_TTS_OPENAI_API_KEY=sk-not-needed
  - AUDIO_TTS_MODEL=tts-1
  - AUDIO_TTS_VOICE=it-IT-IsabellaNeural
```

### Test

```bash
# Test voce
curl -X POST -d "text=Ciao mondo" http://localhost:5556/test

# Genera audio
curl -X POST -d "text=Buongiorno" http://localhost:5556/speak -o audio.mp3
```

## Lettura Documenti

Servizio locale per leggere PDF, Word, Excel, PowerPoint e altri formati.

### Avvio

```bash
# Dalla cartella document_service/
cd document_service
start_document_service.bat    # Windows
./start_document_service.sh   # Linux

# Requisiti
pip install fastapi uvicorn python-multipart pypdf python-docx openpyxl python-pptx
```

### Formati Supportati

| Formato | Estensione | Dipendenza |
|---------|------------|------------|
| PDF | .pdf | pypdf |
| Word | .docx | python-docx |
| Excel | .xlsx | openpyxl |
| PowerPoint | .pptx | python-pptx |
| Testo | .txt, .md, .csv, .json | - |
| LibreOffice | .odt, .ods, .odp | LibreOffice |

### API Endpoints

- `POST /read` - Legge documento completo
- `POST /extract-text` - Estrae solo testo
- `POST /get-metadata` - Solo metadati
- `POST /summary` - Riassunto breve
- `GET /formats` - Formati supportati

### Test

```bash
# Leggi PDF
curl -X POST -F "file=@documento.pdf" http://localhost:5557/read

# Estrai testo da Word
curl -X POST -F "file=@documento.docx" http://localhost:5557/extract-text
```

**Tool Open WebUI:** `Tools OWUI/document_reader.py`

## MCP Bridge Service

Servizio che espone i servizi locali (TTS, Image, Document) tramite **Model Context Protocol (MCP)**.

### Avvio

```bash
# Dalla cartella mcp_service/
cd mcp_service
start_mcp_service.bat    # Windows
./start_mcp_service.sh   # Linux

# Requisiti
pip install fastapi uvicorn requests sse-starlette
pip install mcp  # Opzionale, per protocollo MCP nativo
```

### Architettura

```
┌─────────────────────────────────────────────────────┐
│              MCP Bridge Service (:5558)             │
├─────────────────────────────────────────────────────┤
│  TTS Tools  │  Image Tools  │  Document Tools       │
└──────┬──────┴───────┬───────┴────────┬──────────────┘
       │              │                │
       ▼              ▼                ▼
   TTS :5556    Image :5555     Document :5557
```

### Tools MCP Disponibili

| Categoria | Tools |
|-----------|-------|
| TTS | `tts_speak`, `tts_list_voices`, `tts_list_backends` |
| Image | `image_analyze`, `image_describe`, `image_extract_text`, `image_list_models` |
| Document | `document_read`, `document_extract_text`, `document_summary`, `document_formats` |
| Utility | `check_services` |

### Integrazione Claude Desktop

Aggiungi al file `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "ollama-webui": {
      "command": "python",
      "args": ["/percorso/mcp_service/mcp_service.py"]
    }
  }
}
```

### Test

```bash
# Health check
curl http://localhost:5558/

# Lista tools
curl http://localhost:5558/tools

# Test TTS
curl -X POST "http://localhost:5558/test/tts?text=Ciao"
```

## Note

- Windows: Docker (*****  :3000) o Python fallback (***  :8080)
- Linux: Docker nativo (:3000)
- Lingua: Italiano (`DEFAULT_LOCALE=it-IT`)
- Ollama su host (non container) per GPU
- GUI Lite: Non richiede venv (usa solo libreria standard)
- GUI Completa: Richiede venv con PyQt5
- dist/build.py: Crea automaticamente venv se non esiste
- dist/installer/: Script Inno Setup per Windows
- Conversione immagini: Richiede Pillow (incluso in requirements.txt)
