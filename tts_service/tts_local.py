#!/usr/bin/env python3
"""
TTS Local Service - Sintesi Vocale Italiana OFFLINE

Usa Piper TTS per voci italiane completamente locali.
Non richiede internet dopo il primo download dei modelli.

Autore: Carlo
Versione: 1.0.0
Porta: 5556

Modelli italiani disponibili:
- it_IT-riccardo-x_low (maschile, veloce)
- it_IT-paola-medium (femminile, qualità media)
"""

import os
import sys
import json
import hashlib
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Optional, Dict, List
import time
import threading
import io
import wave

# FastAPI
try:
    from fastapi import FastAPI, Form, HTTPException, File, UploadFile
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import FileResponse, StreamingResponse, JSONResponse
    import uvicorn
    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False

# Requests per download modelli
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


# ============================================================================
# CONFIGURAZIONE
# ============================================================================

SERVICE_PORT = 5556
MODELS_DIR = Path(__file__).parent / "piper_models"
CACHE_DIR = Path(__file__).parent / ".tts_cache"

# Modelli Piper italiani disponibili
PIPER_ITALIAN_MODELS = {
    "riccardo": {
        "name": "Riccardo",
        "gender": "M",
        "quality": "x_low",
        "description": "Voce maschile, veloce, bassa qualità",
        "model_file": "it_IT-riccardo-x_low.onnx",
        "config_file": "it_IT-riccardo-x_low.onnx.json",
        "url_base": "https://huggingface.co/rhasspy/piper-voices/resolve/main/it/it_IT/riccardo/x_low/",
        "sample_rate": 22050
    },
    "paola": {
        "name": "Paola",
        "gender": "F",
        "quality": "medium",
        "description": "Voce femminile, qualità media",
        "model_file": "it_IT-paola-medium.onnx",
        "config_file": "it_IT-paola-medium.onnx.json",
        "url_base": "https://huggingface.co/rhasspy/piper-voices/resolve/main/it/it_IT/paola/medium/",
        "sample_rate": 22050
    }
}

# Mapping per compatibilità OpenAI
OPENAI_VOICE_MAP = {
    "alloy": "paola",
    "echo": "riccardo",
    "fable": "paola",
    "onyx": "riccardo",
    "nova": "paola",
    "shimmer": "paola",
    # Voci dirette
    "riccardo": "riccardo",
    "paola": "paola",
    "it-riccardo": "riccardo",
    "it-paola": "paola"
}


# ============================================================================
# PIPER TTS ENGINE
# ============================================================================

class PiperTTS:
    """Engine TTS locale con Piper."""

    def __init__(self, models_dir: Path = MODELS_DIR):
        self.models_dir = models_dir
        self.models_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir = CACHE_DIR
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self.piper_path = self._find_piper()
        self.available_models = {}
        self._scan_models()

    def _find_piper(self) -> Optional[str]:
        """Trova l'eseguibile Piper."""
        # Cerca in PATH
        piper = shutil.which("piper")
        if piper:
            return piper

        # Cerca nella cartella locale
        local_piper = self.models_dir / "piper"
        if local_piper.exists():
            return str(local_piper)

        # Windows
        local_piper_exe = self.models_dir / "piper.exe"
        if local_piper_exe.exists():
            return str(local_piper_exe)

        return None

    def _scan_models(self):
        """Scansiona i modelli disponibili."""
        self.available_models = {}

        for voice_id, info in PIPER_ITALIAN_MODELS.items():
            model_path = self.models_dir / info["model_file"]
            config_path = self.models_dir / info["config_file"]

            if model_path.exists() and config_path.exists():
                self.available_models[voice_id] = {
                    **info,
                    "model_path": str(model_path),
                    "config_path": str(config_path),
                    "installed": True
                }
            else:
                self.available_models[voice_id] = {
                    **info,
                    "installed": False
                }

    def download_model(self, voice_id: str, progress_callback=None) -> bool:
        """Scarica un modello Piper."""
        if voice_id not in PIPER_ITALIAN_MODELS:
            raise ValueError(f"Voce non trovata: {voice_id}")

        info = PIPER_ITALIAN_MODELS[voice_id]

        files_to_download = [
            (info["model_file"], info["url_base"] + info["model_file"]),
            (info["config_file"], info["url_base"] + info["config_file"])
        ]

        for filename, url in files_to_download:
            dest_path = self.models_dir / filename

            if dest_path.exists():
                if progress_callback:
                    progress_callback(f"{filename} già presente")
                continue

            if progress_callback:
                progress_callback(f"Download {filename}...")

            try:
                resp = requests.get(url, stream=True, timeout=60)
                resp.raise_for_status()

                total = int(resp.headers.get('content-length', 0))
                downloaded = 0

                with open(dest_path, 'wb') as f:
                    for chunk in resp.iter_content(chunk_size=8192):
                        f.write(chunk)
                        downloaded += len(chunk)
                        if progress_callback and total > 0:
                            pct = int(downloaded / total * 100)
                            progress_callback(f"{filename}: {pct}%")

            except Exception as e:
                if dest_path.exists():
                    dest_path.unlink()
                raise Exception(f"Errore download {filename}: {e}")

        self._scan_models()
        return voice_id in self.available_models and self.available_models[voice_id]["installed"]

    def download_piper(self, progress_callback=None) -> bool:
        """Scarica l'eseguibile Piper se non presente."""
        if self.piper_path:
            return True

        import platform
        system = platform.system().lower()
        machine = platform.machine().lower()

        # Determina URL download
        if system == "linux":
            if "arm" in machine or "aarch64" in machine:
                arch = "aarch64"
            else:
                arch = "x86_64"
            filename = f"piper_linux_{arch}.tar.gz"
        elif system == "windows":
            filename = "piper_windows_amd64.zip"
        elif system == "darwin":
            filename = "piper_macos_x64.tar.gz"
        else:
            raise Exception(f"Sistema non supportato: {system}")

        url = f"https://github.com/rhasspy/piper/releases/latest/download/{filename}"

        if progress_callback:
            progress_callback(f"Download Piper ({filename})...")

        try:
            resp = requests.get(url, stream=True, timeout=120)
            resp.raise_for_status()

            archive_path = self.models_dir / filename

            with open(archive_path, 'wb') as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    f.write(chunk)

            # Estrai
            if progress_callback:
                progress_callback("Estrazione Piper...")

            if filename.endswith(".tar.gz"):
                import tarfile
                with tarfile.open(archive_path, 'r:gz') as tar:
                    tar.extractall(self.models_dir)
            else:
                import zipfile
                with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                    zip_ref.extractall(self.models_dir)

            archive_path.unlink()

            # Trova piper
            self.piper_path = self._find_piper()

            if self.piper_path:
                # Rendi eseguibile su Linux/Mac
                if system != "windows":
                    os.chmod(self.piper_path, 0o755)
                return True

        except Exception as e:
            raise Exception(f"Errore download Piper: {e}")

        return False

    def synthesize(self, text: str, voice: str = "paola", speed: float = 1.0) -> bytes:
        """Sintetizza testo in audio WAV."""

        # Mappa voce OpenAI a Piper
        voice_id = OPENAI_VOICE_MAP.get(voice.lower(), voice.lower())

        if voice_id not in self.available_models:
            raise ValueError(f"Voce non disponibile: {voice}. Disponibili: {list(self.available_models.keys())}")

        model_info = self.available_models[voice_id]

        if not model_info.get("installed"):
            raise ValueError(f"Modello non installato: {voice_id}. Scaricalo prima.")

        if not self.piper_path:
            raise ValueError("Piper non installato. Scaricalo prima.")

        # Genera audio
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            cmd = [
                self.piper_path,
                "--model", model_info["model_path"],
                "--config", model_info["config_path"],
                "--output_file", tmp_path
            ]

            if speed != 1.0:
                cmd.extend(["--length_scale", str(1.0 / speed)])

            process = subprocess.run(
                cmd,
                input=text.encode('utf-8'),
                capture_output=True,
                timeout=60
            )

            if process.returncode != 0:
                error_msg = process.stderr.decode() if process.stderr else "Errore sconosciuto"
                raise Exception(f"Piper error: {error_msg}")

            with open(tmp_path, "rb") as f:
                wav_data = f.read()

            return wav_data

        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    def synthesize_to_mp3(self, text: str, voice: str = "paola", speed: float = 1.0) -> bytes:
        """Sintetizza testo e converte in MP3."""
        wav_data = self.synthesize(text, voice, speed)

        # Converti WAV -> MP3 con ffmpeg se disponibile
        if shutil.which("ffmpeg"):
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as wav_tmp:
                wav_tmp.write(wav_data)
                wav_path = wav_tmp.name

            mp3_path = wav_path.replace(".wav", ".mp3")

            try:
                subprocess.run([
                    "ffmpeg", "-y", "-i", wav_path,
                    "-acodec", "libmp3lame", "-b:a", "128k",
                    mp3_path
                ], capture_output=True, timeout=30)

                with open(mp3_path, "rb") as f:
                    mp3_data = f.read()

                return mp3_data

            finally:
                if os.path.exists(wav_path):
                    os.unlink(wav_path)
                if os.path.exists(mp3_path):
                    os.unlink(mp3_path)

        # Fallback: ritorna WAV
        return wav_data


# ============================================================================
# API SERVICE
# ============================================================================

def create_app() -> FastAPI:
    """Crea l'applicazione FastAPI."""

    app = FastAPI(
        title="TTS Local Service",
        description="Sintesi vocale italiana locale con Piper",
        version="1.0.0"
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Inizializza Piper TTS
    tts = PiperTTS()

    @app.get("/")
    async def root():
        """Health check e info."""
        installed = [v for v, info in tts.available_models.items() if info.get("installed")]
        return {
            "service": "TTS Local Service (Piper)",
            "status": "running",
            "port": SERVICE_PORT,
            "piper_installed": tts.piper_path is not None,
            "piper_path": tts.piper_path,
            "models_installed": installed,
            "models_available": list(PIPER_ITALIAN_MODELS.keys()),
            "offline": True,
            "language": "italiano",
            "endpoints": [
                "POST /speak - Sintetizza testo",
                "POST /test - Test voce",
                "GET /voices - Lista voci",
                "POST /install/{voice} - Installa voce",
                "POST /install-piper - Installa Piper",
                "POST /v1/audio/speech - Endpoint OpenAI-compatibile"
            ]
        }

    @app.get("/voices")
    async def list_voices():
        """Lista le voci italiane disponibili."""
        voices = []
        for voice_id, info in tts.available_models.items():
            voices.append({
                "id": voice_id,
                "name": info["name"],
                "gender": info["gender"],
                "quality": info["quality"],
                "description": info["description"],
                "installed": info.get("installed", False)
            })
        return {
            "voices": voices,
            "default": "paola",
            "language": "it-IT"
        }

    @app.post("/install/{voice_id}")
    async def install_voice(voice_id: str):
        """Installa un modello vocale."""
        if voice_id not in PIPER_ITALIAN_MODELS:
            raise HTTPException(404, f"Voce non trovata: {voice_id}")

        messages = []
        def progress(msg):
            messages.append(msg)

        try:
            success = tts.download_model(voice_id, progress)
            return {
                "success": success,
                "voice": voice_id,
                "messages": messages
            }
        except Exception as e:
            raise HTTPException(500, str(e))

    @app.post("/install-piper")
    async def install_piper():
        """Installa l'eseguibile Piper."""
        if tts.piper_path:
            return {"success": True, "message": "Piper già installato", "path": tts.piper_path}

        messages = []
        def progress(msg):
            messages.append(msg)

        try:
            success = tts.download_piper(progress)
            return {
                "success": success,
                "path": tts.piper_path,
                "messages": messages
            }
        except Exception as e:
            raise HTTPException(500, str(e))

    @app.post("/speak")
    async def speak(
        text: str = Form(...),
        voice: str = Form(default="paola"),
        speed: float = Form(default=1.0),
        format: str = Form(default="wav")
    ):
        """
        Sintetizza testo in audio.

        - **text**: Testo da sintetizzare
        - **voice**: Voce (paola, riccardo)
        - **speed**: Velocità (0.5-2.0, default 1.0)
        - **format**: Formato (wav, mp3)
        """
        try:
            if format == "mp3" and shutil.which("ffmpeg"):
                audio_data = tts.synthesize_to_mp3(text, voice, speed)
                media_type = "audio/mpeg"
            else:
                audio_data = tts.synthesize(text, voice, speed)
                media_type = "audio/wav"

            return StreamingResponse(
                io.BytesIO(audio_data),
                media_type=media_type,
                headers={"Content-Disposition": f"attachment; filename=speech.{format}"}
            )

        except ValueError as e:
            raise HTTPException(400, str(e))
        except Exception as e:
            raise HTTPException(500, f"Errore sintesi: {e}")

    @app.post("/test")
    async def test_voice(
        voice: str = Form(default="paola"),
        text: str = Form(default="Ciao! Questo è un test della sintesi vocale italiana.")
    ):
        """Test rapido voce."""
        try:
            start = time.time()
            audio_data = tts.synthesize(text, voice)
            elapsed = time.time() - start

            # Salva per riproduzione
            test_file = CACHE_DIR / "test_audio.wav"
            test_file.write_bytes(audio_data)

            return {
                "success": True,
                "voice": voice,
                "text": text,
                "audio_size_kb": round(len(audio_data) / 1024, 2),
                "synthesis_time_ms": round(elapsed * 1000),
                "audio_url": "/test-audio",
                "offline": True
            }

        except Exception as e:
            return {
                "success": False,
                "voice": voice,
                "error": str(e)
            }

    @app.get("/test-audio")
    async def get_test_audio():
        """Ritorna l'ultimo audio di test."""
        test_file = CACHE_DIR / "test_audio.wav"
        if test_file.exists():
            return FileResponse(test_file, media_type="audio/wav")
        raise HTTPException(404, "Nessun audio di test")

    # Endpoint compatibile OpenAI
    @app.post("/v1/audio/speech")
    async def openai_speech(request: dict = None):
        """Endpoint compatibile con API OpenAI TTS."""
        try:
            text = request.get("input", "")
            voice = request.get("voice", "paola")
            model = request.get("model", "tts-1")  # Ignorato, usiamo sempre Piper
            speed = request.get("speed", 1.0)

            # Mappa voce OpenAI a Piper
            voice_id = OPENAI_VOICE_MAP.get(voice.lower(), "paola")

            audio_data = tts.synthesize(text, voice_id, speed)

            return StreamingResponse(
                io.BytesIO(audio_data),
                media_type="audio/wav"
            )

        except Exception as e:
            raise HTTPException(500, str(e))

    @app.get("/openwebui-config")
    async def get_openwebui_config():
        """Configurazione per Open WebUI."""
        return {
            "docker_compose_env": {
                "AUDIO_TTS_ENGINE": "openai",
                "AUDIO_TTS_OPENAI_API_BASE_URL": f"http://host.docker.internal:{SERVICE_PORT}/v1",
                "AUDIO_TTS_OPENAI_API_KEY": "sk-local",
                "AUDIO_TTS_MODEL": "tts-1",
                "AUDIO_TTS_VOICE": "paola"
            },
            "voices": {
                "paola": "Voce femminile italiana",
                "riccardo": "Voce maschile italiana"
            },
            "note": "Questo servizio è completamente OFFLINE dopo l'installazione dei modelli"
        }

    return app


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Entry point."""
    print("""
╔══════════════════════════════════════════════════════════════╗
║       TTS LOCAL SERVICE - Sintesi Vocale Italiana            ║
╠══════════════════════════════════════════════════════════════╣
║  Voci italiane OFFLINE con Piper TTS                         ║
║  Non richiede internet dopo l'installazione                  ║
╚══════════════════════════════════════════════════════════════╝
    """)

    if not HAS_FASTAPI:
        print("[X] FastAPI non installato!")
        print("    pip install fastapi uvicorn")
        sys.exit(1)

    # Verifica stato
    tts = PiperTTS()

    print(f"[*] Directory modelli: {MODELS_DIR}")
    print(f"[*] Piper installato: {'SI' if tts.piper_path else 'NO'}")

    installed = [v for v, info in tts.available_models.items() if info.get("installed")]
    print(f"[*] Voci installate: {installed if installed else 'Nessuna'}")

    if not tts.piper_path:
        print("\n[!] Piper non trovato. Verrà scaricato alla prima richiesta")
        print("    Oppure visita: http://localhost:5556/install-piper")

    if not installed:
        print("\n[!] Nessuna voce italiana installata.")
        print("    Scarica con:")
        print("    - http://localhost:5556/install/paola")
        print("    - http://localhost:5556/install/riccardo")

    print(f"\n[*] Avvio servizio su http://localhost:{SERVICE_PORT}")
    print("[*] Premi Ctrl+C per fermare\n")

    app = create_app()
    uvicorn.run(app, host="0.0.0.0", port=SERVICE_PORT, log_level="info")


if __name__ == "__main__":
    main()
