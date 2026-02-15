# API Reference

Documentazione degli endpoint REST dei 4 microservizi.

Ogni servizio espone anche la documentazione Swagger interattiva su `/docs` (es. `http://localhost:5556/docs`).

---

## TTS Local Service (:5556)

Sintesi vocale italiana offline con Piper TTS.

### `GET /`

Health check e info servizio.

```bash
curl http://localhost:5556/
```

**Risposta:** `200 OK`
```json
{
  "service": "TTS Local Service (Piper)",
  "status": "running",
  "ready": true,
  "models_installed": ["paola", "riccardo"],
  "offline": true
}
```

### `GET /voices`

Lista voci italiane disponibili.

```bash
curl http://localhost:5556/voices
```

**Risposta:** `200 OK`
```json
{
  "voices": [
    {"id": "paola", "name": "Paola", "gender": "F", "quality": "medium", "installed": true},
    {"id": "riccardo", "name": "Riccardo", "gender": "M", "quality": "x_low", "installed": true}
  ],
  "default": "paola",
  "language": "it-IT"
}
```

### `GET /voices/check`

Verifica disponibilita voci. **Chiamare sempre prima di sintetizzare.**

```bash
curl http://localhost:5556/voices/check
```

**Risposta:** `200 OK`
```json
{
  "ready": true,
  "piper_available": true,
  "voices_installed": ["paola", "riccardo"],
  "voices_missing": []
}
```

### `GET /v1/audio/speech/ready`

Preflight check per Open WebUI.

```bash
curl http://localhost:5556/v1/audio/speech/ready
```

**Risposta:** `200 OK` se pronto, `503` se non pronto.

### `POST /v1/audio/speech`

Endpoint compatibile OpenAI TTS. Usato da Open WebUI.

```bash
curl -X POST http://localhost:5556/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{"input": "Ciao mondo", "voice": "paola", "model": "tts-1"}' \
  -o audio.wav
```

| Parametro | Tipo   | Default  | Descrizione |
|-----------|--------|----------|-------------|
| `input`   | string | required | Testo da sintetizzare |
| `voice`   | string | `paola`  | Voce (paola, riccardo, o nomi OpenAI: alloy, echo, etc.) |
| `model`   | string | `tts-1`  | Ignorato, per compatibilita |
| `speed`   | float  | `1.0`    | Velocita (0.5-2.0) |

**Risposta:** `200 OK` audio/wav, `400` testo vuoto, `503` non pronto.

### `POST /speak`

Sintetizza testo in audio (form data).

```bash
curl -X POST http://localhost:5556/speak \
  -d "text=Buongiorno&voice=paola&format=wav" \
  -o speech.wav
```

| Parametro | Tipo   | Default | Descrizione |
|-----------|--------|---------|-------------|
| `text`    | string | required | Testo |
| `voice`   | string | `paola` | Voce |
| `speed`   | float  | `1.0`   | Velocita |
| `format`  | string | `wav`   | Formato (wav, mp3) |

### `POST /test`

Test rapido di una voce.

```bash
curl -X POST http://localhost:5556/test -d "voice=paola"
```

### `POST /install/{voice_id}`

Installa un modello vocale (scarica da HuggingFace).

```bash
curl -X POST http://localhost:5556/install/paola
```

### `GET /system`

Info sistema e limiti di protezione RAM.

```bash
curl http://localhost:5556/system
```

### `GET /openwebui-config`

Configurazione docker-compose per Open WebUI.

---

## Image Analysis Service (:5555)

Analisi immagini con Ollama Vision (LLaVA).

### `GET /`

Health check.

```bash
curl http://localhost:5555/
```

### `GET /models`

Lista modelli vision disponibili.

```bash
curl http://localhost:5555/models
```

**Risposta:**
```json
{
  "current_model": "llava:latest",
  "available": ["llava:latest", "qwen2.5:7b-instruct-q4_K_M"],
  "vision_capable": ["llava:latest"]
}
```

### `POST /analyze`

Analisi completa di un'immagine.

```bash
curl -X POST http://localhost:5555/analyze \
  -F "file=@immagine.png" \
  -F "analysis_type=complete"
```

| Parametro       | Tipo   | Default    | Descrizione |
|-----------------|--------|------------|-------------|
| `file`          | file   | required   | File immagine |
| `analysis_type` | string | `complete` | complete, describe, objects, text, math, diagram, code |
| `custom_prompt` | string | `""`       | Prompt personalizzato |
| `use_cache`     | bool   | `true`     | Usa cache |

### `POST /describe`

Descrizione veloce.

```bash
curl -X POST http://localhost:5555/describe -F "file=@foto.jpg"
```

### `POST /extract-text`

Estrazione testo (OCR + Vision).

```bash
curl -X POST http://localhost:5555/extract-text -F "file=@screenshot.png"
```

### `POST /analyze-math`

Analisi contenuto matematico.

```bash
curl -X POST http://localhost:5555/analyze-math -F "file=@formula.png"
```

### `POST /batch`

Analisi multipla in batch.

```bash
curl -X POST http://localhost:5555/batch \
  -F "files=@img1.png" -F "files=@img2.png" \
  -F "analysis_type=describe"
```

### `DELETE /cache`

Pulisci cache analisi.

```bash
curl -X DELETE http://localhost:5555/cache
```

---

## Document Reader Service (:5557)

Lettura documenti multi-formato (PDF, Word, Excel, 100+ estensioni).

### `GET /`

Health check con conteggio formati.

```bash
curl http://localhost:5557/
```

### `GET /formats`

Lista formati supportati con stato disponibilita.

```bash
curl http://localhost:5557/formats
```

**Risposta (estratto):**
```json
{
  ".pdf": {"name": "PDF Document", "available": true},
  ".docx": {"name": "Word Document", "available": true},
  ".xlsx": {"name": "Excel Spreadsheet", "available": true},
  ".py": {"name": "Python", "available": true}
}
```

### `POST /read`

Legge un documento e restituisce contenuto strutturato.

```bash
curl -X POST http://localhost:5557/read -F "file=@documento.pdf"
```

| Parametro   | Tipo | Default | Descrizione |
|-------------|------|---------|-------------|
| `file`      | file | required | Documento da leggere |
| `use_cache` | bool | `true`  | Usa cache |

**Risposta (PDF):**
```json
{
  "format": "PDF",
  "pages": 5,
  "metadata": {"title": "Titolo", "author": "Autore"},
  "full_text": "Contenuto testuale...",
  "filename": "documento.pdf",
  "size_kb": 245.3
}
```

### `POST /extract-text`

Estrae solo il testo (senza metadati).

```bash
curl -X POST http://localhost:5557/extract-text -F "file=@doc.docx"
```

### `POST /get-metadata`

Solo metadati (senza contenuto testuale).

```bash
curl -X POST http://localhost:5557/get-metadata -F "file=@doc.pdf"
```

### `POST /summary`

Riassunto breve del documento.

```bash
curl -X POST http://localhost:5557/summary -F "file=@doc.pdf" -F "max_chars=1000"
```

### `POST /batch`

Lettura multipla in batch.

```bash
curl -X POST http://localhost:5557/batch \
  -F "files=@doc1.pdf" -F "files=@doc2.docx"
```

### `DELETE /cache`

Pulisci cache documenti.

```bash
curl -X DELETE http://localhost:5557/cache
```

---

## MCP Bridge Service (:5558)

Bridge Model Context Protocol per Claude Desktop e client MCP.

### `GET /`

Health check con stato di tutti i servizi collegati.

```bash
curl http://localhost:5558/
```

**Risposta:**
```json
{
  "service": "MCP Bridge",
  "version": "1.0.0",
  "mcp_available": true,
  "services": {
    "tts": {"available": true, "port": 5556},
    "image": {"available": true, "port": 5555},
    "document": {"available": true, "port": 5557}
  }
}
```

### `GET /services`

Stato dettagliato dei servizi.

```bash
curl http://localhost:5558/services
```

### `GET /tools`

Lista tools MCP disponibili (12 tools).

```bash
curl http://localhost:5558/tools
```

### `POST /test/tts`

Test rapido TTS via bridge.

```bash
curl -X POST "http://localhost:5558/test/tts?text=Ciao"
```

### `POST /test/image`

Test analisi immagine via bridge.

```bash
curl -X POST "http://localhost:5558/test/image?image_path=/path/to/image.png"
```

### `POST /test/document`

Test lettura documento via bridge.

```bash
curl -X POST "http://localhost:5558/test/document?file_path=/path/to/doc.pdf"
```

---

## Codici di errore comuni

| Codice | Significato |
|--------|-------------|
| `400`  | Parametro mancante o non valido |
| `404`  | Risorsa non trovata (voce, formato) |
| `500`  | Errore interno del servizio |
| `503`  | Servizio non pronto (voci non installate, Ollama offline) |
| `504`  | Timeout (testo troppo lungo, sistema sovraccarico) |
