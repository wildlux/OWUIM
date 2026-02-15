"""
Configurazione centralizzata dei servizi.
Tutte le URL, porte e costanti condivise del progetto.

Principi applicati:
- DIP (Dependency Inversion): Dipendi da questa configurazione, non da valori hardcoded
- DRY: Un solo posto per ogni costante
- Configurabile via variabili d'ambiente
"""

import os
import sys
import platform
import subprocess
import shutil
from pathlib import Path
from dataclasses import dataclass, field


# === Sistema Operativo ===
IS_WINDOWS = platform.system() == "Windows"
IS_LINUX = platform.system() == "Linux"
IS_MAC = platform.system() == "Darwin"

# === Directory ===
SCRIPT_DIR = Path(__file__).parent.resolve()
SCRIPTS_DIR = SCRIPT_DIR / "scripts"

# === Python Executable ===
VENV_DIR = SCRIPT_DIR / "venv"


def get_python_exe():
    """Ritorna il percorso Python del venv o sys.executable come fallback."""
    if IS_WINDOWS:
        venv_python = VENV_DIR / "Scripts" / "python.exe"
    else:
        venv_python = VENV_DIR / "bin" / "python"
    if venv_python.exists():
        return str(venv_python)
    return sys.executable


def ensure_env_file():
    """Crea il file .env con WEBUI_SECRET_KEY se non esiste."""
    env_file = SCRIPT_DIR / ".env"
    if env_file.exists():
        # Verifica che contenga WEBUI_SECRET_KEY
        content = env_file.read_text()
        if "WEBUI_SECRET_KEY=" in content:
            return True

    # Genera una secret key casuale
    import secrets
    secret_key = secrets.token_urlsafe(32)

    env_content = (
        "# Secret key per Open WebUI (generata automaticamente)\n"
        "# NON committare questo file nel repository\n"
        f"WEBUI_SECRET_KEY={secret_key}\n"
    )

    if env_file.exists():
        # Appendi la chiave al file esistente
        with open(env_file, "a") as f:
            f.write(f"\nWEBUI_SECRET_KEY={secret_key}\n")
    else:
        env_file.write_text(env_content)

    return True


def ensure_venv():
    """Crea il venv se non esiste e installa le dipendenze. Ritorna True se ok."""
    if IS_WINDOWS:
        venv_python = VENV_DIR / "Scripts" / "python.exe"
        venv_pip = VENV_DIR / "Scripts" / "pip.exe"
    else:
        venv_python = VENV_DIR / "bin" / "python"
        venv_pip = VENV_DIR / "bin" / "pip"

    if venv_python.exists():
        return True

    result = subprocess.run(
        [sys.executable, "-m", "venv", str(VENV_DIR)],
        capture_output=True
    )
    if result.returncode != 0:
        return False

    # Aggiorna pip
    subprocess.run(
        [str(venv_pip), "install", "--upgrade", "pip"],
        capture_output=True
    )

    # Installa dipendenze
    req_file = SCRIPT_DIR / "requirements.txt"
    if req_file.exists() and venv_pip.exists():
        subprocess.run(
            [str(venv_pip), "install", "-r", str(req_file)],
            capture_output=True
        )

    return venv_python.exists()


PYTHON_EXE = get_python_exe()

# === Percorsi Script Servizi (assoluti) ===
TTS_SCRIPT = SCRIPT_DIR / "tts_service" / "tts_local.py"
IMAGE_SCRIPT = SCRIPT_DIR / "image_analysis" / "image_service.py"
DOCUMENT_SCRIPT = SCRIPT_DIR / "document_service" / "document_service.py"
MCP_SCRIPT = SCRIPT_DIR / "mcp_service" / "mcp_service.py"

# === Porte Servizi (configurabili via env) ===
PORT_WEBUI = int(os.getenv("OWUI_PORT_WEBUI", "3000"))
PORT_OLLAMA = int(os.getenv("OWUI_PORT_OLLAMA", "11434"))
PORT_TTS = int(os.getenv("OWUI_PORT_TTS", "5556"))
PORT_IMAGE = int(os.getenv("OWUI_PORT_IMAGE", "5555"))
PORT_DOCUMENT = int(os.getenv("OWUI_PORT_DOCUMENT", "5557"))
PORT_MCP = int(os.getenv("OWUI_PORT_MCP", "5558"))
PORT_OPENEDAI_SPEECH = int(os.getenv("OWUI_PORT_OPENEDAI_SPEECH", "8000"))

# === URL Servizi (derivate dalle porte) ===
_HOST = os.getenv("OWUI_HOST", "localhost")

URL_WEBUI = f"http://{_HOST}:{PORT_WEBUI}"
URL_OLLAMA = f"http://{_HOST}:{PORT_OLLAMA}"
URL_TTS = f"http://{_HOST}:{PORT_TTS}"
URL_IMAGE = f"http://{_HOST}:{PORT_IMAGE}"
URL_DOCUMENT = f"http://{_HOST}:{PORT_DOCUMENT}"
URL_MCP = f"http://{_HOST}:{PORT_MCP}"
URL_OPENEDAI_SPEECH = f"http://{_HOST}:{PORT_OPENEDAI_SPEECH}"

# URL per Docker (interno al container)
DOCKER_HOST = "host.docker.internal"
URL_TTS_DOCKER = f"http://{DOCKER_HOST}:{PORT_TTS}"
URL_OPENEDAI_SPEECH_DOCKER = f"http://{DOCKER_HOST}:{PORT_OPENEDAI_SPEECH}"


@dataclass
class ServiceInfo:
    """Descrizione di un servizio."""
    name: str
    label: str
    icon: str
    port: int
    url: str
    script: str  # Path relativo allo script di avvio

    @property
    def health_url(self):
        return f"{self.url}/"


# Registry dei servizi
SERVICES = {
    "tts": ServiceInfo("tts", "TTS", "🔊", PORT_TTS, URL_TTS, "tts_service/tts_local.py"),
    "image": ServiceInfo("image", "Image", "🖼️", PORT_IMAGE, URL_IMAGE, "image_analysis/image_service.py"),
    "document": ServiceInfo("document", "Document", "📄", PORT_DOCUMENT, URL_DOCUMENT, "document_service/document_service.py"),
    "mcp": ServiceInfo("mcp", "MCP Bridge", "🔌", PORT_MCP, URL_MCP, "mcp_service/mcp_service.py"),
}


# === Docker Compose ===
def get_docker_compose_cmd():
    """Ritorna il comando docker compose corretto per il sistema."""
    if shutil.which("docker"):
        try:
            result = subprocess.run(
                ["docker", "compose", "version"],
                capture_output=True,
                timeout=5
            )
            if result.returncode == 0:
                return "docker compose"
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
    if shutil.which("docker-compose"):
        return "docker-compose"
    return "docker compose"  # Default


DOCKER_COMPOSE = get_docker_compose_cmd()

# === Layout UI ===
SPACING_LARGE = 15
SPACING_MEDIUM = 10
SPACING_SMALL = 6

# === Versione ===
APP_VERSION = "1.1.0"
APP_NAME = "Open WebUI Manager"
