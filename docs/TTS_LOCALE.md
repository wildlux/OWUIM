# Text-to-Speech (TTS) Locale

Guida alla configurazione del sistema TTS locale con OpenedAI Speech + Piper.

## Panoramica

Il sistema usa **OpenedAI Speech**, un container Docker che fornisce TTS locale usando **Piper** come motore vocale.

- **100% locale** - nessun dato inviato a server esterni
- **Gratuito** - nessuna API key richiesta
- **Veloce** - sintesi vocale in tempo reale
- **Multilingua** - supporto italiano e altre lingue

## Architettura

```
┌─────────────────┐     API call      ┌───────────────────┐
│   Open WebUI    │ ───────────────── │  OpenedAI Speech  │
│   (porta 3000)  │                   │   (porta 8000)    │
└─────────────────┘                   └───────────────────┘
                                              │
                                              ▼
                                      ┌───────────────┐
                                      │   Piper TTS   │
                                      │ (motore vocale)│
                                      └───────────────┘
```

## Avvio

I servizi si avviano automaticamente con Docker Compose:

```bash
docker compose up -d
```

Verifica che entrambi i container siano attivi:

```bash
docker compose ps
```

Output atteso:
```
NAME              STATUS    PORTS
open-webui        Up        0.0.0.0:3000->8080/tcp
openedai-speech   Up        0.0.0.0:8000->8000/tcp
```

## Configurazione Open WebUI

### Passo 1: Accedi alle impostazioni

1. Vai su `http://localhost:3000`
2. Clicca sull'icona ingranaggio (Settings)
3. Vai in **Admin Settings** → **Audio**

### Passo 2: Configura Text-to-Speech

Nella sezione **Text-to-Speech**, imposta:

| Campo | Valore |
|-------|--------|
| **TTS Engine** | `OpenAI` |
| **API Base URL** | `http://openedai-speech:8000/v1` |
| **API Key** | `sk-111111111` (valore fittizio, richiesto ma non usato) |
| **Model** | `tts-1` |
| **Voice** | `alloy` |

### Passo 3: Salva e testa

1. Clicca **Save**
2. Torna alla chat
3. Invia un messaggio e clicca sull'icona altoparlante per ascoltare

## Voci disponibili

OpenedAI Speech supporta queste voci di default:

| Voice | Descrizione |
|-------|-------------|
| `alloy` | Voce neutra, versatile |
| `echo` | Voce maschile |
| `fable` | Voce narrativa |
| `onyx` | Voce maschile profonda |
| `nova` | Voce femminile |
| `shimmer` | Voce femminile morbida |

## Aggiungere voci italiane

Per aggiungere voci italiane Piper:

### 1. Scarica una voce italiana

```bash
# Entra nel container
docker exec -it openedai-speech bash

# Scarica voce italiana (esempio: Paola)
cd /app/voices
wget https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/it/it_IT/paola/medium/it_IT-paola-medium.onnx
wget https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/it/it_IT/paola/medium/it_IT-paola-medium.onnx.json
```

### 2. Configura la voce

Modifica il file di configurazione delle voci nel container o monta un volume con la configurazione personalizzata.

### Voci italiane disponibili (Piper)

| Voce | Qualità | Dimensione |
|------|---------|------------|
| `it_IT-paola-medium` | Media | ~60MB |
| `it_IT-riccardo-x_low` | Bassa | ~15MB |

Lista completa: https://rhasspy.github.io/piper-samples/

## Risoluzione problemi

### Errore 500 su /api/v1/audio/speech

**Causa**: Open WebUI sta usando il backend sbagliato (transformers invece di openai)

**Soluzione**: Configura manualmente nelle impostazioni Admin come descritto sopra.

### OpenedAI Speech non risponde

Verifica che il container sia attivo:

```bash
docker compose logs openedai-speech --tail=20
```

Testa l'API direttamente:

```bash
curl http://localhost:8000/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{"input":"Ciao, questo è un test","voice":"alloy","model":"tts-1"}' \
  -o test.mp3
```

### Primo avvio lento

Al primo avvio, OpenedAI Speech scarica i modelli vocali (~500MB). Attendi che il download sia completato controllando i log:

```bash
docker compose logs -f openedai-speech
```

## Test rapido TTS

Testa che il TTS funzioni:

```bash
# Genera audio di test
curl -s http://localhost:8000/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{"input":"Ciao! Il sistema text to speech funziona correttamente.","voice":"alloy","model":"tts-1"}' \
  -o /tmp/test_tts.mp3

# Verifica che sia un file audio valido
file /tmp/test_tts.mp3

# Riproduci (se hai un player installato)
mpv /tmp/test_tts.mp3  # oppure: aplay, vlc, etc.
```

## Docker Compose

Configurazione in `docker-compose.yml`:

```yaml
services:
  open-webui:
    # ... configurazione esistente ...
    environment:
      # TTS locale con OpenedAI Speech
      - AUDIO_TTS_ENGINE=openai
      - AUDIO_TTS_OPENAI_API_BASE_URL=http://openedai-speech:8000/v1
      - AUDIO_TTS_OPENAI_API_KEY=sk-111111111
      - AUDIO_TTS_MODEL=tts-1
      - AUDIO_TTS_VOICE=alloy
    depends_on:
      - openedai-speech

  openedai-speech:
    image: ghcr.io/matatonic/openedai-speech
    container_name: openedai-speech
    ports:
      - "8000:8000"
    volumes:
      - openedai_speech_data:/app/voices
      - openedai_speech_config:/app/config
    environment:
      - TTS_HOME=/app/voices
      - HF_HOME=/app/voices
    restart: unless-stopped

volumes:
  openedai_speech_data:
  openedai_speech_config:
```

## Risorse

- [OpenedAI Speech GitHub](https://github.com/matatonic/openedai-speech)
- [Piper TTS](https://github.com/rhasspy/piper)
- [Voci Piper disponibili](https://rhasspy.github.io/piper-samples/)
- [Open WebUI Docs](https://docs.openwebui.com/)
