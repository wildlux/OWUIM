"""
Thread per operazioni in background.

Principi applicati:
- SRP: Ogni thread ha una sola responsabilita'
- Programmazione difensiva: Eccezioni specifiche, no bare except
"""

import socket
import subprocess
import time
import shutil
import logging

from PyQt5.QtCore import QThread, pyqtSignal

from config import (
    IS_WINDOWS, SCRIPT_DIR, DOCKER_COMPOSE,
    URL_WEBUI, URL_OLLAMA, URL_TTS,
    PORT_WEBUI, PORT_OLLAMA,
    VENV_DIR, ensure_venv, ensure_env_file,
)

try:
    from translations import get_text
except ImportError:
    def get_text(key, lang="it", **kwargs): return key

logger = logging.getLogger(__name__)


class StartupThread(QThread):
    """Thread per avvio automatico di Docker, Ollama e Open WebUI."""
    progress_signal = pyqtSignal(str, int)  # messaggio, percentuale
    finished_signal = pyqtSignal(bool, str)  # successo, messaggio

    def __init__(self, lang="it", parent=None):
        super().__init__(parent)
        self._lang = lang

    def _t(self, key, **kwargs):
        return get_text(key, self._lang, **kwargs)

    def run(self):
        try:
            # [0/5] Verifica ambiente Python (venv)
            self.progress_signal.emit(self._t("startup_checking_venv"), 3)
            venv_python = VENV_DIR / ("Scripts/python.exe" if IS_WINDOWS else "bin/python")
            if not venv_python.exists():
                self.progress_signal.emit(self._t("startup_creating_venv"), 5)
                ensure_venv()

            # Genera .env con WEBUI_SECRET_KEY se mancante
            ensure_env_file()

            # [1/5] Verifica Docker
            self.progress_signal.emit(self._t("startup_checking_docker"), 10)
            if not self._check_docker():
                if IS_WINDOWS:
                    self.progress_signal.emit(self._t("startup_starting_docker"), 15)
                    if not self._start_docker_windows():
                        self.finished_signal.emit(False, self._t("startup_docker_unavailable"))
                        return
                else:
                    self.finished_signal.emit(False, self._t("startup_docker_unavailable_linux"))
                    return
            self.progress_signal.emit(self._t("startup_docker_ok"), 25)

            # [2/5] Verifica Ollama
            self.progress_signal.emit(self._t("startup_checking_ollama"), 30)
            if not self._check_ollama():
                self.progress_signal.emit(self._t("startup_starting_ollama"), 35)
                if not self._start_ollama():
                    self.finished_signal.emit(False, self._t("startup_ollama_unavailable"))
                    return
            self.progress_signal.emit(self._t("startup_ollama_ok"), 50)

            # [3/5] Avvia container
            self.progress_signal.emit(self._t("startup_starting_webui"), 55)
            if not self._start_containers():
                self.progress_signal.emit(self._t("startup_downloading_image"), 60)
                self._pull_image()
                if not self._start_containers():
                    self.finished_signal.emit(False, self._t("startup_containers_failed"))
                    return
            self.progress_signal.emit(self._t("startup_container_started"), 75)

            # [4/5] Attesa servizio pronto
            self.progress_signal.emit(self._t("startup_waiting_service"), 80)
            for i in range(30):
                if self._check_webui():
                    break
                time.sleep(2)
                self.progress_signal.emit(self._t("startup_waiting_service_msg", i=f"{i+1}"), 80 + i // 2)

            # [5/5] Completato
            self.progress_signal.emit(self._t("startup_ready"), 100)
            time.sleep(0.5)
            self.finished_signal.emit(True, self._t("startup_all_started"))

        except Exception as e:
            logger.error("Errore durante startup: %s", e)
            self.finished_signal.emit(False, f"Errore: {str(e)}")

    def _check_docker(self):
        try:
            result = subprocess.run(["docker", "info"], capture_output=True, timeout=10)
            return result.returncode == 0
        except FileNotFoundError:
            logger.warning("Docker non trovato nel PATH")
            return False
        except subprocess.TimeoutExpired:
            logger.warning("Docker non risponde (timeout)")
            return False

    def _start_docker_windows(self):
        try:
            import os
            docker_paths = [
                r"C:\Program Files\Docker\Docker\Docker Desktop.exe",
                os.path.expandvars(r"%LOCALAPPDATA%\Docker\Docker Desktop.exe"),
                os.path.expandvars(r"%PROGRAMFILES%\Docker\Docker\Docker Desktop.exe"),
            ]
            for path in docker_paths:
                if os.path.exists(path):
                    subprocess.Popen([path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    break
            else:
                subprocess.Popen(
                    ["cmd", "/c", "start", "", "Docker Desktop"],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                )
            for i in range(40):
                time.sleep(3)
                self.progress_signal.emit(self._t("startup_waiting_docker", i=f"{i+1}"), 15 + i // 4)
                if self._check_docker():
                    return True
            return False
        except (FileNotFoundError, OSError) as e:
            logger.error("Impossibile avviare Docker Desktop: %s", e)
            return False

    def _check_ollama(self):
        try:
            result = subprocess.run(
                ["curl", "-s", f"{URL_OLLAMA}/api/version"],
                capture_output=True, timeout=5
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def _start_ollama(self):
        try:
            if IS_WINDOWS:
                ollama_cmd = shutil.which("ollama") or "ollama"
                subprocess.Popen(
                    ["cmd", "/c", "start", "/min", "", ollama_cmd, "serve"],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                )
            else:
                subprocess.Popen(
                    ["ollama", "serve"],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                )
            for i in range(20):
                time.sleep(2)
                self.progress_signal.emit(self._t("startup_waiting_ollama_msg", i=f"{i+1}"), 35 + i // 2)
                if self._check_ollama():
                    return True
            return False
        except FileNotFoundError:
            logger.error("Ollama non trovato nel PATH")
            return False

    def _start_containers(self):
        try:
            result = subprocess.run(
                f"{DOCKER_COMPOSE} up -d",
                shell=True, capture_output=True, cwd=SCRIPT_DIR, timeout=120
            )
            return result.returncode == 0
        except subprocess.TimeoutExpired:
            logger.error("Timeout avvio container Docker")
            return False

    def _pull_image(self):
        try:
            subprocess.run(
                f"{DOCKER_COMPOSE} pull",
                shell=True, capture_output=True, cwd=SCRIPT_DIR, timeout=600
            )
        except subprocess.TimeoutExpired:
            logger.warning("Timeout download immagine Docker")

    def _check_webui(self):
        try:
            result = subprocess.run(
                ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", URL_WEBUI],
                capture_output=True, timeout=5, text=True
            )
            return result.stdout.strip() in ["200", "302"]
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False


class WorkerThread(QThread):
    """Thread per eseguire comandi shell in background."""
    output_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(int)

    def __init__(self, command, cwd=None):
        super().__init__()
        self.command = command
        self.cwd = cwd or SCRIPT_DIR
        self._process = None
        self._cancelled = False

    def run(self):
        try:
            self._process = subprocess.Popen(
                self.command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                cwd=self.cwd,
                text=True,
                bufsize=1
            )
            for line in iter(self._process.stdout.readline, ''):
                if self._cancelled:
                    break
                if line:
                    self.output_signal.emit(line.strip())
            self._process.wait()
            if self._cancelled:
                self.finished_signal.emit(-1)
            else:
                self.finished_signal.emit(self._process.returncode)
        except Exception as e:
            logger.error("Errore esecuzione comando: %s", e)
            self.output_signal.emit(f"Errore: {str(e)}")
            self.finished_signal.emit(1)

    def cancel(self):
        self._cancelled = True
        if self._process and self._process.poll() is None:
            self._process.terminate()


class StatusChecker(QThread):
    """Thread per controllare periodicamente lo stato dei servizi."""
    status_signal = pyqtSignal(dict)

    def run(self):
        while True:
            status = {
                'ollama': self._check_service(f"{URL_OLLAMA}/api/version"),
                'openwebui': self._check_webui(),
                'tts': self._check_service(f"{URL_TTS}/v1/models"),
            }
            self.status_signal.emit(status)
            time.sleep(5)

    def _check_service(self, url):
        try:
            result = subprocess.run(
                ['curl', '-s', url],
                capture_output=True, timeout=2
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def _check_webui(self):
        try:
            result = subprocess.run(
                ['curl', '-s', '-o', '/dev/null', '-w', '%{http_code}', URL_WEBUI],
                capture_output=True, timeout=2, text=True
            )
            return result.stdout.strip() in ['200', '302']
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False
