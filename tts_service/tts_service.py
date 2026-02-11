#!/usr/bin/env python3
"""
TTS Service - Servizio locale per sintesi vocale italiana

Supporta multiple backend:
- edge-tts: Microsoft Edge TTS (gratis, alta qualità, richiede internet)
- piper: Piper TTS locale (offline, veloce)
- gtts: Google TTS (gratis, richiede internet)
- openedai: OpenedAI Speech container (Piper in Docker)

Autore: Carlo
Versione: 1.0.0
Porta: 5556

Uso:
    python tts_service.py                    # Avvia servizio
    curl -X POST -d "text=Ciao mondo" http://localhost:5556/speak
"""

import os
import sys
import json
import hashlib
import asyncio
import tempfile
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime
import threading
import time

# FastAPI
try:
    from fastapi import FastAPI, Form, HTTPException, BackgroundTasks
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
    import uvicorn
    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False

# Requests per backend esterni
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

# Protezione sicurezza
_security_path = str(Path(__file__).parent.parent)
if _security_path not in sys.path:
    sys.path.insert(0, _security_path)
from security import ALLOWED_ORIGINS, create_api_key_middleware, SAFE_HOST


# ============================================================================
# CONFIGURAZIONE
# ============================================================================

SERVICE_PORT = 5556
CACHE_DIR = Path(__file__).parent / ".tts_cache"
CACHE_DIR.mkdir(exist_ok=True)

# Backend disponibili e configurazione
TTS_BACKENDS = {
    "edge-tts": {
        "name": "Microsoft Edge TTS",
        "description": "Alta qualità, gratis, richiede internet",
        "voices_it": [
            "it-IT-ElsaNeural",      # Femminile, standard
            "it-IT-IsabellaNeural",  # Femminile, caldo
            "it-IT-DiegoNeural",     # Maschile, standard
            "it-IT-GiuseppeNeural",  # Maschile, anziano
            "it-IT-BenignoNeural",   # Maschile, giovane
            "it-IT-CalimeroNeural",  # Maschile
            "it-IT-CataldoNeural",   # Maschile
            "it-IT-FabiolaNeural",   # Femminile
            "it-IT-FiammaNeural",    # Femminile
            "it-IT-GianniNeural",    # Maschile
            "it-IT-ImeldaNeural",    # Femminile
            "it-IT-IrmaNeural",      # Femminile
            "it-IT-LisandroNeural",  # Maschile
            "it-IT-PalmiraNeural",   # Femminile
            "it-IT-PierinaNeural",   # Femminile
            "it-IT-RinaldoNeural",   # Maschile
        ],
        "default_voice": "it-IT-IsabellaNeural",
        "requires_internet": True,
        "quality": "alta"
    },
    "piper": {
        "name": "Piper TTS",
        "description": "Locale, veloce, offline",
        "voices_it": [
            "it_IT-riccardo-x_low",
            "it_IT-paola-medium",
        ],
        "default_voice": "it_IT-riccardo-x_low",
        "requires_internet": False,
        "quality": "media"
    },
    "gtts": {
        "name": "Google TTS",
        "description": "Semplice, gratis, richiede internet",
        "voices_it": ["it"],
        "default_voice": "it",
        "requires_internet": True,
        "quality": "media"
    },
    "openedai": {
        "name": "OpenedAI Speech (Docker)",
        "description": "Piper via container Docker, già configurato",
        "api_url": "http://localhost:8000",
        "voices_it": ["alloy", "echo", "fable", "onyx", "nova", "shimmer"],
        "default_voice": "alloy",
        "requires_internet": False,
        "quality": "media"
    }
}


# ============================================================================
# BACKEND TTS
# ============================================================================

class TTSBackend:
    """Classe base per backend TTS."""

    def __init__(self, config: dict):
        self.config = config
        self.available = False
        self._check_availability()

    def _check_availability(self):
        """Verifica se il backend è disponibile."""
        raise NotImplementedError

    async def synthesize(self, text: str, voice: str, **kwargs) -> bytes:
        """Sintetizza testo in audio."""
        raise NotImplementedError

    def get_voices(self) -> List[str]:
        """Ritorna le voci disponibili."""
        return self.config.get("voices_it", [])


class EdgeTTSBackend(TTSBackend):
    """Backend Microsoft Edge TTS."""

    def _check_availability(self):
        try:
            import edge_tts
            self.available = True
        except ImportError:
            self.available = False

    async def synthesize(self, text: str, voice: str = None, rate: str = "+0%", volume: str = "+0%", **kwargs) -> bytes:
        import edge_tts
        import io

        voice = voice or self.config["default_voice"]

        communicate = edge_tts.Communicate(text, voice, rate=rate, volume=volume)

        audio_data = io.BytesIO()
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data.write(chunk["data"])

        return audio_data.getvalue()


class GTTSBackend(TTSBackend):
    """Backend Google TTS."""

    def _check_availability(self):
        try:
            from gtts import gTTS
            self.available = True
        except ImportError:
            self.available = False

    async def synthesize(self, text: str, voice: str = "it", slow: bool = False, **kwargs) -> bytes:
        from gtts import gTTS
        import io

        tts = gTTS(text=text, lang=voice, slow=slow)
        audio_data = io.BytesIO()
        tts.write_to_fp(audio_data)
        audio_data.seek(0)

        return audio_data.getvalue()


class PiperBackend(TTSBackend):
    """Backend Piper TTS locale."""

    def _check_availability(self):
        # Verifica se piper è installato
        import shutil
        self.available = shutil.which("piper") is not None

    async def synthesize(self, text: str, voice: str = None, **kwargs) -> bytes:
        import subprocess
        import tempfile

        voice = voice or self.config["default_voice"]

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            # Esegui piper
            process = subprocess.run(
                ["piper", "--model", voice, "--output_file", tmp_path],
                input=text.encode(),
                capture_output=True,
                timeout=30
            )

            if process.returncode != 0:
                raise Exception(f"Piper error: {process.stderr.decode()}")

            with open(tmp_path, "rb") as f:
                return f.read()

        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)


class OpenedAIBackend(TTSBackend):
    """Backend OpenedAI Speech (container Docker)."""

    def _check_availability(self):
        try:
            url = self.config.get("api_url", "http://localhost:8000")
            resp = requests.get(f"{url}/v1/models", timeout=5)
            self.available = resp.status_code == 200
        except:
            self.available = False

    async def synthesize(self, text: str, voice: str = "alloy", model: str = "tts-1", **kwargs) -> bytes:
        url = self.config.get("api_url", "http://localhost:8000")

        payload = {
            "model": model,
            "input": text,
            "voice": voice
        }

        resp = requests.post(
            f"{url}/v1/audio/speech",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=60
        )

        if resp.status_code != 200:
            raise Exception(f"OpenedAI error: {resp.status_code} - {resp.text}")

        return resp.content


# ============================================================================
# TTS MANAGER
# ============================================================================

class TTSManager:
    """Gestisce i backend TTS e la cache."""

    def __init__(self):
        self.backends: Dict[str, TTSBackend] = {}
        self.cache = TTSCache(CACHE_DIR)
        self._init_backends()

    def _init_backends(self):
        """Inizializza i backend disponibili."""
        backend_classes = {
            "edge-tts": EdgeTTSBackend,
            "gtts": GTTSBackend,
            "piper": PiperBackend,
            "openedai": OpenedAIBackend,
        }

        for name, config in TTS_BACKENDS.items():
            if name in backend_classes:
                try:
                    backend = backend_classes[name](config)
                    self.backends[name] = backend
                    status = "OK" if backend.available else "non disponibile"
                    print(f"[{'OK' if backend.available else '  '}] {config['name']}: {status}")
                except Exception as e:
                    print(f"[X] {config['name']}: errore - {e}")

    def get_available_backends(self) -> Dict[str, dict]:
        """Ritorna i backend disponibili con info."""
        result = {}
        for name, backend in self.backends.items():
            config = TTS_BACKENDS[name]
            result[name] = {
                "name": config["name"],
                "description": config["description"],
                "available": backend.available,
                "voices": backend.get_voices(),
                "default_voice": config["default_voice"],
                "requires_internet": config["requires_internet"],
                "quality": config["quality"]
            }
        return result

    async def synthesize(
        self,
        text: str,
        backend: str = "edge-tts",
        voice: str = None,
        use_cache: bool = True,
        **kwargs
    ) -> bytes:
        """Sintetizza testo usando il backend specificato."""

        # Verifica backend
        if backend not in self.backends:
            raise ValueError(f"Backend non trovato: {backend}")

        tts_backend = self.backends[backend]
        if not tts_backend.available:
            raise ValueError(f"Backend non disponibile: {backend}")

        # Usa voce default se non specificata
        if not voice:
            voice = TTS_BACKENDS[backend]["default_voice"]

        # Check cache
        cache_key = self.cache.get_key(text, backend, voice)
        if use_cache:
            cached = self.cache.get(cache_key)
            if cached:
                return cached

        # Sintetizza
        audio_data = await tts_backend.synthesize(text, voice, **kwargs)

        # Salva in cache
        if use_cache:
            self.cache.set(cache_key, audio_data)

        return audio_data


class TTSCache:
    """Cache per audio sintetizzato."""

    def __init__(self, cache_dir: Path):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(exist_ok=True)
        self.index_file = cache_dir / "index.json"
        self.index = self._load_index()

    def _load_index(self) -> dict:
        if self.index_file.exists():
            try:
                return json.loads(self.index_file.read_text())
            except:
                return {}
        return {}

    def _save_index(self):
        self.index_file.write_text(json.dumps(self.index, indent=2))

    def get_key(self, text: str, backend: str, voice: str) -> str:
        content = f"{text}|{backend}|{voice}"
        return hashlib.md5(content.encode()).hexdigest()

    def get(self, key: str) -> Optional[bytes]:
        if key in self.index:
            file_path = self.cache_dir / self.index[key]["file"]
            if file_path.exists():
                return file_path.read_bytes()
        return None

    def set(self, key: str, data: bytes):
        file_name = f"{key}.mp3"
        file_path = self.cache_dir / file_name
        file_path.write_bytes(data)

        self.index[key] = {
            "file": file_name,
            "timestamp": time.time(),
            "size": len(data)
        }
        self._save_index()

    def cleanup(self, max_age_hours: int = 24) -> int:
        """Rimuove file più vecchi di max_age_hours."""
        now = time.time()
        removed = 0

        for key, entry in list(self.index.items()):
            if now - entry.get("timestamp", 0) > max_age_hours * 3600:
                file_path = self.cache_dir / entry["file"]
                if file_path.exists():
                    file_path.unlink()
                del self.index[key]
                removed += 1

        self._save_index()
        return removed


# ============================================================================
# API SERVICE
# ============================================================================

def create_app() -> FastAPI:
    """Crea l'applicazione FastAPI."""

    app = FastAPI(
        title="TTS Service",
        description="Servizio locale per sintesi vocale italiana",
        version="1.0.0"
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*", "X-API-Key"],
    )

    # API key middleware (protegge POST/PUT/DELETE)
    create_api_key_middleware(app)

    # Inizializza TTS Manager
    manager = TTSManager()

    @app.get("/")
    async def root():
        """Health check e info."""
        backends = manager.get_available_backends()
        available = [name for name, info in backends.items() if info["available"]]

        return {
            "service": "TTS Service",
            "status": "running",
            "port": SERVICE_PORT,
            "backends_available": available,
            "backends_total": len(backends),
            "default_backend": "edge-tts" if "edge-tts" in available else (available[0] if available else None),
            "endpoints": [
                "POST /speak - Sintetizza testo",
                "POST /test - Test rapido voce",
                "GET /backends - Lista backend disponibili",
                "GET /voices/{backend} - Voci per backend",
                "DELETE /cache - Pulisci cache"
            ]
        }

    @app.get("/backends")
    async def list_backends():
        """Lista tutti i backend TTS disponibili."""
        return manager.get_available_backends()

    @app.get("/voices/{backend}")
    async def list_voices(backend: str):
        """Lista le voci disponibili per un backend."""
        if backend not in manager.backends:
            raise HTTPException(404, f"Backend non trovato: {backend}")

        config = TTS_BACKENDS[backend]
        return {
            "backend": backend,
            "name": config["name"],
            "voices": config.get("voices_it", []),
            "default": config["default_voice"]
        }

    @app.post("/speak")
    async def speak(
        text: str = Form(...),
        backend: str = Form(default="edge-tts"),
        voice: str = Form(default=None),
        rate: str = Form(default="+0%"),
        use_cache: bool = Form(default=True)
    ):
        """
        Sintetizza testo in audio.

        - **text**: Testo da sintetizzare
        - **backend**: Backend TTS (edge-tts, gtts, piper, openedai)
        - **voice**: Voce da usare (opzionale, usa default)
        - **rate**: Velocità (solo edge-tts, es. "+10%", "-20%")
        - **use_cache**: Usa cache (default: true)

        Ritorna file audio MP3.
        """
        try:
            audio_data = await manager.synthesize(
                text=text,
                backend=backend,
                voice=voice,
                use_cache=use_cache,
                rate=rate
            )

            return StreamingResponse(
                iter([audio_data]),
                media_type="audio/mpeg",
                headers={
                    "Content-Disposition": "attachment; filename=speech.mp3"
                }
            )

        except ValueError as e:
            raise HTTPException(400, str(e))
        except Exception as e:
            raise HTTPException(500, f"Errore sintesi: {str(e)}")

    @app.post("/test")
    async def test_voice(
        backend: str = Form(default="edge-tts"),
        voice: str = Form(default=None),
        text: str = Form(default="Ciao! Questo è un test della sintesi vocale italiana.")
    ):
        """
        Test rapido di una voce.

        Sintetizza un breve testo di prova e ritorna info + audio.
        """
        try:
            start_time = time.time()

            audio_data = await manager.synthesize(
                text=text,
                backend=backend,
                voice=voice,
                use_cache=False  # No cache per test
            )

            elapsed = time.time() - start_time

            # Salva temporaneamente per test
            test_file = CACHE_DIR / "test_audio.mp3"
            test_file.write_bytes(audio_data)

            return {
                "success": True,
                "backend": backend,
                "voice": voice or TTS_BACKENDS[backend]["default_voice"],
                "text": text,
                "audio_size_kb": round(len(audio_data) / 1024, 2),
                "synthesis_time_ms": round(elapsed * 1000),
                "audio_url": f"/test-audio",
                "message": "Test completato con successo! Usa /test-audio per ascoltare."
            }

        except Exception as e:
            return {
                "success": False,
                "backend": backend,
                "error": str(e),
                "message": "Test fallito. Verifica che il backend sia disponibile."
            }

    @app.get("/test-audio")
    async def get_test_audio():
        """Ritorna l'ultimo audio di test."""
        test_file = CACHE_DIR / "test_audio.mp3"
        if test_file.exists():
            return FileResponse(test_file, media_type="audio/mpeg")
        raise HTTPException(404, "Nessun audio di test disponibile")

    @app.delete("/cache")
    async def clear_cache(max_age_hours: int = 24):
        """Pulisce la cache audio."""
        removed = manager.cache.cleanup(max_age_hours)
        return {"message": f"Cache pulita, rimossi {removed} file"}

    @app.get("/openwebui-config")
    async def get_openwebui_config():
        """
        Ritorna la configurazione consigliata per Open WebUI.
        """
        backends = manager.get_available_backends()

        # Determina il backend migliore disponibile
        if backends.get("edge-tts", {}).get("available"):
            recommended = {
                "AUDIO_TTS_ENGINE": "openai",
                "AUDIO_TTS_OPENAI_API_BASE_URL": f"http://localhost:{SERVICE_PORT}/v1",
                "AUDIO_TTS_OPENAI_API_KEY": "sk-not-needed",
                "AUDIO_TTS_MODEL": "tts-1",
                "AUDIO_TTS_VOICE": "it-IT-IsabellaNeural",
                "note": "Usa questo servizio TTS come proxy OpenAI-compatibile"
            }
        elif backends.get("openedai", {}).get("available"):
            recommended = {
                "AUDIO_TTS_ENGINE": "openai",
                "AUDIO_TTS_OPENAI_API_BASE_URL": "http://localhost:8000/v1",
                "AUDIO_TTS_OPENAI_API_KEY": "sk-not-needed",
                "AUDIO_TTS_MODEL": "tts-1",
                "AUDIO_TTS_VOICE": "alloy",
                "note": "Usa OpenedAI Speech container"
            }
        else:
            recommended = {
                "note": "Nessun backend TTS disponibile. Installa edge-tts: pip install edge-tts"
            }

        return {
            "recommended_config": recommended,
            "available_backends": backends,
            "instructions": [
                "1. Copia le variabili nel file docker-compose.yml",
                "2. Riavvia Open WebUI: docker compose down && docker compose up -d",
                "3. In Open WebUI vai in Settings > Audio",
                "4. Seleziona la voce italiana desiderata"
            ]
        }

    # Endpoint compatibile OpenAI per integrazione diretta
    @app.post("/v1/audio/speech")
    async def openai_compatible_speech(
        request: dict = None
    ):
        """
        Endpoint compatibile con API OpenAI TTS.

        Permette di usare questo servizio come drop-in replacement.
        """
        try:
            # Parse request body
            import json
            from starlette.requests import Request

            text = request.get("input", "")
            voice = request.get("voice", "it-IT-IsabellaNeural")
            model = request.get("model", "tts-1")

            # Usa edge-tts come backend
            audio_data = await manager.synthesize(
                text=text,
                backend="edge-tts",
                voice=voice
            )

            return StreamingResponse(
                iter([audio_data]),
                media_type="audio/mpeg"
            )

        except Exception as e:
            raise HTTPException(500, str(e))

    return app


# ============================================================================
# MAIN
# ============================================================================

def check_dependencies():
    """Verifica dipendenze."""
    missing = []

    if not HAS_FASTAPI:
        missing.append("fastapi uvicorn")
    if not HAS_REQUESTS:
        missing.append("requests")

    # Verifica backend TTS
    try:
        import edge_tts
        print("[OK] edge-tts disponibile")
    except ImportError:
        print("[!] edge-tts non installato (consigliato)")
        missing.append("edge-tts")

    if missing:
        print(f"\n[!] Dipendenze mancanti: {', '.join(missing)}")
        print("\nInstalla con:")
        print(f"    pip install {' '.join(missing)}")
        return len(missing) == 0

    return True


def main():
    """Entry point."""
    print("""
╔══════════════════════════════════════════════════════════════╗
║          TTS SERVICE - Sintesi Vocale Italiana               ║
╠══════════════════════════════════════════════════════════════╣
║  Servizio locale per text-to-speech con voci italiane        ║
║  Compatibile con Open WebUI                                  ║
╚══════════════════════════════════════════════════════════════╝
    """)

    if not check_dependencies():
        print("\n[!] Alcune funzionalità potrebbero non essere disponibili")

    print(f"\n[*] Porta: {SERVICE_PORT}")
    print(f"[*] Cache: {CACHE_DIR}")
    print()

    # Avvia server
    app = create_app()
    uvicorn.run(app, host=SAFE_HOST, port=SERVICE_PORT, log_level="info")


if __name__ == "__main__":
    main()
