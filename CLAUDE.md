# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Panoramica

Sistema AI locale basato su **Open WebUI + Ollama** con 14 tools specializzati, Scientific Council (multi-LLM), localizzazione italiana.

**Stack:** Docker, Open WebUI (:3000), Ollama (:11434), Python 3.8+, PyQt5

## Struttura

```
ollama-webui/
├── windows/                 # Setup Windows (dual-mode)
│   ├── openwebui.bat        # Gestore unificato (start/stop/install/status)
│   └── wsl_fix.bat          # Risoluzione problemi WSL2/Docker
├── linux/                   # Setup Linux (Docker nativo)
│   └── openwebui.sh         # Gestore unificato
├── tools/                   # 14 tools Python per Open WebUI
│   ├── image_handler.py     # Gestione immagini (evita bug base64)
│   ├── image_analyzer.py    # Analisi immagini via servizio locale
│   └── document_reader.py   # Lettura documenti via servizio locale
├── image_analysis/          # Servizio analisi immagini
│   ├── image_service.py     # Servizio FastAPI (:5555)
│   ├── image_converter.py   # Convertitore PNG/SVG
│   ├── start_image_service.bat  # Avvia (Windows)
│   ├── start_image_service.sh   # Avvia (Linux)
│   └── README.md            # Documentazione
├── tts_service/             # Servizio sintesi vocale
│   ├── tts_service.py       # Servizio FastAPI (:5556)
│   ├── start_tts_service.bat    # Avvia (Windows)
│   ├── start_tts_service.sh     # Avvia (Linux)
│   └── README.md            # Documentazione
├── document_service/        # Servizio lettura documenti
│   ├── document_service.py  # Servizio FastAPI (:5557)
│   ├── start_document_service.bat  # Avvia (Windows)
│   ├── start_document_service.sh   # Avvia (Linux)
│   └── README.md            # Documentazione
├── scripts/                 # Script gestione (install_tools, backup, LAN)
├── docs/                    # Documentazione
├── ICONA/                   # Icone applicazione
├── installer/               # Script Inno Setup per installer Windows
├── docker-compose.yml       # Config Docker
├── openwebui_gui.py         # GUI desktop PyQt5 (auto-start + Image Converter)
├── openwebui_gui_lite.py    # GUI leggera Tkinter
├── OpenWebUI.bat            # Doppio click -> avvia tutto
├── OpenWebUI.vbs            # Launcher silenzioso (no finestra nera)
├── build.py                 # Build eseguibile (auto-venv)
├── build_exe.bat            # Doppio click -> crea .exe
└── build_installer.bat      # Doppio click -> crea installer .exe
```

## Avvio Rapido

### Windows - Doppio Click
```
OpenWebUI.bat            -> Avvia tutto (Docker + Ollama + Open WebUI)
OpenWebUI.vbs            -> Come sopra, senza finestra nera
```

### Windows - GUI
```batch
run_gui.bat              :: GUI completa con auto-start
run_gui_lite.bat         :: GUI leggera (Tkinter)
```

### Linux
```bash
chmod +x *.sh
./start_all.sh           # Avvia tutto
./run_gui.sh             # GUI completa (PyQt5)
```

## Build e Distribuzione

### Creare .exe standalone
```batch
build_exe.bat            :: Crea dist\OpenWebUI-Manager.exe
```

### Creare Installer Windows (.exe setup)
```batch
build_installer.bat      :: Crea dist\OpenWebUI-Manager-Setup-X.X.X.exe
```

Requisiti per il build:
- Python 3.8+
- Inno Setup 6 (per installer): https://jrsoftware.org/isdl.php

## Setup Ambiente Python

### Windows
```batch
setup_env.bat                :: Crea venv e installa dipendenze
```

### Linux
```bash
./setup_env.sh               # Crea venv e installa dipendenze
```

## Comandi Manuali

### Windows
```batch
windows\openwebui.bat              :: Menu interattivo
windows\openwebui.bat start        :: Avvia (try Docker -> fallback Python)
windows\openwebui.bat stop         :: Ferma
```

### Linux
```bash
linux/openwebui.sh start           # Avvia
linux/openwebui.sh stop            # Ferma
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

`tools/scientific_council.py` - Consulta 3-5 LLM in parallelo con votazione pesata.

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

**Tool Open WebUI:** `tools/image_analyzer.py`

### Soluzione 2: Conversione Immagini

**GUI (tab Immagini):** Drag & drop per convertire PNG/SVG

**CLI:**
```bash
convert_image.bat          # Windows
./convert_image.sh         # Linux
python image_converter.py immagine.png -f base64
```

**Tool Open WebUI:** `tools/image_handler.py`

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

**Tool Open WebUI:** `tools/document_reader.py`

## Note

- Windows: Docker (*****  :3000) o Python fallback (***  :8080)
- Linux: Docker nativo (:3000)
- Lingua: Italiano (`DEFAULT_LOCALE=it-IT`)
- Ollama su host (non container) per GPU
- GUI Lite: Non richiede venv (usa solo libreria standard)
- GUI Completa: Richiede venv con PyQt5
- build.py: Crea automaticamente venv se non esiste
- Installer: Richiede Inno Setup 6
- Conversione immagini: Richiede Pillow (incluso in requirements.txt)
