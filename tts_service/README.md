# TTS Service - Sintesi Vocale Italiana

Servizio locale per sintesi vocale con supporto per voci italiane di alta qualità.
Risolve i problemi di configurazione TTS in Open WebUI.

## Struttura

```
tts_service/
├── tts_service.py          # Servizio FastAPI (:5556)
├── start_tts_service.bat   # Avvia (Windows)
├── start_tts_service.sh    # Avvia (Linux)
└── README.md               # Questo file
```

## Avvio Rapido

### Windows
```batch
start_tts_service.bat
```

### Linux
```bash
chmod +x start_tts_service.sh
./start_tts_service.sh
```

## Requisiti

```bash
# Base
pip install fastapi uvicorn requests

# Backend TTS (almeno uno)
pip install edge-tts      # Consigliato - Microsoft Edge TTS
pip install gtts          # Google TTS
```

## Backend Disponibili

| Backend | Qualità | Offline | Note |
|---------|---------|---------|------|
| **edge-tts** | Alta | No | Microsoft Edge, molte voci italiane |
| gtts | Media | No | Google TTS, semplice |
| piper | Media | Sì | Richiede installazione separata |
| openedai | Media | Sì | Container Docker già configurato |

## Voci Italiane (edge-tts)

| Voce | Genere | Stile |
|------|--------|-------|
| it-IT-IsabellaNeural | F | Caldo, naturale |
| it-IT-ElsaNeural | F | Standard |
| it-IT-DiegoNeural | M | Standard |
| it-IT-GiuseppeNeural | M | Maturo |
| it-IT-BenignoNeural | M | Giovane |

## API Endpoints

Il servizio gira su `http://localhost:5556`

| Endpoint | Metodo | Descrizione |
|----------|--------|-------------|
| `/` | GET | Health check |
| `/speak` | POST | Sintetizza testo → audio MP3 |
| `/test` | POST | Test rapido voce |
| `/test-audio` | GET | Ascolta ultimo test |
| `/backends` | GET | Lista backend disponibili |
| `/voices/{backend}` | GET | Voci per backend |
| `/openwebui-config` | GET | Config consigliata per Open WebUI |
| `/v1/audio/speech` | POST | Endpoint compatibile OpenAI |

## Esempi

### Test voce
```bash
curl -X POST -d "backend=edge-tts&voice=it-IT-IsabellaNeural" \
     http://localhost:5556/test
```

### Sintetizza testo
```bash
curl -X POST -d "text=Ciao, come stai?&voice=it-IT-IsabellaNeural" \
     http://localhost:5556/speak -o output.mp3
```

### Ottieni config per Open WebUI
```bash
curl http://localhost:5556/openwebui-config
```

## Configurazione Open WebUI

1. Avvia il servizio TTS
2. Visita `http://localhost:5556/openwebui-config`
3. Copia le variabili nel `docker-compose.yml`:

```yaml
environment:
  - AUDIO_TTS_ENGINE=openai
  - AUDIO_TTS_OPENAI_API_BASE_URL=http://host.docker.internal:5556/v1
  - AUDIO_TTS_OPENAI_API_KEY=sk-not-needed
  - AUDIO_TTS_MODEL=tts-1
  - AUDIO_TTS_VOICE=it-IT-IsabellaNeural
```

4. Riavvia Open WebUI:
```bash
docker compose down && docker compose up -d
```

## Risoluzione Problemi

### "edge-tts non funziona"
```bash
pip install --upgrade edge-tts
```

### "Nessun audio"
1. Verifica che il servizio sia attivo: `curl http://localhost:5556/`
2. Testa una voce: visita `http://localhost:5556/test`
3. Controlla i log del servizio

### "Open WebUI non usa le voci italiane"
1. Verifica la configurazione in docker-compose.yml
2. Assicurati che `host.docker.internal` funzioni (Windows/Mac)
3. Su Linux usa l'IP della macchina invece di `host.docker.internal`
