# Image Analysis Service

Servizio locale per analizzare immagini e restituire descrizioni testuali.
Risolve il bug del loop ciclico di Open WebUI con immagini base64.

## Struttura

```
image_analysis/
├── image_service.py        # Servizio FastAPI (:5555)
├── image_converter.py      # Convertitore PNG/SVG standalone
├── start_image_service.bat # Avvia servizio (Windows)
├── start_image_service.sh  # Avvia servizio (Linux)
├── convert_image.bat       # Converti immagini (Windows)
├── convert_image.sh        # Converti immagini (Linux)
└── README.md               # Questo file
```

## Avvio Rapido

### Windows
```batch
start_image_service.bat
```

### Linux
```bash
chmod +x *.sh
./start_image_service.sh
```

## Requisiti

```bash
# Dipendenze Python
pip install fastapi uvicorn Pillow requests python-multipart

# Modello Vision per Ollama
ollama pull llava
```

## API Endpoints

Il servizio gira su `http://localhost:5555`

| Endpoint | Metodo | Descrizione |
|----------|--------|-------------|
| `/` | GET | Health check e info |
| `/analyze` | POST | Analisi completa immagine |
| `/describe` | POST | Descrizione veloce |
| `/extract-text` | POST | Estrai testo (OCR + Vision) |
| `/analyze-math` | POST | Analisi contenuto matematico |
| `/models` | GET | Lista modelli disponibili |
| `/cache` | DELETE | Pulisci cache |

## Esempi

### Analizza immagine
```bash
curl -X POST -F "file=@immagine.png" http://localhost:5555/analyze
```

### Descrizione veloce
```bash
curl -X POST -F "file=@immagine.png" http://localhost:5555/describe
```

### Estrai testo
```bash
curl -X POST -F "file=@screenshot.png" http://localhost:5555/extract-text
```

### Analisi matematica
```bash
curl -X POST -F "file=@grafico.png" http://localhost:5555/analyze-math
```

## Tool Open WebUI

Installa il tool `Tools OWUI/image_analyzer.py` in Open WebUI per usare il servizio direttamente dalla chat.

Metodi disponibili:
- `analyze_image_file(path)` - Analizza file locale
- `analyze_image_url(url)` - Analizza da URL
- `analyze_math_image(base64)` - Analisi matematica
- `extract_text_from_image(base64)` - Estrai testo
- `get_service_status()` - Verifica stato servizio
