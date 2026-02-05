# Open WebUI Manager - Scheda Funzionalità

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║                                                                               ║
║     ██████╗ ██████╗ ███████╗███╗   ██╗    ██╗    ██╗███████╗██████╗           ║
║    ██╔═══██╗██╔══██╗██╔════╝████╗  ██║    ██║    ██║██╔════╝██╔══██╗          ║
║    ██║   ██║██████╔╝█████╗  ██╔██╗ ██║    ██║ █╗ ██║█████╗  ██████╔╝          ║
║    ██║   ██║██╔═══╝ ██╔══╝  ██║╚██╗██║    ██║███╗██║██╔══╝  ██╔══██╗          ║
║    ╚██████╔╝██║     ███████╗██║ ╚████║    ╚███╔███╔╝███████╗██████╔╝          ║
║     ╚═════╝ ╚═╝     ╚══════╝╚═╝  ╚═══╝     ╚══╝╚══╝ ╚══════╝╚═════╝           ║
║                                                                               ║
║                    ██╗   ██╗██╗    ███╗   ███╗ █████╗ ███╗   ██╗ █████╗       ║
║                    ██║   ██║██║    ████╗ ████║██╔══██╗████╗  ██║██╔══██╗      ║
║                    ██║   ██║██║    ██╔████╔██║███████║██╔██╗ ██║███████║      ║
║                    ██║   ██║██║    ██║╚██╔╝██║██╔══██║██║╚██╗██║██╔══██║      ║
║                    ╚██████╔╝██║    ██║ ╚═╝ ██║██║  ██║██║ ╚████║██║  ██║      ║
║                     ╚═════╝ ╚═╝    ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝      ║
║                                                                               ║
║                    ██╗  ██╗    ██████╗ ██╗     ██╗      █████╗ ███╗   ███╗    ║
║                    ╚██╗██╔╝   ██╔═══██╗██║     ██║     ██╔══██╗████╗ ████║    ║
║                     ╚███╔╝    ██║   ██║██║     ██║     ███████║██╔████╔██║    ║
║                     ██╔██╗    ██║   ██║██║     ██║     ██╔══██║██║╚██╔╝██║    ║
║                    ██╔╝ ██╗   ╚██████╔╝███████╗███████╗██║  ██║██║ ╚═╝ ██║    ║
║                    ╚═╝  ╚═╝    ╚═════╝ ╚══════╝╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝    ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

**Sistema AI locale completo basato su Open WebUI + Ollama**

---

## Indice

1. [Panoramica](#panoramica)
2. [Servizi Locali](#servizi-locali)
3. [Tools Open WebUI](#tools-open-webui)
4. [Formati Supportati](#formati-supportati)
5. [Requisiti di Sistema](#requisiti-di-sistema)
6. [Installazione](#installazione)
7. [Avvio Rapido](#avvio-rapido)
8. [API Reference](#api-reference)
9. [Crediti e Licenza](#crediti-e-licenza)

---

## Panoramica

Open WebUI Manager è una suite completa per gestire un sistema AI locale con:

| Caratteristica | Descrizione |
|----------------|-------------|
| **Interfaccia** | Open WebUI (porta 3000) - Chat moderna e intuitiva |
| **Modelli AI** | Ollama (porta 11434) - LLM locali con supporto GPU |
| **Lingua** | Italiano nativo (DEFAULT_LOCALE=it-IT) |
| **Tools** | 14 strumenti specializzati per Open WebUI |
| **Servizi** | 3 microservizi Python per TTS, immagini e documenti |
| **Piattaforme** | Windows 10/11, Linux (Ubuntu, Debian, Fedora) |

---

## Servizi Locali

### 1. TTS Service (Sintesi Vocale) - Porta 5556

Servizio per la sintesi vocale in italiano con voci naturali.

```
┌─────────────────────────────────────────────────────────────┐
│                    TTS SERVICE                               │
├─────────────────────────────────────────────────────────────┤
│  Porta: 5556                                                │
│  Backend: edge-tts, piper, gtts, openedai                   │
│  Voci italiane: 16                                          │
│  Qualità: Alta (edge-tts) / Media (piper)                   │
│  Cache: 24 ore                                              │
└─────────────────────────────────────────────────────────────┘
```

**Voci Italiane Disponibili:**

| Voce | Genere | Stile | Backend |
|------|--------|-------|---------|
| it-IT-IsabellaNeural | Femminile | Caldo, naturale | edge-tts |
| it-IT-ElsaNeural | Femminile | Standard | edge-tts |
| it-IT-DiegoNeural | Maschile | Standard | edge-tts |
| it-IT-GiuseppeNeural | Maschile | Maturo | edge-tts |
| it-IT-BenignoNeural | Maschile | Giovane | edge-tts |
| it-IT-FabiolaNeural | Femminile | Professionale | edge-tts |
| ... | ... | ... | ... |

**Endpoint API:**
- `POST /speak` - Sintetizza testo in audio MP3
- `POST /test` - Test rapido di una voce
- `GET /backends` - Lista backend disponibili
- `GET /voices/{backend}` - Lista voci per backend
- `POST /v1/audio/speech` - Compatibile OpenAI API

---

### 2. Image Analysis Service - Porta 5555

Servizio per l'analisi di immagini con modelli vision (LLaVA).

```
┌─────────────────────────────────────────────────────────────┐
│                 IMAGE ANALYSIS SERVICE                       │
├─────────────────────────────────────────────────────────────┤
│  Porta: 5555                                                │
│  Modelli: llava, bakllava, llama3.2-vision                  │
│  Formati: PNG, JPEG, GIF, WebP, SVG                         │
│  OCR: Tesseract (opzionale)                                 │
│  Cache: 24 ore                                              │
└─────────────────────────────────────────────────────────────┘
```

**Funzionalità:**
- Descrizione automatica immagini
- Estrazione testo (OCR + Vision AI)
- Analisi contenuto matematico
- Rilevamento oggetti
- Analisi diagrammi e schemi

**Endpoint API:**
- `POST /analyze` - Analisi completa
- `POST /describe` - Descrizione veloce
- `POST /extract-text` - OCR + estrazione testo
- `POST /analyze-math` - Contenuto matematico
- `POST /batch` - Analisi batch multiple immagini

---

### 3. Document Reader Service - Porta 5557

Servizio per la lettura di documenti in oltre 100 formati.

```
┌─────────────────────────────────────────────────────────────┐
│                DOCUMENT READER SERVICE                       │
├─────────────────────────────────────────────────────────────┤
│  Porta: 5557                                                │
│  Versione: 2.0.0                                            │
│  Formati: 100+                                              │
│  Max file: 50MB                                             │
│  Cache: 24 ore                                              │
│  Documentazione: http://localhost:5557/docs                 │
└─────────────────────────────────────────────────────────────┘
```

**Endpoint API:**
- `POST /read` - Legge documento completo
- `POST /extract-text` - Estrae solo testo
- `POST /get-metadata` - Solo metadati
- `POST /summary` - Riassunto breve
- `POST /batch` - Lettura batch
- `GET /formats` - Lista formati supportati

---

## Tools Open WebUI

14 strumenti specializzati integrati in Open WebUI:

### Strumenti Principali

| Tool | Descrizione | Funzionalità |
|------|-------------|--------------|
| **Scientific Council** | Concilio multi-LLM | Consulta 3-5 modelli in parallelo, votazione pesata |
| **Math Assistant** | Assistente matematico | Algebra, calcolo, grafici, LaTeX |
| **Code Assistant** | Assistente codice | Debug, review, documentazione |
| **Study Assistant** | Assistente studio | Quiz, riassunti, spiegazioni |
| **Research Assistant** | Assistente ricerca | Paper, analisi, sintesi |

### Strumenti Creativi

| Tool | Descrizione | Funzionalità |
|------|-------------|--------------|
| **Creative Writing** | Scrittura creativa | Storie, poesie, dialoghi |
| **Book Assistant** | Assistente libri | Outline, capitoli, editing |
| **Book Publishing** | Pubblicazione | Formatting, metadata, export |
| **Text Assistant** | Assistente testo | Traduzioni, parafrasatura |

### Strumenti Pratici

| Tool | Descrizione | Funzionalità |
|------|-------------|--------------|
| **Productivity Assistant** | Produttività | Task, email, planning |
| **Finance Italian** | Finanza italiana | Budget, tasse, investimenti |
| **Image Handler** | Gestione immagini | Salvataggio, conversione |
| **Image Analyzer** | Analisi immagini | Connessione al servizio locale |
| **Document Reader** | Lettura documenti | Connessione al servizio locale |
| **MEGA Assistant** | Tool integrato | Combina tutti gli strumenti |

---

## Formati Supportati

### Documenti Office

| Formato | Estensione | Libreria |
|---------|------------|----------|
| PDF | .pdf | pypdf |
| Word | .docx, .doc | python-docx, LibreOffice |
| Excel | .xlsx, .xls | openpyxl, LibreOffice |
| PowerPoint | .pptx, .ppt | python-pptx, LibreOffice |
| Rich Text | .rtf | LibreOffice |

### LibreOffice / OpenDocument

| Formato | Estensione |
|---------|------------|
| OpenDocument Text | .odt |
| OpenDocument Spreadsheet | .ods |
| OpenDocument Presentation | .odp |
| OpenDocument Graphics | .odg |
| OpenDocument Formula | .odf |
| OpenDocument Database | .odb |

### E-book

| Formato | Estensione | Libreria |
|---------|------------|----------|
| EPUB | .epub | ebooklib |
| Kindle | .mobi, .azw, .azw3 | Calibre |
| FictionBook | .fb2 | Calibre |

### Immagini - Editor Grafici

| Formato | Estensione | Programma |
|---------|------------|-----------|
| GIMP | .xcf | GIMP / ImageMagick |
| Photoshop | .psd, .psb | GIMP / ImageMagick |
| OpenRaster | .ora | GIMP / ImageMagick |
| Krita | .kra | GIMP / ImageMagick |
| Adobe Illustrator | .ai | GIMP / ImageMagick |

### Immagini - Standard

| Formato | Estensione |
|---------|------------|
| PNG | .png |
| JPEG | .jpg, .jpeg |
| GIF | .gif |
| BMP | .bmp |
| TIFF | .tiff, .tif |
| WebP | .webp |
| ICO | .ico |
| SVG | .svg, .svgz |

### Immagini - RAW (Fotocamere)

| Marca | Estensione |
|-------|------------|
| Canon | .cr2, .cr3 |
| Nikon | .nef, .nrw |
| Sony | .arw |
| Olympus | .orf |
| Panasonic | .rw2 |
| Pentax | .pef |
| Fujifilm | .raf |
| Digital Negative | .dng |

### Testo e Markup

| Formato | Estensione |
|---------|------------|
| Plain Text | .txt |
| Markdown | .md |
| CSV/TSV | .csv, .tsv |
| JSON | .json |
| XML | .xml |
| HTML | .html, .htm |
| YAML | .yaml, .yml |
| LaTeX | .tex |

### Codice Sorgente (60+ linguaggi)

Python, JavaScript, TypeScript, Java, Kotlin, C, C++, C#, Go, Rust, Ruby, PHP, Swift, R, SQL, Shell, PowerShell, Vue.js, Svelte, CSS, SCSS, Lua, Dart, Scala, Haskell, Elixir, Erlang, Clojure, Perl, Dockerfile, Terraform, GraphQL, e molti altri.

---

## Requisiti di Sistema

### Minimi

| Componente | Requisito |
|------------|-----------|
| OS | Windows 10/11 o Linux (Ubuntu 20.04+) |
| CPU | 4 core |
| RAM | 8 GB |
| Spazio | 20 GB |
| Python | 3.8+ |

### Consigliati

| Componente | Requisito |
|------------|-----------|
| CPU | 8+ core |
| RAM | 16+ GB |
| GPU | NVIDIA con 8+ GB VRAM |
| Spazio | 50+ GB |

### Software Richiesto

| Software | Obbligatorio | Note |
|----------|--------------|------|
| Docker | Sì | Per Open WebUI |
| Ollama | Sì | Per modelli LLM |
| Python 3.8+ | Sì | Per servizi locali |
| LibreOffice | Opzionale | Per documenti legacy |
| GIMP/ImageMagick | Opzionale | Per immagini XCF/PSD |
| Calibre | Opzionale | Per e-book |

---

## Installazione

### 1. Clona il repository

```bash
git clone <repository-url>
cd ollama-webui
```

### 2. Installa dipendenze Python

```bash
# Crea virtual environment
python3 -m venv venv

# Attiva (Linux/macOS)
source venv/bin/activate

# Attiva (Windows)
venv\Scripts\activate

# Installa dipendenze
pip install -r requirements.txt
```

### 3. Installa Ollama

```bash
# Linux
curl -fsSL https://ollama.com/install.sh | sh

# Scarica un modello
ollama pull qwen2.5:7b-instruct-q4_K_M
ollama pull llava  # Per analisi immagini
```

### 4. Avvia Docker

```bash
docker compose up -d
```

---

## Avvio Rapido

### Windows - Doppio Click

```
scripts/OpenWebUI.bat      → Avvia tutto (Docker + Ollama + Open WebUI)
OpenWebUI.vbs      → Come sopra, senza finestra nera
```

### Linux

```bash
chmod +x *.sh
./scripts/start_all.sh     # Avvia tutto
```

### Avvio Servizi Singoli

```bash
# Attiva venv
source venv/bin/activate

# TTS Service (porta 5556)
cd tts_service && python tts_service.py

# Image Analysis (porta 5555)
cd image_analysis && python image_service.py

# Document Reader (porta 5557)
cd document_service && python document_service.py
```

---

## API Reference

### Document Reader Service

**Base URL:** `http://localhost:5557`

#### Lettura Documento

```bash
curl -X POST -F "file=@documento.pdf" http://localhost:5557/read
```

**Response:**
```json
{
  "format": "PDF",
  "pages": 10,
  "metadata": {"title": "...", "author": "..."},
  "full_text": "Contenuto del documento...",
  "filename": "documento.pdf",
  "size_kb": 245.5
}
```

#### Estrazione Testo

```bash
curl -X POST -F "file=@documento.docx" http://localhost:5557/extract-text
```

### TTS Service

**Base URL:** `http://localhost:5556`

#### Sintesi Vocale

```bash
curl -X POST -d "text=Ciao mondo" -d "voice=it-IT-IsabellaNeural" \
     http://localhost:5556/speak -o audio.mp3
```

### Image Analysis Service

**Base URL:** `http://localhost:5555`

#### Analisi Immagine

```bash
curl -X POST -F "file=@immagine.png" http://localhost:5555/analyze
```

---

## Architettura

```
┌─────────────────────────────────────────────────────────────────┐
│                         UTENTE                                   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    OPEN WEBUI (:3000)                            │
│              Interfaccia chat moderna                            │
│                    14 Tools integrati                            │
└─────────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              │               │               │
              ▼               ▼               ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│  TTS SERVICE    │ │ IMAGE SERVICE   │ │ DOCUMENT SVC    │
│    (:5556)      │ │    (:5555)      │ │    (:5557)      │
│                 │ │                 │ │                 │
│ - edge-tts      │ │ - LLaVA         │ │ - PDF           │
│ - piper         │ │ - OCR           │ │ - Word          │
│ - gtts          │ │ - SVG→PNG       │ │ - Excel         │
│ - 16 voci IT    │ │                 │ │ - 100+ formati  │
└─────────────────┘ └─────────────────┘ └─────────────────┘
              │               │               │
              └───────────────┼───────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      OLLAMA (:11434)                             │
│                   Modelli LLM locali                             │
│         qwen2.5, llama3, mistral, codellama, llava...           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         GPU NVIDIA                               │
│                    Accelerazione CUDA                            │
└─────────────────────────────────────────────────────────────────┘
```

---

## Troubleshooting

### Problema: "python-multipart not installed"
```bash
pip install python-multipart
```

### Problema: "LibreOffice non trovato"
```bash
# Linux
sudo apt install libreoffice

# Windows
winget install TheDocumentFoundation.LibreOffice
```

### Problema: "Ollama non raggiungibile"
```bash
# Verifica che Ollama sia in esecuzione
ollama serve

# Controlla lo stato
curl http://localhost:11434/api/tags
```

### Problema: "Docker non parte"
```bash
# Linux
sudo systemctl start docker

# Windows
# Avvia Docker Desktop
```

---

## Changelog

### Versione 2.0.0 (Gennaio 2026)

- **Nuovo:** Document Reader Service con 100+ formati
- **Nuovo:** Supporto completo formati GIMP e LibreOffice
- **Nuovo:** Supporto immagini RAW da fotocamere
- **Nuovo:** Supporto e-book (EPUB, MOBI, AZW)
- **Migliorato:** Codice completamente documentato
- **Migliorato:** Type hints su tutti i metodi
- **Migliorato:** Script avvio con installazione automatica dipendenze

### Versione 1.0.0

- Release iniziale
- TTS Service con 4 backend
- Image Analysis Service
- 14 Tools per Open WebUI
- Scientific Council multi-LLM

---

## Crediti e Licenza

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║                                                                               ║
║                           DIRITTO D'AUTORE                                    ║
║                                                                               ║
║  ┌─────────────────────────────────────────────────────────────────────────┐  ║
║  │                                                                         │  ║
║  │   Questo software è stato creato da:                                    │  ║
║  │                                                                         │  ║
║  │   ███████╗ Paolo Lo Bello                                               │  ║
║  │   ██╔══██║ Ideatore e sviluppatore principale                           │  ║
║  │   ██████╔╝                                                              │  ║
║  │   ██╔═══╝                                                               │  ║
║  │   ██║                                                                   │  ║
║  │   ╚═╝                                                                   │  ║
║  │                                                                         │  ║
║  │   ██████╗  Claudio                                                      │  ║
║  │   ██╔════╝ Co-sviluppatore e collaboratore                              │  ║
║  │   ██║                                                                   │  ║
║  │   ██║                                                                   │  ║
║  │   ╚██████╗                                                              │  ║
║  │    ╚═════╝                                                              │  ║
║  │                                                                         │  ║
║  │   ██████╗ Claude Code (Anthropic)                                       │  ║
║  │   ██╔════╝ Assistente AI per sviluppo e documentazione                  │  ║
║  │   ██║      Powered by Claude Opus 4.5                                   │  ║
║  │   ██║                                                                   │  ║
║  │   ╚██████╗                                                              │  ║
║  │    ╚═════╝                                                              │  ║
║  │                                                                         │  ║
║  └─────────────────────────────────────────────────────────────────────────┘  ║
║                                                                               ║
║  Copyright (c) 2024-2026 Paolo Lo Bello, Claudio                              ║
║                                                                               ║
║  Con il contributo di Claude Code (Anthropic)                                 ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

### Licenza

Questo progetto è distribuito sotto licenza **MIT**.

```
MIT License

Copyright (c) 2024-2026 Paolo Lo Bello, Claudio

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

### Ringraziamenti

- **Open WebUI Team** - Per l'interfaccia chat eccezionale
- **Ollama Team** - Per rendere i LLM accessibili localmente
- **Microsoft** - Per edge-tts e le voci neurali italiane
- **Anthropic** - Per Claude Code e l'assistenza allo sviluppo

---

## Contatti

Per segnalazioni, suggerimenti o contributi:

- **Repository:** [GitHub]
- **Documentazione:** Questo file e i README nelle sottocartelle
- **API Docs:** http://localhost:5557/docs (quando il servizio è attivo)

---

<div align="center">

**Fatto con ❤️ in Italia**

*Paolo Lo Bello • Claudio • Claude Code*

</div>
