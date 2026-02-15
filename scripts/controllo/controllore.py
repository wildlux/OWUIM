#!/usr/bin/env python3
"""
Controllore di Sistema - Open WebUI Manager

Verifica completa dell'installazione: Docker, Ollama, servizi locali,
dipendenze Python, configurazione, sicurezza, voci TTS, integrita' file.

Autore: Carlo
Versione: 1.0.0

Uso:
    python scripts/controllo/controllore.py                  # Controllo completo
    python scripts/controllo/controllore.py --verbose / -v   # Dettagli + suggerimenti
    python scripts/controllo/controllore.py --test / -t       # Includi pytest
    python scripts/controllo/controllore.py --fix / -f       # Auto-riparazione
    python scripts/controllo/controllore.py --json FILE      # Export JSON
    python scripts/controllo/controllore.py --quiet / -q     # Solo score
"""

import os
import sys
import json
import socket
import shutil
import argparse
import subprocess
import importlib.metadata
import importlib.util
from enum import Enum
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Optional, Dict

# ============================================================================
# SETUP PATH PER IMPORT DAL PROGETTO
# ============================================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import config  # noqa: E402
import security  # noqa: E402

# Import dinamico system_profiler (in scripts/, non package standard)
_sp_spec = importlib.util.spec_from_file_location(
    "system_profiler",
    PROJECT_ROOT / "scripts" / "system_profiler.py"
)
_sp_module = importlib.util.module_from_spec(_sp_spec)
_sp_spec.loader.exec_module(_sp_module)
get_system_profile = _sp_module.get_system_profile
SystemTier = _sp_module.SystemTier


# ============================================================================
# ENUMS E DATA CLASSES
# ============================================================================

class CheckStatus(Enum):
    """Stato di un singolo controllo."""
    OK = "OK"
    AVVISO = "AVVISO"
    ERRORE = "ERRORE"
    SALTATO = "SALTATO"

    @property
    def symbol(self) -> str:
        return {
            "OK": "[OK]",
            "AVVISO": "[!!]",
            "ERRORE": "[XX]",
            "SALTATO": "[--]",
        }[self.value]

    @property
    def color(self) -> str:
        return {
            "OK": "\033[92m",       # Verde
            "AVVISO": "\033[93m",   # Giallo
            "ERRORE": "\033[91m",   # Rosso
            "SALTATO": "\033[90m",  # Grigio
        }[self.value]


# Codici ANSI
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"


@dataclass
class CheckResult:
    """Risultato di un singolo controllo."""
    nome: str
    stato: CheckStatus
    messaggio: str
    categoria: str
    fix_hint: str = ""


@dataclass
class HealthReport:
    """Report complessivo con punteggio di salute."""
    risultati: List[CheckResult] = field(default_factory=list)
    score: int = 0
    ok_count: int = 0
    avviso_count: int = 0
    errore_count: int = 0
    saltato_count: int = 0

    def calcola_score(self):
        """Calcola il punteggio 0-100 basato sui risultati."""
        valutati = [r for r in self.risultati if r.stato != CheckStatus.SALTATO]
        total = len(valutati)
        if total == 0:
            self.score = 0
            return

        self.ok_count = sum(1 for r in self.risultati if r.stato == CheckStatus.OK)
        self.avviso_count = sum(
            1 for r in self.risultati if r.stato == CheckStatus.AVVISO
        )
        self.errore_count = sum(
            1 for r in self.risultati if r.stato == CheckStatus.ERRORE
        )
        self.saltato_count = sum(
            1 for r in self.risultati if r.stato == CheckStatus.SALTATO
        )

        punti = self.ok_count * 10 + self.avviso_count * 4
        max_punti = total * 10
        self.score = min(100, round(punti / max_punti * 100)) if max_punti > 0 else 0


# ============================================================================
# UTILITY
# ============================================================================

def _http_get(url: str, timeout: int = 5) -> Optional[dict]:
    """GET HTTP con timeout, ritorna JSON o None."""
    try:
        import requests
        resp = requests.get(url, timeout=timeout)
        if resp.status_code == 200:
            try:
                return resp.json()
            except ValueError:
                return {"status": "ok", "text": resp.text[:200]}
        return None
    except Exception:
        return None


def _port_in_use(port: int) -> bool:
    """Controlla se una porta e' in ascolto su localhost."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(1)
        return s.connect_ex(("127.0.0.1", port)) == 0


def _run_cmd(cmd: List[str], timeout: int = 10) -> Optional[str]:
    """Esegue un comando e ritorna stdout, o None se fallisce."""
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout
        )
        if result.returncode == 0:
            return result.stdout.strip()
        return None
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return None


# ============================================================================
# 1. SISTEMA
# ============================================================================

def check_sistema() -> List[CheckResult]:
    """Controlla RAM, tier, GPU, spazio disco."""
    risultati = []

    profile = get_system_profile()

    # RAM totale
    ram_ok = profile.ram_total_gb >= 4
    risultati.append(CheckResult(
        "RAM Totale",
        CheckStatus.OK if ram_ok else CheckStatus.AVVISO,
        f"{profile.ram_total_gb:.1f} GB (disponibile: {profile.ram_available_gb:.1f} GB)",
        "Sistema",
        "Chiudi applicazioni per liberare RAM" if not ram_ok else ""
    ))

    # Tier
    tier_status = {
        SystemTier.MINIMAL: CheckStatus.ERRORE,
        SystemTier.LOW: CheckStatus.AVVISO,
        SystemTier.MEDIUM: CheckStatus.OK,
        SystemTier.HIGH: CheckStatus.OK,
    }
    risultati.append(CheckResult(
        "Tier Sistema",
        tier_status[profile.tier],
        f"{profile.tier.value.upper()} (timeout LLM: {profile.timeout_llm}s)",
        "Sistema",
        "Risorse limitate: usa modelli piccoli"
        if profile.tier in (SystemTier.MINIMAL, SystemTier.LOW) else ""
    ))

    # GPU
    if profile.has_gpu:
        gpu_msg = profile.gpu_name
        if profile.gpu_vram_gb > 0:
            gpu_msg += f" ({profile.gpu_vram_gb:.1f} GB VRAM)"
        risultati.append(CheckResult("GPU", CheckStatus.OK, gpu_msg, "Sistema"))
    else:
        risultati.append(CheckResult(
            "GPU", CheckStatus.AVVISO, "Nessuna GPU rilevata (solo CPU)",
            "Sistema", "Ollama sara' piu' lento senza GPU"
        ))

    # Spazio disco
    try:
        usage = shutil.disk_usage(str(PROJECT_ROOT))
        free_gb = usage.free / (1024 ** 3)
        total_gb = usage.total / (1024 ** 3)
        if free_gb > 5:
            stato = CheckStatus.OK
        elif free_gb > 1:
            stato = CheckStatus.AVVISO
        else:
            stato = CheckStatus.ERRORE
        risultati.append(CheckResult(
            "Spazio Disco", stato,
            f"{free_gb:.1f} GB liberi su {total_gb:.0f} GB",
            "Sistema",
            "Libera spazio disco" if free_gb <= 5 else ""
        ))
    except OSError:
        risultati.append(CheckResult(
            "Spazio Disco", CheckStatus.SALTATO,
            "Impossibile verificare", "Sistema"
        ))

    return risultati


# ============================================================================
# 2. DOCKER
# ============================================================================

def check_docker() -> List[CheckResult]:
    """Controlla Docker installato, daemon attivo, compose, container."""
    risultati = []

    # Docker installato
    docker_path = shutil.which("docker")
    if not docker_path:
        risultati.append(CheckResult(
            "Docker Installato", CheckStatus.ERRORE,
            "Non trovato nel PATH",
            "Docker",
            "Installa Docker: https://docs.docker.com/get-docker/"
        ))
        return risultati

    risultati.append(CheckResult(
        "Docker Installato", CheckStatus.OK,
        f"Trovato: {docker_path}", "Docker"
    ))

    # Daemon attivo
    info = _run_cmd(["docker", "info"])
    if info is None:
        fix = "sudo systemctl start docker" if config.IS_LINUX else "Avvia Docker Desktop"
        risultati.append(CheckResult(
            "Docker Daemon", CheckStatus.ERRORE,
            "Non in esecuzione", "Docker", fix
        ))
        return risultati

    risultati.append(CheckResult(
        "Docker Daemon", CheckStatus.OK, "In esecuzione", "Docker"
    ))

    # Docker Compose
    compose_ver = _run_cmd(config.DOCKER_COMPOSE.split() + ["version"])
    if compose_ver:
        risultati.append(CheckResult(
            "Docker Compose", CheckStatus.OK,
            compose_ver.split('\n')[0], "Docker"
        ))
    else:
        risultati.append(CheckResult(
            "Docker Compose", CheckStatus.ERRORE,
            "Non disponibile", "Docker", "Installa docker-compose"
        ))

    # Container
    for container_name in ["open-webui", "openedai-speech"]:
        ps = _run_cmd([
            "docker", "inspect", "--format", "{{.State.Status}}", container_name
        ])
        if ps and "running" in ps.lower():
            risultati.append(CheckResult(
                f"Container {container_name}", CheckStatus.OK,
                "In esecuzione", "Docker"
            ))
        else:
            risultati.append(CheckResult(
                f"Container {container_name}", CheckStatus.ERRORE,
                "Non in esecuzione", "Docker",
                f"docker compose up -d {container_name}"
            ))

    return risultati


# ============================================================================
# 3. OLLAMA
# ============================================================================

def check_ollama() -> List[CheckResult]:
    """Controlla Ollama nel PATH, API raggiungibile, modelli."""
    risultati = []

    # Nel PATH
    ollama_path = shutil.which("ollama")
    if not ollama_path:
        risultati.append(CheckResult(
            "Ollama Installato", CheckStatus.ERRORE,
            "Non trovato nel PATH",
            "Ollama",
            "Installa Ollama: https://ollama.ai/download"
        ))
        return risultati

    risultati.append(CheckResult(
        "Ollama Installato", CheckStatus.OK,
        f"Trovato: {ollama_path}", "Ollama"
    ))

    # API version
    version_data = _http_get(f"{config.URL_OLLAMA}/api/version")
    if version_data:
        ver = version_data.get("version", "sconosciuta")
        risultati.append(CheckResult(
            "Ollama API", CheckStatus.OK,
            f"Versione: {ver}", "Ollama"
        ))
    else:
        risultati.append(CheckResult(
            "Ollama API", CheckStatus.ERRORE,
            f"Non raggiungibile su {config.URL_OLLAMA}",
            "Ollama", "Avvia Ollama: ollama serve"
        ))
        return risultati

    # Modelli
    tags_data = _http_get(f"{config.URL_OLLAMA}/api/tags")
    if tags_data and "models" in tags_data:
        models = tags_data["models"]
        if models:
            nomi = [m.get("name", "?") for m in models[:5]]
            extra = f" (+{len(models) - 5} altri)" if len(models) > 5 else ""
            risultati.append(CheckResult(
                "Modelli Ollama", CheckStatus.OK,
                f"{len(models)} modelli: {', '.join(nomi)}{extra}",
                "Ollama"
            ))
        else:
            risultati.append(CheckResult(
                "Modelli Ollama", CheckStatus.AVVISO,
                "Nessun modello scaricato",
                "Ollama",
                "ollama pull qwen2.5:7b-instruct-q4_K_M"
            ))
    else:
        risultati.append(CheckResult(
            "Modelli Ollama", CheckStatus.AVVISO,
            "Impossibile leggere lista modelli",
            "Ollama", ""
        ))

    return risultati


# ============================================================================
# 4. SERVIZI LOCALI
# ============================================================================

def check_servizi_locali() -> List[CheckResult]:
    """Controlla servizi da config.SERVICES + OpenedAI Speech + WebUI."""
    risultati = []

    # Servizi da config.SERVICES
    for key, svc in config.SERVICES.items():
        if _port_in_use(svc.port):
            data = _http_get(svc.health_url)
            msg = f"Attivo su porta {svc.port}"
            if data:
                msg += " (health OK)"
            risultati.append(CheckResult(
                f"Servizio {svc.label}", CheckStatus.OK, msg, "Servizi"
            ))
        else:
            risultati.append(CheckResult(
                f"Servizio {svc.label}", CheckStatus.AVVISO,
                f"Non attivo su porta {svc.port}",
                "Servizi",
                f"python {svc.script}"
            ))

    # OpenedAI Speech
    if _port_in_use(config.PORT_OPENEDAI_SPEECH):
        risultati.append(CheckResult(
            "OpenedAI Speech", CheckStatus.OK,
            f"Attivo su porta {config.PORT_OPENEDAI_SPEECH}",
            "Servizi"
        ))
    else:
        risultati.append(CheckResult(
            "OpenedAI Speech", CheckStatus.AVVISO,
            f"Non attivo su porta {config.PORT_OPENEDAI_SPEECH}",
            "Servizi", "docker compose up -d openedai-speech"
        ))

    # Open WebUI
    if _port_in_use(config.PORT_WEBUI):
        risultati.append(CheckResult(
            "Open WebUI", CheckStatus.OK,
            f"Attivo su porta {config.PORT_WEBUI}",
            "Servizi"
        ))
    else:
        risultati.append(CheckResult(
            "Open WebUI", CheckStatus.ERRORE,
            f"Non attivo su porta {config.PORT_WEBUI}",
            "Servizi", "docker compose up -d open-webui"
        ))

    return risultati


# ============================================================================
# 5. DIPENDENZE PYTHON
# ============================================================================

def check_dipendenze_python() -> List[CheckResult]:
    """Verifica dipendenze da requirements.txt con importlib.metadata."""
    risultati = []
    req_file = PROJECT_ROOT / "requirements.txt"

    if not req_file.exists():
        risultati.append(CheckResult(
            "requirements.txt", CheckStatus.ERRORE,
            "File non trovato", "Dipendenze", ""
        ))
        return risultati

    mancanti = []
    presenti = 0

    for line in req_file.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        # Parse nome pacchetto: "nome>=versione" o "nome==versione" o "nome"
        pkg_name = line.split(">=")[0].split("==")[0].split("[")[0].strip()
        if not pkg_name:
            continue

        try:
            importlib.metadata.version(pkg_name)
            presenti += 1
        except importlib.metadata.PackageNotFoundError:
            mancanti.append(pkg_name)

    if not mancanti:
        risultati.append(CheckResult(
            "Dipendenze Python", CheckStatus.OK,
            f"Tutte {presenti} dipendenze installate",
            "Dipendenze"
        ))
    else:
        extra = f" (+{len(mancanti) - 5})" if len(mancanti) > 5 else ""
        risultati.append(CheckResult(
            "Dipendenze Python", CheckStatus.ERRORE,
            f"{len(mancanti)} mancanti: {', '.join(mancanti[:5])}{extra}",
            "Dipendenze",
            "pip install -r requirements.txt"
        ))

    return risultati


# ============================================================================
# 6. CONFIGURAZIONE
# ============================================================================

def check_configurazione() -> List[CheckResult]:
    """Controlla config.py, porte senza conflitti, docker-compose.yml."""
    risultati = []

    # config.py caricabile (se siamo qui, lo e' gia')
    risultati.append(CheckResult(
        "config.py", CheckStatus.OK,
        f"{config.APP_NAME} v{config.APP_VERSION}",
        "Configurazione"
    ))

    # docker-compose.yml presente
    dc_file = PROJECT_ROOT / "docker-compose.yml"
    if dc_file.exists():
        risultati.append(CheckResult(
            "docker-compose.yml", CheckStatus.OK,
            "Presente", "Configurazione"
        ))
    else:
        risultati.append(CheckResult(
            "docker-compose.yml", CheckStatus.ERRORE,
            "Non trovato", "Configurazione", ""
        ))

    # Conflitti porte
    porte: Dict[str, int] = {
        "WebUI": config.PORT_WEBUI,
        "Ollama": config.PORT_OLLAMA,
        "TTS": config.PORT_TTS,
        "Image": config.PORT_IMAGE,
        "Document": config.PORT_DOCUMENT,
        "MCP": config.PORT_MCP,
        "OpenedAI Speech": config.PORT_OPENEDAI_SPEECH,
    }
    valori = list(porte.values())
    duplicati = [p for p in set(valori) if valori.count(p) > 1]

    if duplicati:
        nomi = [n for n, p in porte.items() if p in duplicati]
        risultati.append(CheckResult(
            "Conflitto Porte", CheckStatus.ERRORE,
            f"Porte duplicate: {', '.join(nomi)}",
            "Configurazione",
            "Modifica le porte in config.py o variabili d'ambiente"
        ))
    else:
        risultati.append(CheckResult(
            "Porte Configurate", CheckStatus.OK,
            f"{len(porte)} porte univoche",
            "Configurazione"
        ))

    return risultati


# ============================================================================
# 7. SICUREZZA
# ============================================================================

def check_sicurezza() -> List[CheckResult]:
    """Controlla security.py, .api_key, CORS, binding host."""
    risultati = []

    # security.py caricabile
    risultati.append(CheckResult(
        "security.py", CheckStatus.OK,
        "Modulo caricato", "Sicurezza"
    ))

    # .api_key esiste
    api_key_file = PROJECT_ROOT / ".api_key"
    if api_key_file.exists():
        if config.IS_LINUX or config.IS_MAC:
            mode = oct(api_key_file.stat().st_mode)[-3:]
            if mode == "600":
                risultati.append(CheckResult(
                    "API Key", CheckStatus.OK,
                    f"File presente, permessi corretti ({mode})",
                    "Sicurezza"
                ))
            else:
                risultati.append(CheckResult(
                    "API Key", CheckStatus.AVVISO,
                    f"Permessi: {mode} (dovrebbe essere 600)",
                    "Sicurezza", "chmod 600 .api_key"
                ))
        else:
            risultati.append(CheckResult(
                "API Key", CheckStatus.OK,
                "File presente", "Sicurezza"
            ))
    else:
        risultati.append(CheckResult(
            "API Key", CheckStatus.AVVISO,
            "File non trovato (verra' generato al primo avvio)",
            "Sicurezza", ""
        ))

    # CORS senza wildcard
    has_wildcard = "*" in security.ALLOWED_ORIGINS
    if has_wildcard:
        risultati.append(CheckResult(
            "CORS", CheckStatus.ERRORE,
            "Wildcard * presente nelle origini consentite",
            "Sicurezza",
            "Rimuovi * da ALLOWED_ORIGINS in security.py"
        ))
    else:
        risultati.append(CheckResult(
            "CORS", CheckStatus.OK,
            f"{len(security.ALLOWED_ORIGINS)} origini specifiche (no wildcard)",
            "Sicurezza"
        ))

    # SAFE_HOST
    if security.SAFE_HOST == "127.0.0.1":
        risultati.append(CheckResult(
            "Binding Host", CheckStatus.OK,
            f"Servizi su {security.SAFE_HOST} (solo locale)",
            "Sicurezza"
        ))
    else:
        risultati.append(CheckResult(
            "Binding Host", CheckStatus.AVVISO,
            f"Servizi su {security.SAFE_HOST} (non localhost)",
            "Sicurezza",
            "Imposta SAFE_HOST = '127.0.0.1' in security.py"
        ))

    return risultati


# ============================================================================
# 8. VOCI TTS
# ============================================================================

def check_voci_tts() -> List[CheckResult]:
    """Controlla voci Piper (.onnx) in tts_service/piper_models/."""
    risultati = []

    models_dir = PROJECT_ROOT / "tts_service" / "piper_models"
    if not models_dir.exists():
        risultati.append(CheckResult(
            "Directory Voci TTS", CheckStatus.AVVISO,
            "tts_service/piper_models/ non esiste",
            "TTS", "python tts_service/download_voices.py"
        ))
        return risultati

    onnx_files = list(models_dir.glob("*.onnx"))
    json_files = list(models_dir.glob("*.onnx.json"))

    if onnx_files:
        nomi = [f.stem for f in onnx_files[:3]]
        extra = f" (+{len(onnx_files) - 3})" if len(onnx_files) > 3 else ""
        risultati.append(CheckResult(
            "Voci TTS", CheckStatus.OK,
            f"{len(onnx_files)} voci: {', '.join(nomi)}{extra}",
            "TTS"
        ))

        # Controlla che ogni .onnx abbia il suo .json
        onnx_names = {f.name for f in onnx_files}
        json_for = {f.name.replace(".onnx.json", ".onnx") for f in json_files}
        missing_json = onnx_names - json_for
        if missing_json:
            risultati.append(CheckResult(
                "Config Voci TTS", CheckStatus.AVVISO,
                f"{len(missing_json)} voci senza file .json config",
                "TTS", "Riscarica le voci con download_voices.py"
            ))
    else:
        risultati.append(CheckResult(
            "Voci TTS", CheckStatus.AVVISO,
            "Nessuna voce .onnx trovata",
            "TTS", "python tts_service/download_voices.py"
        ))

    # Piper eseguibile
    piper_path = shutil.which("piper")
    piper_local = PROJECT_ROOT / "tts_service" / "piper"
    if piper_path or piper_local.exists():
        found = piper_path or str(piper_local)
        risultati.append(CheckResult(
            "Piper TTS", CheckStatus.OK,
            f"Trovato: {found}", "TTS"
        ))
    else:
        risultati.append(CheckResult(
            "Piper TTS", CheckStatus.AVVISO,
            "Eseguibile piper non trovato (edge-tts come fallback)",
            "TTS", ""
        ))

    return risultati


# ============================================================================
# 9. INTEGRITA' FILE
# ============================================================================

def check_integrita_file() -> List[CheckResult]:
    """Verifica presenza dei file critici del progetto."""
    risultati = []

    file_critici = [
        "config.py",
        "security.py",
        "openwebui_gui.py",
        "openwebui_gui_lite.py",
        "docker-compose.yml",
        "requirements.txt",
        "run_gui.sh",
        "dist/build.py",
        "tts_service/tts_local.py",
        "image_analysis/image_service.py",
        "document_service/document_service.py",
        "mcp_service/mcp_service.py",
        "scripts/system_profiler.py",
        "scripts/install_tools.py",
        "scripts/start_all.sh",
    ]

    presenti = 0
    mancanti = []

    for f in file_critici:
        path = PROJECT_ROOT / f
        if path.exists():
            presenti += 1
        else:
            mancanti.append(f)

    if not mancanti:
        risultati.append(CheckResult(
            "File Critici", CheckStatus.OK,
            f"Tutti {presenti} file presenti",
            "Integrita'"
        ))
    else:
        extra = f" (+{len(mancanti) - 4})" if len(mancanti) > 4 else ""
        risultati.append(CheckResult(
            "File Critici", CheckStatus.ERRORE,
            f"{len(mancanti)} mancanti: {', '.join(mancanti[:4])}{extra}",
            "Integrita'", ""
        ))

    return risultati


# ============================================================================
# 10. TOOLS
# ============================================================================

def check_tools() -> List[CheckResult]:
    """Verifica i file .py in Tools OWUI/."""
    risultati = []

    tools_dir = PROJECT_ROOT / "Tools OWUI"
    if not tools_dir.exists():
        risultati.append(CheckResult(
            "Directory Tools", CheckStatus.ERRORE,
            "Tools OWUI/ non trovata",
            "Tools", ""
        ))
        return risultati

    py_files = sorted([
        f for f in tools_dir.glob("*.py") if f.name != "__init__.py"
    ])

    if len(py_files) >= 14:
        nomi = [f.stem for f in py_files[:4]]
        risultati.append(CheckResult(
            "Tools Open WebUI", CheckStatus.OK,
            f"{len(py_files)} tools: {', '.join(nomi)}...",
            "Tools"
        ))
    elif py_files:
        risultati.append(CheckResult(
            "Tools Open WebUI", CheckStatus.AVVISO,
            f"Solo {len(py_files)} tools trovati (attesi >= 14)",
            "Tools", "Verifica la cartella Tools OWUI/"
        ))
    else:
        risultati.append(CheckResult(
            "Tools Open WebUI", CheckStatus.ERRORE,
            "Nessun tool trovato",
            "Tools", "python scripts/install_tools.py"
        ))

    return risultati


# ============================================================================
# 11. TEST (solo con --test)
# ============================================================================

def check_test() -> List[CheckResult]:
    """Esegue pytest e riporta i risultati."""
    risultati = []

    pytest_path = shutil.which("pytest")
    if not pytest_path:
        risultati.append(CheckResult(
            "Pytest", CheckStatus.SALTATO,
            "pytest non installato",
            "Test", "pip install pytest"
        ))
        return risultati

    output = _run_cmd(
        [pytest_path, str(PROJECT_ROOT), "-v", "--tb=short", "-q"],
        timeout=120
    )

    if output is not None:
        lines = output.strip().splitlines()
        summary = lines[-1] if lines else "Nessun output"

        if "failed" in summary.lower():
            risultati.append(CheckResult(
                "Test Suite", CheckStatus.ERRORE, summary, "Test", ""
            ))
        elif "passed" in summary.lower():
            risultati.append(CheckResult(
                "Test Suite", CheckStatus.OK, summary, "Test"
            ))
        else:
            risultati.append(CheckResult(
                "Test Suite", CheckStatus.AVVISO, summary, "Test"
            ))
    else:
        risultati.append(CheckResult(
            "Test Suite", CheckStatus.ERRORE,
            "Esecuzione fallita o timeout",
            "Test", ""
        ))

    return risultati


# ============================================================================
# AUTO-FIX
# ============================================================================

def attempt_fixes(risultati: List[CheckResult]) -> List[str]:
    """Tenta auto-riparazione per errori/avvisi con fix_hint."""
    azioni = []
    fix_eseguiti = set()

    for r in risultati:
        if r.stato not in (CheckStatus.ERRORE, CheckStatus.AVVISO):
            continue
        if not r.fix_hint:
            continue

        hint = r.fix_hint

        # Evita duplicati
        if hint in fix_eseguiti:
            continue

        # Docker daemon
        if "systemctl start docker" in hint and config.IS_LINUX:
            fix_eseguiti.add(hint)
            print(f"  FIX: Avvio Docker daemon...")
            result = _run_cmd(
                ["sudo", "systemctl", "start", "docker"], timeout=30
            )
            azioni.append(
                f"Docker daemon: {'OK' if result is not None else 'Fallito'}"
            )

        # Docker compose up
        elif "docker compose up -d" in hint:
            # Avvia tutti i container in una volta sola
            if "docker compose up -d" not in fix_eseguiti:
                fix_eseguiti.add("docker compose up -d")
                print(f"  FIX: Avvio container...")
                result = _run_cmd(
                    config.DOCKER_COMPOSE.split() + [
                        "-f", str(PROJECT_ROOT / "docker-compose.yml"),
                        "up", "-d"
                    ],
                    timeout=60
                )
                azioni.append(
                    f"Docker compose up: {'OK' if result is not None else 'Fallito'}"
                )

        # pip install
        elif "pip install -r requirements.txt" in hint:
            fix_eseguiti.add(hint)
            print(f"  FIX: Installazione dipendenze...")
            result = _run_cmd(
                [sys.executable, "-m", "pip", "install",
                 "-r", str(PROJECT_ROOT / "requirements.txt")],
                timeout=120
            )
            azioni.append(
                f"pip install: {'OK' if result is not None else 'Fallito'}"
            )

        # chmod .api_key
        elif "chmod 600 .api_key" in hint:
            fix_eseguiti.add(hint)
            try:
                (PROJECT_ROOT / ".api_key").chmod(0o600)
                azioni.append("chmod .api_key: OK")
            except OSError as e:
                azioni.append(f"chmod .api_key: Fallito ({e})")

        # Download voci TTS
        elif "download_voices.py" in hint:
            fix_eseguiti.add(hint)
            dv_script = PROJECT_ROOT / "tts_service" / "download_voices.py"
            if dv_script.exists():
                print(f"  FIX: Download voci TTS...")
                result = _run_cmd(
                    [sys.executable, str(dv_script)],
                    timeout=120
                )
                azioni.append(
                    f"Download voci: {'OK' if result is not None else 'Fallito'}"
                )

    return azioni


# ============================================================================
# REPORT FORMATTER
# ============================================================================

class ReportFormatter:
    """Formatta l'output con box Unicode e colori ANSI."""
    WIDTH = 62

    @staticmethod
    def header():
        w = ReportFormatter.WIDTH
        title = "CONTROLLORE DI SISTEMA - Open WebUI Manager"
        print(f"\n{BOLD}\u2554{'\u2550' * w}\u2557")
        print(f"\u2551{title:^{w}}\u2551")
        print(f"\u255a{'\u2550' * w}\u255d{RESET}\n")

    @staticmethod
    def section(nome: str):
        padding = ReportFormatter.WIDTH - len(nome) - 5
        print(f"  {BOLD}\u2500\u2500\u2500 {nome} {'\u2500' * padding}{RESET}")

    @staticmethod
    def result(r: CheckResult, verbose: bool = False):
        print(f"  {r.stato.color}{r.stato.symbol}{RESET} {r.nome}: {r.messaggio}")
        if verbose and r.fix_hint:
            print(f"      {DIM}\u2192 {r.fix_hint}{RESET}")

    @staticmethod
    def summary(report: HealthReport):
        w = ReportFormatter.WIDTH

        # Barra progresso
        filled = round(report.score / 100 * 30)
        bar = "\u2588" * filled + "\u2591" * (30 - filled)

        # Colore score
        if report.score >= 80:
            score_color = "\033[92m"   # Verde
        elif report.score >= 50:
            score_color = "\033[93m"   # Giallo
        else:
            score_color = "\033[91m"   # Rosso

        # Verdetto
        if report.score >= 80:
            verdetto = "Sistema in buona salute"
        elif report.score >= 50:
            verdetto = "Alcuni problemi da risolvere"
        else:
            verdetto = "Intervento necessario"

        print(f"\n{BOLD}\u2554{'\u2550' * w}\u2557")
        print(f"\u2551{'RIEPILOGO':^{w}}\u2551")
        print(f"\u2560{'\u2550' * w}\u2563{RESET}")
        print(f"  Punteggio:  {score_color}{bar} {report.score}/100{RESET}")
        print(
            f"  Risultati:  {report.ok_count} OK  "
            f"{report.avviso_count} AVVISI  "
            f"{report.errore_count} ERRORI  "
            f"{report.saltato_count} SALTATI"
        )
        print(f"  Verdetto:   {score_color}{verdetto}{RESET}")
        print(f"{BOLD}\u255a{'\u2550' * w}\u255d{RESET}\n")

    @staticmethod
    def fixes(azioni: List[str]):
        if not azioni:
            return
        padding = ReportFormatter.WIDTH - 15
        print(
            f"\n  {BOLD}\u2500\u2500\u2500 Auto-Fix "
            f"{'\u2500' * padding}{RESET}"
        )
        for a in azioni:
            print(f"  \u2192 {a}")


# ============================================================================
# MAIN
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description=(
            f"Controllore di Sistema - "
            f"{config.APP_NAME} v{config.APP_VERSION}"
        )
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true",
        help="Mostra dettagli e suggerimenti fix"
    )
    parser.add_argument(
        "-t", "--test", action="store_true",
        help="Includi esecuzione test pytest"
    )
    parser.add_argument(
        "-f", "--fix", action="store_true",
        help="Tenta auto-riparazione problemi"
    )
    parser.add_argument(
        "--json", metavar="FILE",
        help="Esporta report in formato JSON"
    )
    parser.add_argument(
        "-q", "--quiet", action="store_true",
        help="Mostra solo il punteggio"
    )

    args = parser.parse_args()

    # Raccogli risultati
    report = HealthReport()

    checks = [
        ("Sistema", check_sistema),
        ("Docker", check_docker),
        ("Ollama", check_ollama),
        ("Servizi", check_servizi_locali),
        ("Dipendenze", check_dipendenze_python),
        ("Configurazione", check_configurazione),
        ("Sicurezza", check_sicurezza),
        ("TTS", check_voci_tts),
        ("Integrita'", check_integrita_file),
        ("Tools", check_tools),
    ]

    if args.test:
        checks.append(("Test", check_test))

    if not args.quiet:
        ReportFormatter.header()

    for cat_name, check_fn in checks:
        risultati = check_fn()
        report.risultati.extend(risultati)

        if not args.quiet:
            ReportFormatter.section(cat_name)
            for r in risultati:
                ReportFormatter.result(r, verbose=args.verbose)
            print()

    report.calcola_score()

    # Auto-fix
    if args.fix:
        azioni = attempt_fixes(report.risultati)
        if not args.quiet:
            ReportFormatter.fixes(azioni)

    # Output
    if args.quiet:
        print(f"{report.score}/100")
    else:
        ReportFormatter.summary(report)

    # Export JSON
    if args.json:
        data = {
            "app": config.APP_NAME,
            "version": config.APP_VERSION,
            "score": report.score,
            "ok": report.ok_count,
            "avvisi": report.avviso_count,
            "errori": report.errore_count,
            "saltati": report.saltato_count,
            "risultati": [
                {
                    "nome": r.nome,
                    "stato": r.stato.value,
                    "messaggio": r.messaggio,
                    "categoria": r.categoria,
                    "fix_hint": r.fix_hint,
                }
                for r in report.risultati
            ]
        }
        json_path = Path(args.json)
        json_path.write_text(json.dumps(data, indent=2, ensure_ascii=False))
        if not args.quiet:
            print(f"  Report JSON salvato: {json_path}\n")

    sys.exit(0 if report.score >= 50 else 1)


if __name__ == "__main__":
    main()
