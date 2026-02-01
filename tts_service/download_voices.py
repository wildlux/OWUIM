#!/usr/bin/env python3
"""
Download Voci Italiane per TTS Locale

Scarica automaticamente:
- Piper TTS (eseguibile)
- Voce Paola (femminile, qualità media)
- Voce Riccardo (maschile, veloce)

Autore: Carlo
"""

import os
import sys
import platform
import shutil
import tarfile
import zipfile
from pathlib import Path

try:
    import requests
except ImportError:
    print("[X] Libreria 'requests' non installata!")
    print("    Esegui: pip install requests")
    sys.exit(1)


# Configurazione
SCRIPT_DIR = Path(__file__).parent
MODELS_DIR = SCRIPT_DIR / "piper_models"

# URL modelli Piper
PIPER_RELEASES_URL = "https://github.com/rhasspy/piper/releases/latest/download"
PIPER_VOICES_URL = "https://huggingface.co/rhasspy/piper-voices/resolve/main/it/it_IT"

VOICES = {
    "paola": {
        "name": "Paola",
        "gender": "Femminile",
        "quality": "medium",
        "files": [
            ("it_IT-paola-medium.onnx", f"{PIPER_VOICES_URL}/paola/medium/it_IT-paola-medium.onnx"),
            ("it_IT-paola-medium.onnx.json", f"{PIPER_VOICES_URL}/paola/medium/it_IT-paola-medium.onnx.json"),
        ]
    },
    "riccardo": {
        "name": "Riccardo",
        "gender": "Maschile",
        "quality": "x_low",
        "files": [
            ("it_IT-riccardo-x_low.onnx", f"{PIPER_VOICES_URL}/riccardo/x_low/it_IT-riccardo-x_low.onnx"),
            ("it_IT-riccardo-x_low.onnx.json", f"{PIPER_VOICES_URL}/riccardo/x_low/it_IT-riccardo-x_low.onnx.json"),
        ]
    }
}


def print_header():
    """Stampa header."""
    print("""
╔══════════════════════════════════════════════════════════════╗
║      DOWNLOAD VOCI ITALIANE - Piper TTS                      ║
╠══════════════════════════════════════════════════════════════╣
║  Questo script scarica:                                      ║
║  • Piper TTS (eseguibile)                                    ║
║  • Voce Paola (femminile)                                    ║
║  • Voce Riccardo (maschile)                                  ║
╚══════════════════════════════════════════════════════════════╝
    """)


def get_piper_url():
    """Ottiene URL corretto per il sistema operativo."""
    system = platform.system().lower()
    machine = platform.machine().lower()

    if system == "linux":
        if "arm" in machine or "aarch64" in machine:
            arch = "aarch64"
        else:
            arch = "x86_64"
        return f"{PIPER_RELEASES_URL}/piper_linux_{arch}.tar.gz"
    elif system == "windows":
        return f"{PIPER_RELEASES_URL}/piper_windows_amd64.zip"
    elif system == "darwin":
        return f"{PIPER_RELEASES_URL}/piper_macos_x64.tar.gz"
    else:
        raise Exception(f"Sistema non supportato: {system}")


def download_file(url: str, dest: Path, desc: str = None) -> bool:
    """Scarica un file con progress bar."""
    if desc:
        print(f"\n[*] {desc}")
    print(f"    URL: {url}")
    print(f"    Destinazione: {dest}")

    try:
        resp = requests.get(url, stream=True, timeout=120)
        resp.raise_for_status()

        total = int(resp.headers.get('content-length', 0))
        downloaded = 0

        with open(dest, 'wb') as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)
                downloaded += len(chunk)
                if total > 0:
                    pct = int(downloaded / total * 100)
                    bar = "█" * (pct // 5) + "░" * (20 - pct // 5)
                    print(f"\r    [{bar}] {pct}% ({downloaded // 1024} KB)", end="", flush=True)

        print(f"\n    [✓] Completato!")
        return True

    except Exception as e:
        print(f"\n    [X] Errore: {e}")
        if dest.exists():
            dest.unlink()
        return False


def download_piper():
    """Scarica e installa Piper TTS."""
    print("\n" + "=" * 60)
    print("STEP 1: Download Piper TTS")
    print("=" * 60)

    # Verifica se già installato
    piper_exe = MODELS_DIR / "piper" / "piper"
    if platform.system().lower() == "windows":
        piper_exe = MODELS_DIR / "piper" / "piper.exe"

    if piper_exe.exists():
        print(f"[✓] Piper già installato: {piper_exe}")
        return True

    # Scarica
    url = get_piper_url()
    filename = url.split("/")[-1]
    archive_path = MODELS_DIR / filename

    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    if not download_file(url, archive_path, "Scaricamento Piper TTS..."):
        return False

    # Estrai
    print("\n[*] Estrazione archivio...")
    try:
        if filename.endswith(".tar.gz"):
            with tarfile.open(archive_path, 'r:gz') as tar:
                tar.extractall(MODELS_DIR)
        else:
            with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                zip_ref.extractall(MODELS_DIR)

        archive_path.unlink()
        print("    [✓] Estrazione completata!")

        # Rendi eseguibile su Linux/Mac
        if platform.system().lower() != "windows":
            piper_path = MODELS_DIR / "piper" / "piper"
            if piper_path.exists():
                os.chmod(piper_path, 0o755)
                print(f"    [✓] Permessi impostati: {piper_path}")

        return True

    except Exception as e:
        print(f"    [X] Errore estrazione: {e}")
        return False


def download_voice(voice_id: str):
    """Scarica una voce."""
    if voice_id not in VOICES:
        print(f"[X] Voce non trovata: {voice_id}")
        return False

    voice = VOICES[voice_id]
    print(f"\n{'=' * 60}")
    print(f"Download Voce: {voice['name']} ({voice['gender']})")
    print("=" * 60)

    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    for filename, url in voice["files"]:
        dest = MODELS_DIR / filename

        if dest.exists():
            print(f"[✓] {filename} già presente")
            continue

        if not download_file(url, dest, f"Scaricamento {filename}..."):
            return False

    print(f"\n[✓] Voce {voice['name']} installata con successo!")
    return True


def verify_installation():
    """Verifica l'installazione."""
    print("\n" + "=" * 60)
    print("VERIFICA INSTALLAZIONE")
    print("=" * 60)

    # Verifica Piper
    piper_path = None
    for name in ["piper", "piper.exe"]:
        path = MODELS_DIR / "piper" / name
        if path.exists():
            piper_path = path
            break

    if piper_path:
        print(f"[✓] Piper TTS: {piper_path}")
    else:
        print("[X] Piper TTS: NON TROVATO")

    # Verifica voci
    for voice_id, voice in VOICES.items():
        model_file = MODELS_DIR / voice["files"][0][0]
        config_file = MODELS_DIR / voice["files"][1][0]

        if model_file.exists() and config_file.exists():
            print(f"[✓] Voce {voice['name']}: installata")
        else:
            print(f"[X] Voce {voice['name']}: NON installata")


def test_voice():
    """Test opzionale della voce."""
    print("\n" + "=" * 60)
    print("TEST VOCE (opzionale)")
    print("=" * 60)

    piper_path = None
    for name in ["piper", "piper.exe"]:
        path = MODELS_DIR / "piper" / name
        if path.exists():
            piper_path = path
            break

    if not piper_path:
        print("[!] Piper non trovato, skip test")
        return

    model_file = MODELS_DIR / "it_IT-paola-medium.onnx"
    if not model_file.exists():
        model_file = MODELS_DIR / "it_IT-riccardo-x_low.onnx"
    if not model_file.exists():
        print("[!] Nessuna voce installata, skip test")
        return

    config_file = Path(str(model_file) + ".json")

    print(f"[*] Test con: {model_file.name}")

    import subprocess
    import tempfile

    test_text = "Ciao! Questo è un test della sintesi vocale italiana."

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp_path = tmp.name

    try:
        result = subprocess.run(
            [str(piper_path), "--model", str(model_file), "--config", str(config_file), "--output_file", tmp_path],
            input=test_text.encode('utf-8'),
            capture_output=True,
            timeout=30
        )

        if result.returncode == 0 and os.path.exists(tmp_path):
            size = os.path.getsize(tmp_path)
            print(f"[✓] Audio generato: {size} bytes")

            # Prova a riprodurre
            if platform.system().lower() == "linux":
                subprocess.Popen(["xdg-open", tmp_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            elif platform.system().lower() == "darwin":
                subprocess.Popen(["open", tmp_path])
            elif platform.system().lower() == "windows":
                os.startfile(tmp_path)

            print("[✓] Audio in riproduzione...")
        else:
            print(f"[X] Errore: {result.stderr.decode() if result.stderr else 'sconosciuto'}")

    except Exception as e:
        print(f"[X] Errore test: {e}")


def main():
    """Entry point."""
    print_header()

    print(f"[*] Directory modelli: {MODELS_DIR}")
    print(f"[*] Sistema: {platform.system()} {platform.machine()}")

    # Step 1: Download Piper
    if not download_piper():
        print("\n[X] Errore durante il download di Piper. Riprova.")
        input("\nPremi INVIO per uscire...")
        return

    # Step 2: Download voci
    for voice_id in VOICES:
        if not download_voice(voice_id):
            print(f"\n[!] Errore durante il download della voce {voice_id}")

    # Verifica
    verify_installation()

    # Test opzionale
    try:
        risposta = input("\nVuoi eseguire un test audio? [s/N]: ").strip().lower()
        if risposta == 's':
            test_voice()
    except:
        pass

    print("\n" + "=" * 60)
    print("COMPLETATO!")
    print("=" * 60)
    print("""
Ora puoi:
1. Avviare il servizio TTS:
   python tts_service/tts_local.py

2. Usarlo in Open WebUI aggiungendo al docker-compose.yml:
   AUDIO_TTS_ENGINE=openai
   AUDIO_TTS_OPENAI_API_BASE_URL=http://host.docker.internal:5556/v1
   AUDIO_TTS_OPENAI_API_KEY=sk-local
   AUDIO_TTS_VOICE=paola
    """)

    input("\nPremi INVIO per uscire...")


if __name__ == "__main__":
    main()
