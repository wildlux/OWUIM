"""
Configurazione centralizzata dei servizi.
Tutte le URL, porte e costanti condivise del progetto.

Principi applicati:
- DIP (Dependency Inversion): Dipendi da questa configurazione, non da valori hardcoded
- DRY: Un solo posto per ogni costante
- Configurabile via variabili d'ambiente
"""

import os
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

# === Porte Servizi (configurabili via env) ===
PORT_WEBUI = int(os.getenv("OWUI_PORT_WEBUI", "3000"))
PORT_OLLAMA = int(os.getenv("OWUI_PORT_OLLAMA", "11434"))
PORT_TTS = int(os.getenv("OWUI_PORT_TTS", "5556"))
PORT_IMAGE = int(os.getenv("OWUI_PORT_IMAGE", "5555"))
PORT_DOCUMENT = int(os.getenv("OWUI_PORT_DOCUMENT", "5557"))
PORT_MCP = int(os.getenv("OWUI_PORT_MCP", "5558"))

# === URL Servizi (derivate dalle porte) ===
_HOST = os.getenv("OWUI_HOST", "localhost")

URL_WEBUI = f"http://{_HOST}:{PORT_WEBUI}"
URL_OLLAMA = f"http://{_HOST}:{PORT_OLLAMA}"
URL_TTS = f"http://{_HOST}:{PORT_TTS}"
URL_IMAGE = f"http://{_HOST}:{PORT_IMAGE}"
URL_DOCUMENT = f"http://{_HOST}:{PORT_DOCUMENT}"
URL_MCP = f"http://{_HOST}:{PORT_MCP}"

# URL per Docker (interno al container)
DOCKER_HOST = "host.docker.internal"
URL_TTS_DOCKER = f"http://{DOCKER_HOST}:{PORT_TTS}"


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
