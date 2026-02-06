#!/usr/bin/env python3
"""
TTS Local Service - Sintesi Vocale Italiana OFFLINE

Usa Piper TTS per voci italiane completamente locali.
Non richiede internet dopo il primo download dei modelli.

Autore: Carlo
Versione: 1.1.0
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

# Piper TTS Python library
try:
    from piper import PiperVoice
    HAS_PIPER_LIB = True
except ImportError:
    HAS_PIPER_LIB = False

# System Profiler per timeout dinamici
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
try:
    from system_profiler import (
        get_system_profile, init_system_protection,
        protected_call, MemoryWatchdog, SystemTier
    )
    HAS_PROFILER = True
except ImportError:
    HAS_PROFILER = False


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

        self.piper_path = self._find_piper_executable()
        self.use_python_lib = HAS_PIPER_LIB
        self.loaded_voices = {}  # Cache delle voci caricate
        self.available_models = {}
        self._scan_models()

    def _find_piper_executable(self) -> Optional[str]:
        """Trova l'eseguibile NATIVO Piper (non lo script Python)."""
        # Cerca nella cartella locale PRIMA (priorità)
        local_piper = self.models_dir / "piper"
        if local_piper.exists() and local_piper.is_file():
            return str(local_piper)

        # Windows
        local_piper_exe = self.models_dir / "piper.exe"
        if local_piper_exe.exists():
            return str(local_piper_exe)

        # Cerca in PATH ma verifica che sia l'eseguibile nativo
        piper = shutil.which("piper")
        if piper:
            # Verifica se è l'eseguibile nativo o lo script Python
            # Lo script Python inizia con #!/usr/bin/python o simili
            try:
                with open(piper, 'rb') as f:
                    header = f.read(100)
                    # Gli script Python iniziano con #! e python
                    if b'python' in header.lower():
                        # È lo script Python, non usarlo come eseguibile
                        return None
                    # ELF o PE header = eseguibile nativo
                    if header.startswith(b'\x7fELF') or header.startswith(b'MZ'):
                        return piper
            except:
                pass

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

    def is_ready(self) -> tuple[bool, str]:
        """
        Verifica se il TTS è pronto per la sintesi.

        Returns:
            (ready, message): Tupla con stato e messaggio
        """
        installed_voices = [v for v, info in self.available_models.items() if info.get("installed")]

        if not installed_voices:
            return False, "Nessuna voce installata. Apri il tab 'Voce' nella GUI per scaricare le voci italiane."

        if not self.piper_path and not self.use_python_lib:
            return False, "Piper non installato. Apri il tab 'Voce' nella GUI per installarlo."

        return True, f"TTS pronto. Voci disponibili: {', '.join(installed_voices)}"

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
            self.piper_path = self._find_piper_executable()

            if self.piper_path:
                # Rendi eseguibile su Linux/Mac
                if system != "windows":
                    os.chmod(self.piper_path, 0o755)
                return True

        except Exception as e:
            raise Exception(f"Errore download Piper: {e}")

        return False

    def _synthesize_with_lib(self, text: str, model_path: str, config_path: str) -> bytes:
        """Sintetizza usando la libreria Python piper-tts."""
        if not HAS_PIPER_LIB:
            raise ValueError("Libreria piper-tts non installata")

        # Carica la voce se non già in cache
        if model_path not in self.loaded_voices:
            try:
                self.loaded_voices[model_path] = PiperVoice.load(model_path, config_path)
            except Exception as e:
                raise ValueError(f"Impossibile caricare modello {model_path}: {e}")

        voice = self.loaded_voices[model_path]

        # Sintetizza in memoria (piper-tts >= 1.3.0 usa synthesize_wav)
        wav_buffer = io.BytesIO()
        with wave.open(wav_buffer, 'wb') as wav_file:
            voice.synthesize_wav(text, wav_file)

        wav_buffer.seek(0)
        return wav_buffer.read()

    def _synthesize_with_executable(self, text: str, model_path: str, config_path: str, speed: float) -> bytes:
        """Sintetizza usando l'eseguibile nativo Piper."""
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            cmd = [
                self.piper_path,
                "--model", model_path,
                "--config", config_path,
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

    def synthesize(self, text: str, voice: str = "paola", speed: float = 1.0) -> bytes:
        """Sintetizza testo in audio WAV."""

        # Mappa voce OpenAI a Piper
        voice_id = OPENAI_VOICE_MAP.get(voice.lower(), voice.lower())

        if voice_id not in self.available_models:
            raise ValueError(f"Voce non disponibile: {voice}. Disponibili: {list(self.available_models.keys())}")

        model_info = self.available_models[voice_id]

        if not model_info.get("installed"):
            raise ValueError(f"VOCE_NON_INSTALLATA: La voce '{voice_id}' non è installata. Apri il tab 'Voce' nella GUI per scaricarla.")

        model_path = model_info["model_path"]
        config_path = model_info["config_path"]

        # Verifica che i file esistano realmente
        if not os.path.exists(model_path):
            raise ValueError(f"VOCE_NON_INSTALLATA: File modello non trovato: {model_path}. Scarica la voce dal tab 'Voce'.")
        if not os.path.exists(config_path):
            raise ValueError(f"VOCE_NON_INSTALLATA: File config non trovato: {config_path}. Scarica la voce dal tab 'Voce'.")

        # Prova prima con la libreria Python (se disponibile)
        if self.use_python_lib:
            try:
                return self._synthesize_with_lib(text, model_path, config_path)
            except Exception as e:
                # Se fallisce con la lib, prova con l'eseguibile
                if self.piper_path:
                    pass  # Continua sotto
                else:
                    raise ValueError(f"Errore sintesi con libreria Piper: {e}")

        # Usa l'eseguibile nativo
        if self.piper_path:
            return self._synthesize_with_executable(text, model_path, config_path, speed)

        raise ValueError("PIPER_NON_INSTALLATO: Né la libreria Python né l'eseguibile Piper sono disponibili. Apri il tab 'Voce' per installare.")

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
        version="1.1.0"
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

    # Inizializza System Profiler per timeout dinamici
    system_profile = None
    memory_watchdog = None
    if HAS_PROFILER:
        try:
            system_profile = init_system_protection(start_watchdog=True)
            from system_profiler import get_watchdog
            memory_watchdog = get_watchdog()
            print(f"[*] System Profiler attivo: tier={system_profile.tier.value}, timeout_tts={system_profile.timeout_tts}s")
        except Exception as e:
            print(f"[!] System Profiler non disponibile: {e}")

    @app.get("/")
    async def root():
        """Health check e info."""
        installed = [v for v, info in tts.available_models.items() if info.get("installed")]
        ready, message = tts.is_ready()

        # Info sistema
        system_info = None
        if system_profile:
            system_info = {
                "tier": system_profile.tier.value,
                "ram_total_gb": system_profile.ram_total_gb,
                "ram_available_gb": system_profile.ram_available_gb,
                "ram_percent_used": system_profile.ram_percent_used,
                "timeout_tts": system_profile.timeout_tts,
                "memory_blocked": memory_watchdog.is_blocked() if memory_watchdog else False
            }

        return {
            "service": "TTS Local Service (Piper)",
            "status": "running",
            "ready": ready,
            "ready_message": message,
            "port": SERVICE_PORT,
            "piper_executable": tts.piper_path,
            "piper_library": tts.use_python_lib,
            "models_installed": installed,
            "models_available": list(PIPER_ITALIAN_MODELS.keys()),
            "offline": True,
            "language": "italiano",
            "system": system_info,
            "action": None if ready else "Apri il tab 'Voce' nella GUI per installare le voci",
            "endpoints": [
                "GET /system - Info sistema e limiti",
                "GET /voices/check - Verifica disponibilità voci (CHIAMARE PRIMA DI SINTETIZZARE)",
                "GET /v1/audio/speech/ready - Preflight check per Open WebUI",
                "POST /v1/audio/speech - Endpoint OpenAI-compatibile",
                "POST /speak - Sintetizza testo",
                "POST /test - Test voce",
                "GET /voices - Lista voci",
                "POST /install/{voice} - Installa voce",
                "POST /install-piper - Installa Piper"
            ]
        }

    @app.get("/system")
    async def system_status():
        """Informazioni sul sistema e limiti di protezione."""
        if not system_profile:
            return {
                "profiler_available": False,
                "message": "System Profiler non disponibile. Installa psutil: pip install psutil"
            }

        return {
            "profiler_available": True,
            "tier": system_profile.tier.value,
            "tier_description": {
                "minimal": "Risorse molto limitate - timeout brevi, operazioni serializzate",
                "low": "Risorse limitate - timeout ridotti",
                "medium": "Risorse adeguate - timeout normali",
                "high": "Sistema potente - nessun limite"
            }.get(system_profile.tier.value, ""),
            "ram": {
                "total_gb": system_profile.ram_total_gb,
                "available_gb": system_profile.ram_available_gb,
                "percent_used": system_profile.ram_percent_used,
                "warning_threshold": system_profile.ram_warning_threshold,
                "critical_threshold": system_profile.ram_critical_threshold
            },
            "cpu": {
                "cores": system_profile.cpu_cores,
                "percent": system_profile.cpu_percent
            },
            "limits": {
                "timeout_tts_seconds": system_profile.timeout_tts,
                "timeout_llm_seconds": system_profile.timeout_llm,
                "max_parallel_operations": system_profile.max_parallel_ops,
                "max_text_length": system_profile.max_text_length
            },
            "protection": {
                "watchdog_active": memory_watchdog is not None,
                "operations_blocked": memory_watchdog.is_blocked() if memory_watchdog else False
            }
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
        # Verifica preventiva
        ready, message = tts.is_ready()
        if not ready:
            return {
                "success": False,
                "voice": voice,
                "error": message,
                "action": "open_voice_tab",
                "help": "Apri il tab 'Voce' nella GUI per scaricare le voci italiane."
            }

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
            error_msg = str(e)
            return {
                "success": False,
                "voice": voice,
                "error": error_msg,
                "action": "open_voice_tab" if "VOCE_NON_INSTALLATA" in error_msg or "PIPER_NON_INSTALLATO" in error_msg else None,
                "help": "Apri il tab 'Voce' nella GUI per risolvere il problema." if "NON_INSTALLAT" in error_msg else None
            }

    @app.get("/test-audio")
    async def get_test_audio():
        """Ritorna l'ultimo audio di test."""
        test_file = CACHE_DIR / "test_audio.wav"
        if test_file.exists():
            return FileResponse(test_file, media_type="audio/wav")
        raise HTTPException(404, "Nessun audio di test")

    @app.get("/voices/check")
    async def check_voices():
        """
        Verifica se le voci sono disponibili per l'uso.
        IMPORTANTE: Chiamare SEMPRE questo endpoint prima di /v1/audio/speech
        per evitare errori.

        Ritorna:
        - ready: True se almeno una voce è installata
        - voices_installed: Lista voci installate
        - voices_missing: Lista voci da installare
        - piper_available: True se Piper (lib o exe) è disponibile
        """
        installed = [v for v, info in tts.available_models.items() if info.get("installed")]
        missing = [v for v, info in tts.available_models.items() if not info.get("installed")]

        ready, message = tts.is_ready()

        return {
            "ready": ready,
            "piper_executable": tts.piper_path is not None,
            "piper_library": tts.use_python_lib,
            "piper_available": tts.piper_path is not None or tts.use_python_lib,
            "voices_installed": installed,
            "voices_missing": missing,
            "default_voice": installed[0] if installed else None,
            "message": message,
            "action": None if ready else "open_voice_tab"
        }

    @app.get("/v1/audio/speech/ready")
    async def check_speech_ready():
        """
        Endpoint di preflight check per Open WebUI.
        Chiama questo PRIMA di sintetizzare per verificare che tutto sia pronto.

        Ritorna 200 se pronto, 503 se non pronto.
        """
        ready, message = tts.is_ready()

        if not ready:
            raise HTTPException(
                503,
                detail={
                    "error": "tts_not_ready",
                    "message": message,
                    "action": "open_voice_tab",
                    "voices_installed": [v for v, info in tts.available_models.items() if info.get("installed")]
                }
            )

        return {
            "ready": True,
            "message": message,
            "default_voice": "paola" if "paola" in tts.available_models and tts.available_models["paola"].get("installed") else None
        }

    # Endpoint compatibile OpenAI
    @app.post("/v1/audio/speech")
    async def openai_speech(request: dict = None):
        """
        Endpoint compatibile con API OpenAI TTS.

        NOTA: Questo endpoint verifica la disponibilità delle voci PRIMA
        di tentare la sintesi. Se le voci non sono installate, ritorna
        un errore 503 con istruzioni chiare.

        Include protezione memoria e timeout dinamici basati sulle capacità del sistema.
        """
        # === CONTROLLO MEMORIA (protezione blocco sistema) ===
        if memory_watchdog and memory_watchdog.is_blocked():
            raise HTTPException(
                503,
                detail={
                    "error": "memory_critical",
                    "message": "Memoria insufficiente. Chiudi altre applicazioni e riprova.",
                    "ram_percent": system_profile.ram_percent_used if system_profile else None,
                    "action": "free_memory"
                }
            )

        # === CONTROLLO TTS PRONTO ===
        ready, ready_message = tts.is_ready()
        if not ready:
            raise HTTPException(
                503,
                detail={
                    "error": "tts_not_ready",
                    "message": ready_message,
                    "action": "open_voice_tab",
                    "help": "Apri la GUI di Open WebUI Manager e vai nel tab 'Voce' per scaricare le voci italiane."
                }
            )

        try:
            text = request.get("input", "") if request else ""
            voice = request.get("voice", "paola") if request else "paola"
            model = request.get("model", "tts-1") if request else "tts-1"  # Ignorato
            speed = request.get("speed", 1.0) if request else 1.0

            if not text:
                raise HTTPException(400, detail={"error": "empty_text", "message": "Nessun testo da sintetizzare"})

            # === LIMITE LUNGHEZZA TESTO (protezione RAM) ===
            max_length = system_profile.max_text_length if system_profile else 10000
            if len(text) > max_length:
                text = text[:max_length]
                # Non blocchiamo, ma tronchiamo silenziosamente

            # Mappa voce OpenAI a Piper
            voice_id = OPENAI_VOICE_MAP.get(voice.lower(), "paola")

            # Verifica che la voce richiesta sia installata
            if voice_id not in tts.available_models:
                # Usa la prima voce disponibile come fallback
                installed = [v for v, info in tts.available_models.items() if info.get("installed")]
                if installed:
                    voice_id = installed[0]
                else:
                    raise HTTPException(
                        503,
                        detail={
                            "error": "no_voices_installed",
                            "message": "Nessuna voce installata. Apri il tab 'Voce' nella GUI per scaricare le voci.",
                            "action": "open_voice_tab"
                        }
                    )

            model_info = tts.available_models[voice_id]
            if not model_info.get("installed"):
                # Cerca una voce alternativa installata
                installed = [v for v, info in tts.available_models.items() if info.get("installed")]
                if installed:
                    voice_id = installed[0]
                    model_info = tts.available_models[voice_id]
                else:
                    raise HTTPException(
                        503,
                        detail={
                            "error": "voice_not_installed",
                            "message": f"Voce '{voice}' non installata e nessuna alternativa disponibile. Apri il tab 'Voce' nella GUI.",
                            "action": "open_voice_tab"
                        }
                    )

            # === SINTESI CON TIMEOUT DINAMICO ===
            timeout = system_profile.timeout_tts if system_profile else 60

            def do_synthesis():
                return tts.synthesize(text, voice_id, speed)

            if HAS_PROFILER:
                try:
                    from system_profiler import run_with_timeout, TimeoutError as ProfilerTimeout
                    audio_data = run_with_timeout(do_synthesis, timeout)
                except ProfilerTimeout:
                    raise HTTPException(
                        504,
                        detail={
                            "error": "timeout",
                            "message": f"Sintesi vocale interrotta dopo {timeout}s. Il sistema potrebbe essere sovraccarico.",
                            "timeout_seconds": timeout,
                            "system_tier": system_profile.tier.value if system_profile else "unknown"
                        }
                    )
            else:
                audio_data = do_synthesis()

            return StreamingResponse(
                io.BytesIO(audio_data),
                media_type="audio/wav"
            )

        except HTTPException:
            raise
        except ValueError as e:
            error_msg = str(e)
            # Controlla se è un errore di configurazione specifico
            if "VOCE_NON_INSTALLATA" in error_msg or "PIPER_NON_INSTALLATO" in error_msg:
                raise HTTPException(
                    503,
                    detail={
                        "error": "configuration_error",
                        "message": error_msg.replace("VOCE_NON_INSTALLATA: ", "").replace("PIPER_NON_INSTALLATO: ", ""),
                        "action": "open_voice_tab"
                    }
                )
            raise HTTPException(
                500,
                detail={
                    "error": "synthesis_error",
                    "message": error_msg
                }
            )
        except Exception as e:
            raise HTTPException(
                500,
                detail={
                    "error": "internal_error",
                    "message": f"Errore sintesi: {str(e)}"
                }
            )

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
    print(f"[*] Piper eseguibile: {'SI -> ' + tts.piper_path if tts.piper_path else 'NO'}")
    print(f"[*] Piper libreria Python: {'SI' if tts.use_python_lib else 'NO'}")

    installed = [v for v, info in tts.available_models.items() if info.get("installed")]
    missing = [v for v, info in tts.available_models.items() if not info.get("installed")]
    print(f"[*] Voci installate: {installed if installed else 'Nessuna'}")
    print(f"[*] Voci mancanti: {missing if missing else 'Nessuna'}")

    # Verifica se il sistema è pronto
    ready, message = tts.is_ready()

    if ready:
        print(f"\n[✓] SISTEMA PRONTO: {message}")
    else:
        print(f"\n[!] SISTEMA NON PRONTO: {message}")
        print("\n" + "="*60)
        print("    ATTENZIONE: La sintesi vocale NON funzionerà!")
        print("    Apri la GUI di Open WebUI Manager e vai nel tab 'Voce'")
        print("    per scaricare le voci italiane.")
        print("="*60)

        if not installed:
            print("\n    Oppure scarica da terminale con:")
            print("    - curl -X POST http://localhost:5556/install/paola")
            print("    - curl -X POST http://localhost:5556/install/riccardo")

    print(f"\n[*] Avvio servizio su http://localhost:{SERVICE_PORT}")
    print("[*] Verifica stato: http://localhost:5556/voices/check")
    print("[*] Premi Ctrl+C per fermare\n")

    app = create_app()
    uvicorn.run(app, host="0.0.0.0", port=SERVICE_PORT, log_level="info")


if __name__ == "__main__":
    main()
