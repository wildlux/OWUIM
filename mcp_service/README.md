# MCP Bridge Service

Servizio **locale/LAN** che espone i servizi di Open WebUI (TTS, Image Analysis, Document) tramite API REST e protocollo MCP.

**Porta:** 5558
**100% Offline** - Nessuna connessione internet richiesta

## Architettura

```
┌─────────────────────────────────────────────────────┐
│              MCP Bridge Service (:5558)             │
│                  (API REST + MCP)                   │
├─────────────────────────────────────────────────────┤
│  TTS Tools  │  Image Tools  │  Document Tools       │
└──────┬──────┴───────┬───────┴────────┬──────────────┘
       │              │                │
       ▼              ▼                ▼
   TTS :5556    Image :5555     Document :5557
       │              │                │
       └──────────────┴────────────────┘
                      │
                      ▼
               [Ollama locale]
```

## Avvio Rapido

### Dalla GUI
1. Apri `openwebui_gui.py`
2. Vai nel tab **🔌 MCP**
3. Clicca **🚀 Avvia Servizio**

### Da terminale

**Windows:**
```batch
cd mcp_service
start_mcp_service.bat
```

**Linux/macOS:**
```bash
cd mcp_service
./start_mcp_service.sh

# Oppure con venv (consigliato per MCP SDK):
../venv/bin/python mcp_service.py
```

## Accesso LAN

Una volta avviato, il servizio è accessibile da qualsiasi dispositivo nella rete locale:

| Endpoint | URL |
|----------|-----|
| Locale | `http://localhost:5558` |
| LAN | `http://<IP-PC>:5558` |
| Swagger Docs | `http://<IP-PC>:5558/docs` |

## API REST

### Endpoints principali

| Endpoint | Metodo | Descrizione |
|----------|--------|-------------|
| `/` | GET | Health check + stato servizi |
| `/services` | GET | Stato dettagliato dei servizi |
| `/tools` | GET | Lista tools MCP disponibili |
| `/docs` | GET | Documentazione Swagger interattiva |

### Test endpoints

| Endpoint | Metodo | Descrizione |
|----------|--------|-------------|
| `/test/tts` | POST | Test sintesi vocale |
| `/test/image` | POST | Test analisi immagine |
| `/test/document` | POST | Test lettura documento |

### Esempi curl

```bash
# Health check
curl http://localhost:5558/

# Lista servizi
curl http://localhost:5558/services

# Test TTS (genera audio)
curl -X POST "http://localhost:5558/test/tts?text=Ciao%20mondo"

# Test con voce specifica
curl -X POST "http://localhost:5558/test/tts?text=Buongiorno&voice=paola"
```

## Tools Disponibili (12)

### TTS (Sintesi Vocale)

| Tool | Descrizione |
|------|-------------|
| `tts_speak` | Sintetizza testo in audio MP3 |
| `tts_list_voices` | Lista voci disponibili (riccardo, paola) |
| `tts_list_backends` | Lista backend TTS (piper, edge-tts, gtts) |

### Image Analysis

| Tool | Descrizione |
|------|-------------|
| `image_analyze` | Analisi completa con LLaVA |
| `image_describe` | Descrizione veloce |
| `image_extract_text` | OCR + Vision |
| `image_list_models` | Lista modelli vision |

### Document

| Tool | Descrizione |
|------|-------------|
| `document_read` | Legge PDF, Word, Excel, PowerPoint |
| `document_extract_text` | Estrae solo testo |
| `document_summary` | Genera riassunto |
| `document_formats` | Lista 40+ formati supportati |

### Utility

| Tool | Descrizione |
|------|-------------|
| `check_services` | Verifica stato di tutti i servizi |

## Integrazione con Open WebUI

Il bridge MCP può essere usato da Open WebUI in due modi:

### 1. Via Tools esistenti (consigliato)
I tools in `tools/` già chiamano i servizi direttamente:
- `tools/image_analyzer.py` → Image Service
- `tools/document_reader.py` → Document Service

### 2. Via API REST
Crea un nuovo tool che chiama l'API del bridge:

```python
"""
title: MCP Bridge
author: Tu
version: 1.0.0
"""
import requests

class Tools:
    def call_mcp(self, endpoint: str, params: dict = {}) -> str:
        """Chiama il bridge MCP."""
        resp = requests.post(
            f"http://localhost:5558/{endpoint}",
            params=params,
            timeout=30
        )
        return resp.json()
```

## Requisiti Sistema

### Minimi
- **RAM:** 4 GB liberi
- **CPU:** Qualsiasi (x64)
- **Disco:** 100 MB

### Consigliati (per Image Analysis)
- **RAM:** 8+ GB
- **VRAM:** 4+ GB (GPU NVIDIA)
- **Modello:** LLaVA installato in Ollama

## Dipendenze Python

```bash
pip install fastapi uvicorn requests sse-starlette

# Opzionale: MCP SDK per protocollo nativo
pip install mcp
```

## Troubleshooting

### "Servizio non raggiungibile"
1. Verifica che sia avviato: `curl http://localhost:5558/`
2. Controlla firewall: porta 5558 deve essere aperta per LAN

### "TTS non funziona"
1. Avvia TTS Service: tab Voce → Avvia Servizio
2. Scarica voci: tab Voce → Scarica Tutte

### "Image Analysis non funziona"
1. Avvia Image Service
2. Verifica Ollama: `ollama list`
3. Scarica LLaVA: `ollama pull llava`

### Porta già in uso
Modifica `SERVICE_PORT` in `mcp_service.py`:
```python
SERVICE_PORT = 5559  # Cambia porta
```

## Licenza

MIT - Parte del progetto Open WebUI Manager
