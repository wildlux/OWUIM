#!/usr/bin/env python3
"""
Open WebUI Manager - Interfaccia Grafica
Autore: Paolo Lo Bello
Versione: 1.1.0
Framework: PyQt5

Doppio click per avviare automaticamente:
- Docker Desktop (Windows)
- Ollama
- Open WebUI Container
"""

import sys
import os
import subprocess
import threading
import time
import platform
import shutil
import webbrowser
from pathlib import Path

# Rileva sistema operativo
IS_WINDOWS = platform.system() == "Windows"
IS_LINUX = platform.system() == "Linux"
IS_MAC = platform.system() == "Darwin"

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTextEdit, QTabWidget, QGroupBox, QGridLayout,
    QComboBox, QLineEdit, QMessageBox, QProgressBar, QFrame, QSplitter,
    QListWidget, QListWidgetItem, QSystemTrayIcon, QMenu, QAction,
    QStatusBar, QToolBar, QSizePolicy, QScrollArea, QDialog, QSplashScreen,
    QTreeView, QFileDialog, QHeaderView, QAbstractItemView, QCheckBox
)
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal, QSize, QByteArray, QBuffer, QUrl, QDir, QFileInfo, QSettings, QModelIndex
from PyQt5.QtGui import QIcon, QFont, QPalette, QColor, QPixmap, QImage, QDesktopServices
from PyQt5.QtWidgets import QFileSystemModel

# Audio playback
try:
    from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
    HAS_MULTIMEDIA = True
except ImportError:
    HAS_MULTIMEDIA = False

# QR Code generation
try:
    import qrcode
    from io import BytesIO
    HAS_QRCODE = True
except ImportError:
    HAS_QRCODE = False

# Directory dello script
SCRIPT_DIR = Path(__file__).parent.resolve()
SCRIPTS_DIR = SCRIPT_DIR / "scripts"

# Comando docker compose (compatibile con vecchie e nuove versioni)
def get_docker_compose_cmd():
    """Ritorna il comando docker compose corretto per il sistema."""
    import shutil
    # Prova prima 'docker compose' (nuovo), poi 'docker-compose' (vecchio)
    if shutil.which("docker") and subprocess.run(
        ["docker", "compose", "version"],
        capture_output=True
    ).returncode == 0:
        return "docker compose"
    elif shutil.which("docker-compose"):
        return "docker-compose"
    else:
        return "docker compose"  # Default

DOCKER_COMPOSE = get_docker_compose_cmd()


class StartupThread(QThread):
    """Thread per avvio automatico di Docker, Ollama e Open WebUI"""
    progress_signal = pyqtSignal(str, int)  # messaggio, percentuale
    finished_signal = pyqtSignal(bool, str)  # successo, messaggio

    def run(self):
        try:
            # [1/5] Verifica Docker
            self.progress_signal.emit("Verifica Docker...", 10)
            if not self.check_docker():
                if IS_WINDOWS:
                    self.progress_signal.emit("Avvio Docker Desktop...", 15)
                    if not self.start_docker_windows():
                        self.finished_signal.emit(False, "Docker Desktop non disponibile.\nAvvialo manualmente e riprova.")
                        return
                else:
                    self.finished_signal.emit(False, "Docker non disponibile.\nInstalla Docker e riprova.")
                    return
            self.progress_signal.emit("Docker OK", 25)

            # [2/5] Verifica Ollama
            self.progress_signal.emit("Verifica Ollama...", 30)
            if not self.check_ollama():
                self.progress_signal.emit("Avvio Ollama...", 35)
                if not self.start_ollama():
                    self.finished_signal.emit(False, "Ollama non disponibile.\nInstalla Ollama e riprova.")
                    return
            self.progress_signal.emit("Ollama OK", 50)

            # [3/5] Avvia container
            self.progress_signal.emit("Avvio Open WebUI...", 55)
            if not self.start_containers():
                self.progress_signal.emit("Download immagine...", 60)
                self.pull_image()
                if not self.start_containers():
                    self.finished_signal.emit(False, "Impossibile avviare i container.")
                    return
            self.progress_signal.emit("Container avviato", 75)

            # [4/5] Attesa servizio pronto
            self.progress_signal.emit("Attesa servizio...", 80)
            for i in range(30):
                if self.check_webui():
                    break
                time.sleep(2)
                self.progress_signal.emit(f"Attesa servizio... ({i+1}/30)", 80 + i//2)

            # [5/5] Completato
            self.progress_signal.emit("Pronto!", 100)
            time.sleep(0.5)
            self.finished_signal.emit(True, "Tutti i servizi avviati!")

        except Exception as e:
            self.finished_signal.emit(False, f"Errore: {str(e)}")

    def check_docker(self):
        """Verifica se Docker risponde"""
        try:
            result = subprocess.run(
                ["docker", "info"],
                capture_output=True,
                timeout=10
            )
            return result.returncode == 0
        except:
            return False

    def start_docker_windows(self):
        """Tenta di avviare Docker Desktop su Windows"""
        try:
            # Percorsi comuni Docker Desktop
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
                # Prova con start
                subprocess.Popen(
                    ["cmd", "/c", "start", "", "Docker Desktop"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )

            # Attendi che Docker sia pronto
            for i in range(40):  # Max 2 minuti
                time.sleep(3)
                self.progress_signal.emit(f"Attesa Docker Desktop... ({i+1}/40)", 15 + i//4)
                if self.check_docker():
                    return True
            return False
        except:
            return False

    def check_ollama(self):
        """Verifica se Ollama risponde"""
        try:
            result = subprocess.run(
                ["curl", "-s", "http://localhost:11434/api/version"],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except:
            return False

    def start_ollama(self):
        """Avvia Ollama"""
        try:
            # Verifica se ollama esiste
            if IS_WINDOWS:
                ollama_cmd = shutil.which("ollama") or "ollama"
                subprocess.Popen(
                    ["cmd", "/c", "start", "/min", "", ollama_cmd, "serve"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            else:
                subprocess.Popen(
                    ["ollama", "serve"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )

            # Attendi che Ollama sia pronto
            for i in range(20):
                time.sleep(2)
                self.progress_signal.emit(f"Attesa Ollama... ({i+1}/20)", 35 + i//2)
                if self.check_ollama():
                    return True
            return False
        except:
            return False

    def start_containers(self):
        """Avvia i container Docker"""
        try:
            result = subprocess.run(
                f"{DOCKER_COMPOSE} up -d",
                shell=True,
                capture_output=True,
                cwd=SCRIPT_DIR,
                timeout=120
            )
            return result.returncode == 0
        except:
            return False

    def pull_image(self):
        """Scarica l'immagine Docker"""
        try:
            subprocess.run(
                f"{DOCKER_COMPOSE} pull",
                shell=True,
                capture_output=True,
                cwd=SCRIPT_DIR,
                timeout=600
            )
        except:
            pass

    def check_webui(self):
        """Verifica se Open WebUI risponde"""
        try:
            result = subprocess.run(
                ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", "http://localhost:3000"],
                capture_output=True,
                timeout=5,
                text=True
            )
            return result.stdout.strip() in ["200", "302"]
        except:
            return False


class StartupDialog(QDialog):
    """Dialog di avvio con progress bar"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Open WebUI Manager")
        self.setFixedSize(400, 200)
        self.setWindowFlags(Qt.Dialog | Qt.CustomizeWindowHint | Qt.WindowTitleHint)

        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        # Titolo
        title = QLabel("Avvio Open WebUI + Ollama")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Status
        self.status_label = QLabel("Inizializzazione...")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setFont(QFont("Arial", 10))
        layout.addWidget(self.status_label)

        # Progress bar
        self.progress = QProgressBar()
        self.progress.setMinimum(0)
        self.progress.setMaximum(100)
        self.progress.setValue(0)
        self.progress.setTextVisible(True)
        self.progress.setStyleSheet("""
            QProgressBar {
                border: 1px solid #ddd;
                border-radius: 5px;
                text-align: center;
                height: 25px;
            }
            QProgressBar::chunk {
                background-color: #3498db;
                border-radius: 4px;
            }
        """)
        layout.addWidget(self.progress)

        # Pulsante skip (nascosto inizialmente)
        self.skip_btn = QPushButton("Salta e apri GUI")
        self.skip_btn.setVisible(False)
        self.skip_btn.clicked.connect(self.accept)
        layout.addWidget(self.skip_btn)

        layout.addStretch()

        # Thread di avvio
        self.startup_thread = StartupThread()
        self.startup_thread.progress_signal.connect(self.update_progress)
        self.startup_thread.finished_signal.connect(self.startup_finished)

        # Mostra pulsante skip dopo 10 secondi
        QTimer.singleShot(10000, lambda: self.skip_btn.setVisible(True))

    def start(self):
        """Avvia il processo di startup"""
        self.startup_thread.start()

    def update_progress(self, message, percent):
        """Aggiorna la progress bar"""
        self.status_label.setText(message)
        self.progress.setValue(percent)

    def startup_finished(self, success, message):
        """Chiamato quando lo startup e' completato"""
        if success:
            self.accept()
        else:
            self.skip_btn.setVisible(True)
            self.skip_btn.setText("Continua comunque")
            self.status_label.setText(f"Attenzione: {message}")
            self.status_label.setStyleSheet("color: #e74c3c;")


class WorkerThread(QThread):
    """Thread per eseguire comandi in background"""
    output_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(int)

    def __init__(self, command, cwd=None):
        super().__init__()
        self.command = command
        self.cwd = cwd or SCRIPT_DIR

    def run(self):
        try:
            process = subprocess.Popen(
                self.command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                cwd=self.cwd,
                text=True,
                bufsize=1
            )
            for line in iter(process.stdout.readline, ''):
                if line:
                    self.output_signal.emit(line.strip())
            process.wait()
            self.finished_signal.emit(process.returncode)
        except Exception as e:
            self.output_signal.emit(f"Errore: {str(e)}")
            self.finished_signal.emit(1)


class StatusChecker(QThread):
    """Thread per controllare lo stato dei servizi"""
    status_signal = pyqtSignal(dict)

    def run(self):
        while True:
            status = {
                'ollama': self.check_ollama(),
                'openwebui': self.check_openwebui(),
                'tts': self.check_tts()
            }
            self.status_signal.emit(status)
            time.sleep(5)

    def check_ollama(self):
        try:
            result = subprocess.run(
                ['curl', '-s', 'http://localhost:11434/api/version'],
                capture_output=True, timeout=2
            )
            return result.returncode == 0
        except:
            return False

    def check_openwebui(self):
        try:
            result = subprocess.run(
                ['curl', '-s', '-o', '/dev/null', '-w', '%{http_code}', 'http://localhost:3000'],
                capture_output=True, timeout=2, text=True
            )
            code = result.stdout.strip()
            return code in ['200', '302']
        except:
            return False

    def check_tts(self):
        try:
            result = subprocess.run(
                ['curl', '-s', 'http://localhost:8000/v1/models'],
                capture_output=True, timeout=2
            )
            return result.returncode == 0
        except:
            return False


class ModernButton(QPushButton):
    """Pulsante con stile moderno"""
    def __init__(self, text, color="blue", parent=None):
        super().__init__(text, parent)
        self.setMinimumHeight(40)
        self.setCursor(Qt.PointingHandCursor)

        colors = {
            "blue": ("#3498db", "#2980b9"),
            "green": ("#27ae60", "#1e8449"),
            "red": ("#e74c3c", "#c0392b"),
            "orange": ("#f39c12", "#d68910"),
            "purple": ("#9b59b6", "#8e44ad"),
            "gray": ("#6c7a89", "#566573"),
        }

        bg, hover = colors.get(color, colors["blue"])
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {hover};
            }}
            QPushButton:pressed {{
                background-color: {hover};
                padding-top: 12px;
            }}
            QPushButton:disabled {{
                background-color: #bdc3c7;
            }}
        """)


class StatusIndicator(QFrame):
    """Indicatore di stato con pallino colorato"""
    def __init__(self, name, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)

        self.indicator = QLabel("●")
        self.indicator.setFont(QFont("Arial", 16))
        self.label = QLabel(name)
        self.label.setFont(QFont("Arial", 12))
        self.status_label = QLabel("Verifica...")
        self.status_label.setFont(QFont("Arial", 10))
        self.status_label.setStyleSheet("color: #7f8c8d;")

        layout.addWidget(self.indicator)
        layout.addWidget(self.label)
        layout.addStretch()
        layout.addWidget(self.status_label)

        self.set_status(None)

    def set_status(self, active):
        if active is None:
            self.indicator.setStyleSheet("color: #f39c12;")
            self.status_label.setText("Verifica...")
        elif active:
            self.indicator.setStyleSheet("color: #27ae60;")
            self.status_label.setText("Attivo")
        else:
            self.indicator.setStyleSheet("color: #e74c3c;")
            self.status_label.setText("Non attivo")


class DashboardWidget(QWidget):
    """Widget Dashboard principale"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)

        # Titolo
        title = QLabel("Dashboard")
        title.setFont(QFont("Arial", 24, QFont.Bold))
        title.setStyleSheet("color: #2c3e50;")
        layout.addWidget(title)

        # Stato servizi
        status_group = QGroupBox("Stato Servizi")
        status_group.setFont(QFont("Arial", 12, QFont.Bold))
        status_layout = QVBoxLayout(status_group)

        self.ollama_status = StatusIndicator("Ollama")
        self.openwebui_status = StatusIndicator("Open WebUI")
        self.tts_status = StatusIndicator("TTS (Speech)")

        status_layout.addWidget(self.ollama_status)
        status_layout.addWidget(self.openwebui_status)
        status_layout.addWidget(self.tts_status)
        layout.addWidget(status_group)

        # Azioni rapide
        actions_group = QGroupBox("Azioni Rapide")
        actions_group.setFont(QFont("Arial", 12, QFont.Bold))
        actions_layout = QGridLayout(actions_group)
        actions_layout.setSpacing(10)

        self.btn_start = ModernButton("▶  Avvia", "green")
        self.btn_stop = ModernButton("⏹  Ferma", "red")
        self.btn_restart = ModernButton("🔄  Riavvia", "orange")
        self.btn_open_browser = ModernButton("🌐  Apri Browser", "blue")

        self.btn_start.clicked.connect(self.start_services)
        self.btn_stop.clicked.connect(self.stop_services)
        self.btn_restart.clicked.connect(self.restart_services)
        self.btn_open_browser.clicked.connect(self.open_browser)

        actions_layout.addWidget(self.btn_start, 0, 0)
        actions_layout.addWidget(self.btn_stop, 0, 1)
        actions_layout.addWidget(self.btn_restart, 1, 0)
        actions_layout.addWidget(self.btn_open_browser, 1, 1)
        layout.addWidget(actions_group)

        # Info
        info_group = QGroupBox("Informazioni")
        info_group.setFont(QFont("Arial", 12, QFont.Bold))
        info_layout = QVBoxLayout(info_group)

        info_text = QLabel(
            "🌐 Open WebUI: <a href='http://localhost:3000'>http://localhost:3000</a><br>"
            "🤖 Ollama API: <a href='http://localhost:11434'>http://localhost:11434</a><br>"
            "🔊 TTS API: <a href='http://localhost:8000'>http://localhost:8000</a><br>"
            f"📁 Directory: {SCRIPT_DIR}"
        )
        info_text.setOpenExternalLinks(True)
        info_text.setFont(QFont("Arial", 11))
        info_text.setWordWrap(True)
        info_layout.addWidget(info_text)
        layout.addWidget(info_group)

        layout.addStretch()

    def update_status(self, status):
        self.ollama_status.set_status(status.get('ollama'))
        self.openwebui_status.set_status(status.get('openwebui'))
        self.tts_status.set_status(status.get('tts'))

    def start_services(self):
        self.main_window.run_command(f"{DOCKER_COMPOSE} up -d", "Avvio servizi...")

    def stop_services(self):
        self.main_window.run_command(f"{DOCKER_COMPOSE} down", "Arresto servizi...")

    def restart_services(self):
        self.main_window.run_command(f"{DOCKER_COMPOSE} down && {DOCKER_COMPOSE} up -d", "Riavvio servizi...")

    def open_browser(self):
        url = 'http://localhost:3000'
        if IS_WINDOWS:
            os.startfile(url)
        elif IS_MAC:
            subprocess.Popen(['open', url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            subprocess.Popen(['xdg-open', url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


class LogsWidget(QWidget):
    """Widget per visualizzare i log"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        title = QLabel("Log dei Servizi")
        title.setFont(QFont("Arial", 24, QFont.Bold))
        title.setStyleSheet("color: #2c3e50;")
        layout.addWidget(title)

        # Area log
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setFont(QFont("Monospace", 10))
        self.log_area.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: 1px solid #3c3c3c;
                border-radius: 6px;
                padding: 10px;
            }
        """)
        layout.addWidget(self.log_area)

        # Pulsanti
        btn_layout = QHBoxLayout()

        btn_refresh = ModernButton("🔄 Aggiorna Log", "blue")
        btn_clear = ModernButton("🗑️ Pulisci", "gray")
        btn_follow = ModernButton("📜 Segui Log", "green")

        btn_refresh.clicked.connect(self.refresh_logs)
        btn_clear.clicked.connect(self.clear_logs)
        btn_follow.clicked.connect(self.follow_logs)

        btn_layout.addWidget(btn_refresh)
        btn_layout.addWidget(btn_clear)
        btn_layout.addWidget(btn_follow)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

    def append_log(self, text):
        self.log_area.append(text)
        self.log_area.verticalScrollBar().setValue(
            self.log_area.verticalScrollBar().maximum()
        )

    def clear_logs(self):
        self.log_area.clear()

    def refresh_logs(self):
        self.clear_logs()
        try:
            result = subprocess.run(
                f"{DOCKER_COMPOSE} logs --tail=100",
                shell=True, capture_output=True, text=True, cwd=SCRIPT_DIR
            )
            self.log_area.setText(result.stdout or result.stderr or "Nessun log disponibile")
        except Exception as e:
            self.log_area.setText(f"Errore: {str(e)}")

    def follow_logs(self):
        self.main_window.run_command(
            f"{DOCKER_COMPOSE} logs -f --tail=50",
            "Caricamento log in tempo reale..."
        )


class ModelsWidget(QWidget):
    """Widget per gestire i modelli"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        title = QLabel("Gestione Modelli")
        title.setFont(QFont("Arial", 24, QFont.Bold))
        title.setStyleSheet("color: #2c3e50;")
        layout.addWidget(title)

        # Lista modelli
        models_group = QGroupBox("Modelli Installati")
        models_group.setFont(QFont("Arial", 12, QFont.Bold))
        models_layout = QVBoxLayout(models_group)

        self.models_list = QListWidget()
        self.models_list.setFont(QFont("Monospace", 11))
        self.models_list.setMinimumHeight(200)
        models_layout.addWidget(self.models_list)

        btn_refresh = ModernButton("🔄 Aggiorna Lista", "blue")
        btn_refresh.clicked.connect(self.refresh_models)
        models_layout.addWidget(btn_refresh)

        layout.addWidget(models_group)

        # Download modello
        download_group = QGroupBox("Scarica Nuovo Modello")
        download_group.setFont(QFont("Arial", 12, QFont.Bold))
        download_layout = QVBoxLayout(download_group)

        info_label = QLabel("Modelli consigliati per italiano:")
        info_label.setFont(QFont("Arial", 10))
        download_layout.addWidget(info_label)

        self.model_combo = QComboBox()
        self.model_combo.setFont(QFont("Arial", 11))
        self.model_combo.addItems([
            "mistral:7b-instruct",
            "qwen2.5:7b-instruct",
            "llama3:8b",
            "gemma2:9b",
            "codellama:7b",
            "phi3:medium",
        ])
        self.model_combo.setEditable(True)
        download_layout.addWidget(self.model_combo)

        btn_download = ModernButton("⬇️ Scarica Modello", "green")
        btn_download.clicked.connect(self.download_model)
        download_layout.addWidget(btn_download)

        layout.addWidget(download_group)

        # Rimuovi modello
        remove_group = QGroupBox("Rimuovi Modello")
        remove_group.setFont(QFont("Arial", 12, QFont.Bold))
        remove_layout = QHBoxLayout(remove_group)

        self.remove_input = QLineEdit()
        self.remove_input.setPlaceholderText("Nome modello da rimuovere...")
        self.remove_input.setFont(QFont("Arial", 11))
        remove_layout.addWidget(self.remove_input)

        btn_remove = ModernButton("🗑️ Rimuovi", "red")
        btn_remove.clicked.connect(self.remove_model)
        remove_layout.addWidget(btn_remove)

        layout.addWidget(remove_group)
        layout.addStretch()

        # Carica modelli all'avvio
        self.refresh_models()

    def refresh_models(self):
        self.models_list.clear()
        try:
            result = subprocess.run(
                "ollama list 2>/dev/null || docker exec ollama ollama list 2>/dev/null",
                shell=True, capture_output=True, text=True
            )
            if result.stdout:
                for line in result.stdout.strip().split('\n'):
                    if line and not line.startswith('NAME'):
                        item = QListWidgetItem(line)
                        self.models_list.addItem(item)
        except Exception as e:
            self.models_list.addItem(f"Errore: {str(e)}")

    def download_model(self):
        model = self.model_combo.currentText().strip()
        if model:
            self.main_window.run_command(
                f"ollama pull {model} 2>/dev/null || docker exec -it ollama ollama pull {model}",
                f"Download {model}..."
            )

    def remove_model(self):
        model = self.remove_input.text().strip()
        if model:
            reply = QMessageBox.question(
                self, "Conferma",
                f"Vuoi davvero rimuovere il modello '{model}'?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self.main_window.run_command(
                    f"ollama rm {model} 2>/dev/null || docker exec ollama ollama rm {model}",
                    f"Rimozione {model}..."
                )


class ConfigWidget(QWidget):
    """Widget per le configurazioni"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(10, 10, 10, 10)

        title = QLabel("Configurazione")
        title.setFont(QFont("Arial", 20, QFont.Bold))
        title.setStyleSheet("color: #2c3e50;")
        layout.addWidget(title)

        # LAN Access
        lan_group = QGroupBox("Accesso LAN (Cellulare/Tablet)")
        lan_layout = QVBoxLayout(lan_group)
        lan_layout.setSpacing(6)
        lan_layout.setContentsMargins(8, 12, 8, 8)

        # Indirizzo con pulsante copia
        addr_row = QHBoxLayout()
        addr_row.setSpacing(5)
        addr_label = QLabel("📱 Indirizzo:")
        addr_label.setStyleSheet("font-size: 11px; font-weight: bold;")
        addr_row.addWidget(addr_label)

        self.lan_url_field = QLineEdit()
        self.lan_url_field.setReadOnly(True)
        self.lan_url_field.setStyleSheet("font-family: Monospace; font-size: 11px; padding: 4px; background: #e8f5e9;")
        addr_row.addWidget(self.lan_url_field, 1)

        copy_url_btn = QPushButton("📋")
        copy_url_btn.setMaximumWidth(30)
        copy_url_btn.setToolTip("Copia indirizzo negli appunti")
        copy_url_btn.clicked.connect(lambda: QApplication.clipboard().setText(self.lan_url_field.text()))
        addr_row.addWidget(copy_url_btn)

        lan_layout.addLayout(addr_row)

        # Istruzioni compatte
        instructions = QLabel(
            "<b>Come collegarsi:</b> "
            "1) Connetti il cellulare alla stessa WiFi · "
            "2) Apri il browser e vai all'indirizzo · "
            "3) Effettua il login"
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("font-size: 10px; color: #555; padding: 4px;")
        lan_layout.addWidget(instructions)

        # Pulsanti LAN
        lan_btn_layout = QHBoxLayout()
        lan_btn_layout.setSpacing(5)

        btn_lan_enable = ModernButton("🌐 Abilita LAN", "green")
        btn_lan_enable.setToolTip("Permette l'accesso da altri dispositivi sulla rete")
        btn_lan_enable.clicked.connect(self.enable_lan)
        lan_btn_layout.addWidget(btn_lan_enable)

        btn_lan_disable = ModernButton("🔒 Solo Localhost", "red")
        btn_lan_disable.setToolTip("Limita l'accesso solo a questo computer")
        btn_lan_disable.clicked.connect(self.disable_lan)
        lan_btn_layout.addWidget(btn_lan_disable)

        btn_lan_refresh = ModernButton("🔄", "blue")
        btn_lan_refresh.setMaximumWidth(40)
        btn_lan_refresh.setToolTip("Aggiorna indirizzo IP")
        btn_lan_refresh.clicked.connect(self.update_lan_info)
        lan_btn_layout.addWidget(btn_lan_refresh)

        lan_layout.addLayout(lan_btn_layout)
        layout.addWidget(lan_group)

        # HTTPS
        https_group = QGroupBox("HTTPS (per Microfono)")
        https_layout = QVBoxLayout(https_group)
        https_layout.setContentsMargins(8, 12, 8, 8)

        https_info = QLabel("Necessario per usare il microfono da dispositivi mobili.")
        https_info.setStyleSheet("font-size: 10px; color: #555;")
        https_layout.addWidget(https_info)

        btn_https = ModernButton("🔐 Configura HTTPS", "purple")
        btn_https.setToolTip("Genera certificato SSL per connessioni sicure")
        btn_https.clicked.connect(self.configure_https)
        https_layout.addWidget(btn_https)

        layout.addWidget(https_group)

        # Italiano
        italian_group = QGroupBox("Lingua Italiana")
        italian_layout = QVBoxLayout(italian_group)
        italian_layout.setContentsMargins(8, 12, 8, 8)

        btn_italian = ModernButton("🇮🇹 Guida Configurazione Italiano", "blue")
        btn_italian.setToolTip("Mostra come impostare Open WebUI in italiano")
        btn_italian.clicked.connect(self.show_italian_guide)
        italian_layout.addWidget(btn_italian)

        layout.addWidget(italian_group)

        # Manutenzione
        maint_group = QGroupBox("Manutenzione")
        maint_layout = QHBoxLayout(maint_group)
        maint_layout.setContentsMargins(8, 12, 8, 8)
        maint_layout.setSpacing(8)

        btn_update = ModernButton("⬆️ Aggiorna", "blue")
        btn_update.setToolTip("Scarica l'ultima versione di Open WebUI")
        btn_update.clicked.connect(self.update_openwebui)
        maint_layout.addWidget(btn_update)

        btn_fix = ModernButton("🔧 Ripara", "orange")
        btn_fix.setToolTip("Riavvia i container e pulisce la cache")
        btn_fix.clicked.connect(self.fix_openwebui)
        maint_layout.addWidget(btn_fix)

        btn_backup = ModernButton("💾 Backup", "green")
        btn_backup.setToolTip("Crea backup dei dati su USB")
        btn_backup.clicked.connect(self.backup_usb)
        maint_layout.addWidget(btn_backup)

        layout.addWidget(maint_group)
        layout.addStretch()

    def get_local_ip(self):
        """Ottiene l'IP locale della macchina."""
        import socket
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "192.168.1.X"

    def update_lan_info(self):
        """Aggiorna le informazioni LAN visualizzate."""
        ip = self.get_local_ip()
        self.lan_status_label.setText(
            f"📱 Per collegarti dal cellulare:\n\n"
            f"   Indirizzo:  http://{ip}:3000\n\n"
            f"   1. Connetti il cellulare alla stessa WiFi\n"
            f"   2. Apri il browser e vai all'indirizzo sopra\n"
            f"   3. Effettua il login con le tue credenziali"
        )

    def show_lan_qr_dialog(self, ip):
        """Mostra dialog con QR code per connessione LAN."""
        url = f"http://{ip}:3000"

        dialog = QDialog(self)
        dialog.setWindowTitle("✅ Accesso LAN Abilitato")
        dialog.setMinimumWidth(400)

        layout = QVBoxLayout(dialog)

        # Titolo
        title = QLabel("📱 Scansiona il QR Code dal cellulare")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # QR Code
        if HAS_QRCODE:
            qr = qrcode.QRCode(version=1, box_size=8, border=2)
            qr.add_data(url)
            qr.make(fit=True)
            qr_img = qr.make_image(fill_color="black", back_color="white")

            # Converti PIL image a QPixmap
            buffer = BytesIO()
            qr_img.save(buffer, format='PNG')
            buffer.seek(0)

            qr_pixmap = QPixmap()
            qr_pixmap.loadFromData(buffer.getvalue())

            qr_label = QLabel()
            qr_label.setPixmap(qr_pixmap)
            qr_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(qr_label)
        else:
            no_qr = QLabel("(Installa 'qrcode' per vedere il QR:\npip install qrcode[pil])")
            no_qr.setAlignment(Qt.AlignCenter)
            no_qr.setStyleSheet("color: #888;")
            layout.addWidget(no_qr)

        # URL
        url_frame = QFrame()
        url_frame.setStyleSheet("""
            QFrame {
                background-color: #e3f2fd;
                border: 2px solid #2196f3;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        url_layout = QVBoxLayout(url_frame)

        url_label = QLabel(f"<b style='font-size: 16px;'>{url}</b>")
        url_label.setAlignment(Qt.AlignCenter)
        url_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        url_layout.addWidget(url_label)

        layout.addWidget(url_frame)

        # Istruzioni PWA
        pwa_info = QLabel(
            "<b>📲 Installa come App (PWA):</b><br><br>"
            "1. Apri Chrome sul cellulare<br>"
            "2. Scansiona il QR code o vai all'indirizzo<br>"
            "3. Menu ⋮ → 'Aggiungi a schermata Home'<br>"
            "4. Avrai un'icona come app!<br><br>"
            "<i>⚠️ Cellulare e PC devono essere sulla stessa WiFi</i>"
        )
        pwa_info.setWordWrap(True)
        pwa_info.setStyleSheet("padding: 10px;")
        layout.addWidget(pwa_info)

        # Pulsante chiudi
        btn_close = QPushButton("OK")
        btn_close.setStyleSheet("""
            QPushButton {
                background-color: #4caf50;
                color: white;
                border: none;
                padding: 10px 30px;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        btn_close.clicked.connect(dialog.accept)
        layout.addWidget(btn_close, alignment=Qt.AlignCenter)

        dialog.exec_()

    def enable_lan(self):
        ip = self.get_local_ip()
        self.main_window.run_command(
            f"sed -i 's/127\\.0\\.0\\.1:3000/0.0.0.0:3000/g' docker-compose.yml && "
            f"sed -i 's/127\\.0\\.0\\.1:11434/0.0.0.0:11434/g' docker-compose.yml && "
            f"{DOCKER_COMPOSE} down && {DOCKER_COMPOSE} up -d",
            "Abilitazione accesso LAN..."
        )
        # Mostra dialog con QR code
        self.show_lan_qr_dialog(ip)
        self.update_lan_info()

    def disable_lan(self):
        self.main_window.run_command(
            f"sed -i 's/0\\.0\\.0\\.0:3000/127.0.0.1:3000/g' docker-compose.yml && "
            f"sed -i 's/0\\.0\\.0\\.0:11434/127.0.0.1:11434/g' docker-compose.yml && "
            f"{DOCKER_COMPOSE} down && {DOCKER_COMPOSE} up -d",
            "Disabilitazione accesso LAN..."
        )
        QMessageBox.information(
            self,
            "Accesso LAN Disabilitato",
            "🔒 Accesso limitato a localhost.\n\n"
            "Solo questo PC può accedere a Open WebUI."
        )

    def configure_https(self):
        script = SCRIPTS_DIR / "enable_https.sh"
        if script.exists():
            self.main_window.run_command(f"bash {script}", "Configurazione HTTPS...")
        else:
            QMessageBox.warning(self, "Errore", "Script HTTPS non trovato")

    def show_italian_guide(self):
        guide = """
<h2>Configurazione Italiano in Open WebUI</h2>

<h3>1. Lingua Interfaccia</h3>
<p>Settings → Interface → Language → <b>Italiano</b></p>

<h3>2. System Prompt</h3>
<p>Settings → Personalization → System Prompt</p>
<pre style="background: #f5f5f5; padding: 10px;">
Sei un assistente AI che risponde SEMPRE in italiano.
Non importa la lingua della domanda, rispondi sempre in italiano.
Usa un linguaggio chiaro, professionale e amichevole.
</pre>

<h3>3. Modello Predefinito</h3>
<p>Settings → Models → Default Model → <b>mistral:7b-instruct</b> (consigliato)</p>
"""
        msg = QMessageBox(self)
        msg.setWindowTitle("Guida Configurazione Italiano")
        msg.setTextFormat(Qt.RichText)
        msg.setText(guide)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    def update_openwebui(self):
        self.main_window.run_command(f"{DOCKER_COMPOSE} pull && {DOCKER_COMPOSE} up -d", "Aggiornamento Open WebUI...")

    def fix_openwebui(self):
        self.main_window.run_command(f"{DOCKER_COMPOSE} down && docker system prune -f && {DOCKER_COMPOSE} up -d", "Riparazione Open WebUI...")

    def backup_usb(self):
        script = SCRIPTS_DIR / "backup_to_usb.sh"
        if IS_WINDOWS:
            QMessageBox.information(
                self, "Backup",
                "Su Windows, usa il File Explorer per copiare manualmente:\n\n"
                f"• Cartella: {SCRIPT_DIR}\n"
                "• Volumi Docker (open-webui-data)"
            )
        elif script.exists():
            # Apri terminale per backup interattivo
            if IS_MAC:
                subprocess.Popen(['open', '-a', 'Terminal', str(script)], cwd=SCRIPT_DIR)
            else:
                # Linux - prova vari terminali
                for terminal in ['gnome-terminal', 'konsole', 'xfce4-terminal', 'xterm']:
                    try:
                        if terminal == 'gnome-terminal':
                            subprocess.Popen([terminal, '--', 'bash', str(script)], cwd=SCRIPT_DIR)
                        else:
                            subprocess.Popen([terminal, '-e', f'bash {script}'], cwd=SCRIPT_DIR)
                        break
                    except FileNotFoundError:
                        continue
        else:
            QMessageBox.warning(self, "Errore", "Script backup non trovato")


class TTSWidget(QWidget):
    """Widget per configurare e testare la sintesi vocale italiana LOCALE."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        self.tts_service_url = "http://localhost:5556"
        self.audio_file = None  # Path del file audio temporaneo

        # Media player per riproduzione audio
        if HAS_MULTIMEDIA:
            self.player = QMediaPlayer()
            self.player.stateChanged.connect(self._on_player_state_changed)
            self.player.error.connect(self._on_player_error)
        else:
            self.player = None

        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # ScrollArea per contenuto
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        # Titolo
        title = QLabel("Sintesi Vocale Italiana (Locale)")
        title.setFont(QFont("Arial", 20, QFont.Bold))
        title.setStyleSheet("color: #2c3e50;")
        layout.addWidget(title)

        # Info
        info = QLabel("Voci italiane OFFLINE con Piper TTS. Non richiede internet dopo l'installazione.")
        info.setWordWrap(True)
        info.setStyleSheet("color: #27ae60; font-size: 11px; font-weight: bold;")
        layout.addWidget(info)

        # === STATO SERVIZIO ===
        status_group = QGroupBox("Stato Servizio")
        status_layout = QHBoxLayout(status_group)
        status_layout.setContentsMargins(10, 10, 10, 10)

        self.status_indicator = QLabel("●")
        self.status_indicator.setFont(QFont("Arial", 14))
        self.status_indicator.setStyleSheet("color: #f39c12;")
        status_layout.addWidget(self.status_indicator)

        self.status_label = QLabel("Verifica in corso...")
        self.status_label.setFont(QFont("Arial", 10))
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()

        self.start_service_btn = ModernButton("Avvia Servizio", "green")
        self.start_service_btn.clicked.connect(self.start_tts_service)
        status_layout.addWidget(self.start_service_btn)

        self.refresh_btn = ModernButton("Aggiorna", "gray")
        self.refresh_btn.clicked.connect(self.check_service_status)
        status_layout.addWidget(self.refresh_btn)

        layout.addWidget(status_group)

        # === VOCI DISPONIBILI ===
        voices_group = QGroupBox("Voci Italiane Disponibili")
        voices_layout = QVBoxLayout(voices_group)
        voices_layout.setSpacing(8)

        # Voce Paola
        paola_row = QHBoxLayout()
        paola_row.setSpacing(10)

        self.paola_status = QLabel("●")
        self.paola_status.setFixedWidth(20)
        self.paola_status.setFont(QFont("Arial", 14))
        self.paola_status.setStyleSheet("color: #bdc3c7;")
        paola_row.addWidget(self.paola_status)

        paola_icon = QLabel("👩")
        paola_icon.setFixedWidth(30)
        paola_icon.setFont(QFont("Arial", 18))
        paola_row.addWidget(paola_icon)

        paola_info = QLabel("<b>Paola</b> - Voce femminile, qualità media (~30 MB)")
        paola_info.setStyleSheet("color: #c2185b;")
        paola_row.addWidget(paola_info, 1)

        self.install_paola_btn = ModernButton("Scarica", "purple")
        self.install_paola_btn.setFixedWidth(90)
        self.install_paola_btn.clicked.connect(lambda: self.install_voice("paola"))
        paola_row.addWidget(self.install_paola_btn)

        voices_layout.addLayout(paola_row)

        # Voce Riccardo
        riccardo_row = QHBoxLayout()
        riccardo_row.setSpacing(10)

        self.riccardo_status = QLabel("●")
        self.riccardo_status.setFixedWidth(20)
        self.riccardo_status.setFont(QFont("Arial", 14))
        self.riccardo_status.setStyleSheet("color: #bdc3c7;")
        riccardo_row.addWidget(self.riccardo_status)

        riccardo_icon = QLabel("👨")
        riccardo_icon.setFixedWidth(30)
        riccardo_icon.setFont(QFont("Arial", 18))
        riccardo_row.addWidget(riccardo_icon)

        riccardo_info = QLabel("<b>Riccardo</b> - Voce maschile, veloce (~30 MB)")
        riccardo_info.setStyleSheet("color: #1565c0;")
        riccardo_row.addWidget(riccardo_info, 1)

        self.install_riccardo_btn = ModernButton("Scarica", "purple")
        self.install_riccardo_btn.setFixedWidth(90)
        self.install_riccardo_btn.clicked.connect(lambda: self.install_voice("riccardo"))
        riccardo_row.addWidget(self.install_riccardo_btn)

        voices_layout.addLayout(riccardo_row)

        # Pulsante scarica tutte
        script_btn = ModernButton("📥 Scarica Tutte le Voci", "blue")
        script_btn.clicked.connect(self.run_download_script)
        voices_layout.addWidget(script_btn)

        layout.addWidget(voices_group)

        # === TEST VOCE ===
        test_group = QGroupBox("Test Voce")
        test_layout = QVBoxLayout(test_group)
        test_layout.setSpacing(8)

        # Riga voce
        voice_row = QHBoxLayout()
        voice_row.addWidget(QLabel("Voce:"))
        self.voice_combo = QComboBox()
        self.voice_combo.addItems(["paola (Femminile)", "riccardo (Maschile)"])
        self.voice_combo.setMinimumWidth(200)
        voice_row.addWidget(self.voice_combo, 1)
        test_layout.addLayout(voice_row)

        # Riga testo
        text_row = QHBoxLayout()
        text_row.addWidget(QLabel("Testo:"))
        self.test_text = QLineEdit()
        self.test_text.setText("Ciao! Sono una voce italiana locale.")
        self.test_text.setMinimumWidth(200)
        text_row.addWidget(self.test_text, 1)
        test_layout.addLayout(text_row)

        # Pulsanti test
        test_btn_row = QHBoxLayout()
        self.test_btn = ModernButton("Test Voce", "blue")
        self.test_btn.clicked.connect(self.test_voice)
        test_btn_row.addWidget(self.test_btn)

        self.play_btn = ModernButton("Riproduci Audio", "green")
        self.play_btn.clicked.connect(self.play_test_audio)
        self.play_btn.setEnabled(False)
        test_btn_row.addWidget(self.play_btn)
        test_layout.addLayout(test_btn_row)

        layout.addWidget(test_group)

        # === RISULTATO ===
        result_group = QGroupBox("Risultato")
        result_layout = QVBoxLayout(result_group)
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setMaximumHeight(80)
        self.result_text.setPlaceholderText("Avvia un test per vedere i risultati...")
        result_layout.addWidget(self.result_text)
        layout.addWidget(result_group)

        # === CONFIGURAZIONE ===
        config_group = QGroupBox("Come configurare Open WebUI")
        config_layout = QVBoxLayout(config_group)
        config_layout.setSpacing(8)

        # Istruzioni
        instructions = QLabel(
            "<b>Vai in:</b> Open WebUI → Impostazioni → Audio → Sintesi Vocale (TTS)"
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("font-size: 11px; padding: 5px;")
        config_layout.addWidget(instructions)

        # Parametri con pulsanti copia
        def create_param_row(label_text, value, layout):
            row = QHBoxLayout()
            row.setSpacing(5)
            label = QLabel(f"<b>{label_text}:</b>")
            label.setMinimumWidth(80)
            label.setStyleSheet("font-size: 10px;")
            row.addWidget(label)

            field = QLineEdit(value)
            field.setReadOnly(True)
            field.setStyleSheet("font-family: Monospace; font-size: 10px; padding: 3px; background: #f5f5f5;")
            row.addWidget(field, 1)

            copy_btn = QPushButton("📋")
            copy_btn.setMaximumWidth(28)
            copy_btn.setToolTip(f"Copia {label_text}")
            copy_btn.clicked.connect(lambda: QApplication.clipboard().setText(value))
            row.addWidget(copy_btn)

            layout.addLayout(row)
            return field

        # Parametri individuali
        create_param_row("Motore TTS", "OpenAI", config_layout)
        self.url_field = create_param_row("URL API", "http://localhost:5556/v1", config_layout)
        create_param_row("Chiave API", "sk-local", config_layout)
        create_param_row("Voce", "paola", config_layout)

        # Nota Docker
        docker_row = QHBoxLayout()
        docker_row.setSpacing(5)
        docker_label = QLabel("<b>Docker URL:</b>")
        docker_label.setMinimumWidth(80)
        docker_label.setStyleSheet("font-size: 10px; color: #e67e22;")
        docker_row.addWidget(docker_label)

        docker_field = QLineEdit("http://host.docker.internal:5556/v1")
        docker_field.setReadOnly(True)
        docker_field.setStyleSheet("font-family: Monospace; font-size: 10px; padding: 3px; background: #fef5e7;")
        docker_row.addWidget(docker_field, 1)

        docker_copy = QPushButton("📋")
        docker_copy.setMaximumWidth(28)
        docker_copy.setToolTip("Copia URL Docker")
        docker_copy.clicked.connect(lambda: QApplication.clipboard().setText("http://host.docker.internal:5556/v1"))
        docker_row.addWidget(docker_copy)

        config_layout.addLayout(docker_row)

        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("background-color: #ddd;")
        config_layout.addWidget(sep)

        # docker-compose.yml
        env_label = QLabel("<b>Per docker-compose.yml</b> (copia tutto):")
        env_label.setStyleSheet("font-size: 10px;")
        config_layout.addWidget(env_label)

        self.config_text = QTextEdit()
        self.config_text.setReadOnly(True)
        self.config_text.setMaximumHeight(70)
        self.config_text.setFont(QFont("Monospace", 9))
        self.config_text.setPlainText(
            "AUDIO_TTS_ENGINE=openai\n"
            "AUDIO_TTS_OPENAI_API_BASE_URL=http://host.docker.internal:5556/v1\n"
            "AUDIO_TTS_OPENAI_API_KEY=sk-local\n"
            "AUDIO_TTS_VOICE=paola"
        )
        config_layout.addWidget(self.config_text)

        btn_row = QHBoxLayout()
        copy_btn = ModernButton("📋 Copia Tutto", "blue")
        copy_btn.clicked.connect(self.copy_config)
        btn_row.addWidget(copy_btn)

        apply_btn = ModernButton("Applica a docker-compose.yml", "orange")
        apply_btn.clicked.connect(self.apply_config)
        btn_row.addWidget(apply_btn)

        config_layout.addLayout(btn_row)
        layout.addWidget(config_group)

        layout.addStretch()

        scroll.setWidget(content)
        main_layout.addWidget(scroll)

        # Check iniziale
        QTimer.singleShot(1000, self.check_service_status)

    def check_service_status(self):
        """Verifica stato servizio TTS locale."""
        try:
            import requests
            resp = requests.get(f"{self.tts_service_url}/", timeout=3)
            if resp.status_code == 200:
                data = resp.json()
                models = data.get("models_installed", [])
                piper_ok = data.get("piper_installed", False)

                if piper_ok and models:
                    self.status_indicator.setStyleSheet("color: #27ae60;")
                    self.status_label.setText(f"Attivo - OFFLINE ({len(models)} voci)")
                    self.test_btn.setEnabled(True)
                    self.play_btn.setEnabled(False)  # Reset play button
                elif piper_ok:
                    self.status_indicator.setStyleSheet("color: #f39c12;")
                    self.status_label.setText("Attivo - Scarica le voci")
                    self.test_btn.setEnabled(False)
                else:
                    self.status_indicator.setStyleSheet("color: #f39c12;")
                    self.status_label.setText("Attivo - Installa Piper")
                    self.test_btn.setEnabled(False)

                self.start_service_btn.setEnabled(False)

                # Aggiorna stato voci
                if "paola" in models:
                    self.paola_status.setStyleSheet("color: #27ae60;")
                    self.paola_status.setToolTip("Installata")
                    self.install_paola_btn.setText("✓ OK")
                    self.install_paola_btn.setEnabled(False)
                else:
                    self.paola_status.setStyleSheet("color: #bdc3c7;")
                    self.paola_status.setToolTip("Non installata")
                    self.install_paola_btn.setText("Scarica")
                    self.install_paola_btn.setEnabled(True)

                if "riccardo" in models:
                    self.riccardo_status.setStyleSheet("color: #27ae60;")
                    self.riccardo_status.setToolTip("Installato")
                    self.install_riccardo_btn.setText("✓ OK")
                    self.install_riccardo_btn.setEnabled(False)
                else:
                    self.riccardo_status.setStyleSheet("color: #bdc3c7;")
                    self.riccardo_status.setToolTip("Non installato")
                    self.install_riccardo_btn.setText("Scarica")
                    self.install_riccardo_btn.setEnabled(True)
            else:
                self._set_service_offline()
        except Exception as e:
            self._set_service_offline()
            print(f"[TTS] Errore check status: {e}")

    def _set_service_offline(self):
        self.status_indicator.setStyleSheet("color: #e74c3c;")
        self.status_label.setText("Non attivo - Avvia il servizio")
        self.start_service_btn.setEnabled(True)
        self.test_btn.setEnabled(False)
        # Reset stato voci
        self.paola_status.setStyleSheet("color: #bdc3c7;")
        self.riccardo_status.setStyleSheet("color: #bdc3c7;")

    def run_download_script(self):
        """Esegue lo script per scaricare tutte le voci."""
        script_path = SCRIPT_DIR / "tts_service" / "download_voices.py"
        if not script_path.exists():
            QMessageBox.warning(
                self, "Script non trovato",
                f"Script non trovato:\n{script_path}\n\n"
                "Usa i pulsanti 'Scarica' per ogni voce."
            )
            return

        reply = QMessageBox.question(
            self, "Scarica Voci",
            "Vuoi scaricare Piper TTS e tutte le voci italiane?\n\n"
            "Verranno scaricati:\n"
            "• Piper TTS (~15 MB)\n"
            "• Voce Paola (~30 MB)\n"
            "• Voce Riccardo (~30 MB)\n\n"
            "Totale: ~75 MB",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.result_text.setPlainText("Avvio download in corso...\nControlla la finestra del terminale.")
            QApplication.processEvents()

            if IS_WINDOWS:
                subprocess.Popen(
                    ['cmd', '/c', 'start', 'Download Voci', 'python', str(script_path)],
                    cwd=SCRIPT_DIR
                )
            else:
                subprocess.Popen(
                    ['x-terminal-emulator', '-e', 'python3', str(script_path)],
                    cwd=SCRIPT_DIR
                )

            # Refresh dopo un po'
            QTimer.singleShot(10000, self.check_service_status)

    def start_tts_service(self):
        """Avvia servizio TTS locale."""
        if IS_WINDOWS:
            subprocess.Popen(
                ['cmd', '/c', 'start', 'TTS Local', 'python', 'tts_service/tts_local.py'],
                cwd=SCRIPT_DIR
            )
        else:
            subprocess.Popen(
                ['python3', 'tts_service/tts_local.py'],
                cwd=SCRIPT_DIR,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        self.status_label.setText("Avvio in corso...")
        QTimer.singleShot(3000, self.check_service_status)

    def install_voice(self, voice_id):
        """Installa una voce italiana."""
        try:
            import requests
            self.result_text.setPlainText(f"Download voce {voice_id} in corso...\nQuesto potrebbe richiedere qualche minuto.")
            QApplication.processEvents()

            resp = requests.post(f"{self.tts_service_url}/install/{voice_id}", timeout=300)
            if resp.status_code == 200:
                result = resp.json()
                if result.get("success"):
                    self.result_text.setPlainText(f"Voce {voice_id} installata con successo!")
                    self.check_service_status()
                else:
                    self.result_text.setPlainText(f"Errore: {result}")
            else:
                self.result_text.setPlainText(f"Errore HTTP: {resp.status_code}")
        except Exception as e:
            self.result_text.setPlainText(f"Errore: {e}")

    def test_voice(self):
        """Testa la voce selezionata."""
        try:
            import requests
            voice = self.voice_combo.currentText().split(" ")[0]  # "paola (Femminile)" -> "paola"
            text = self.test_text.text().strip()

            if not text:
                self.result_text.setPlainText("Inserisci un testo da sintetizzare!")
                return

            self.result_text.setPlainText(f"Sintesi in corso con voce '{voice}'...")
            self.test_btn.setEnabled(False)
            QApplication.processEvents()

            data = {"voice": voice, "text": text}
            resp = requests.post(f"{self.tts_service_url}/test", data=data, timeout=30)

            self.test_btn.setEnabled(True)

            if resp.status_code == 200:
                result = resp.json()
                if result.get("success"):
                    self.result_text.setPlainText(
                        f"✓ Test completato!\n"
                        f"Voce: {result.get('voice')}\n"
                        f"Dimensione: {result.get('audio_size_kb')} KB\n"
                        f"Tempo: {result.get('synthesis_time_ms')} ms\n"
                        f"Offline: {'SI' if result.get('offline') else 'NO'}"
                    )
                    self.play_btn.setEnabled(True)
                else:
                    self.result_text.setPlainText(f"✗ Errore: {result.get('error')}")
                    self.play_btn.setEnabled(False)
            else:
                self.result_text.setPlainText(f"✗ Errore HTTP: {resp.status_code}")
                self.play_btn.setEnabled(False)
        except Exception as e:
            self.test_btn.setEnabled(True)
            self.result_text.setPlainText(f"✗ Errore: {e}\n\nAssicurati che il servizio TTS sia attivo.")
            self.play_btn.setEnabled(False)

    def play_test_audio(self):
        """Riproduce l'audio di test tramite Qt (cross-platform)."""
        try:
            import requests
            import tempfile

            # Scarica l'audio in un file temporaneo
            audio_url = f"{self.tts_service_url}/test-audio"

            self.play_btn.setEnabled(False)
            self.result_text.setPlainText(
                self.result_text.toPlainText().split("\n\n▶")[0] + "\n\n⏳ Download audio..."
            )
            QApplication.processEvents()

            resp = requests.get(audio_url, timeout=10)

            if resp.status_code == 200:
                # Salva in file temporaneo
                self.audio_file = Path(tempfile.gettempdir()) / "tts_test_audio.wav"
                self.audio_file.write_bytes(resp.content)

                # Riproduci con QMediaPlayer se disponibile
                if self.player and HAS_MULTIMEDIA:
                    url = QUrl.fromLocalFile(str(self.audio_file))
                    self.player.setMedia(QMediaContent(url))
                    self.player.play()
                    self.result_text.setPlainText(
                        self.result_text.toPlainText().split("\n\n⏳")[0] + "\n\n▶ Audio in riproduzione..."
                    )
                else:
                    # Fallback: apri con app di sistema
                    self._play_with_system(str(self.audio_file))
                    self.play_btn.setEnabled(True)
            else:
                self.result_text.setPlainText(f"✗ Errore download audio: {resp.status_code}")
                self.play_btn.setEnabled(True)
        except Exception as e:
            self.result_text.setPlainText(f"✗ Errore riproduzione: {e}")
            self.play_btn.setEnabled(True)

    def _play_with_system(self, filepath):
        """Fallback: riproduce con app di sistema."""
        try:
            if IS_WINDOWS:
                os.startfile(filepath)
            elif IS_MAC:
                subprocess.Popen(['open', filepath], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            else:
                subprocess.Popen(['xdg-open', filepath], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self.result_text.setPlainText(
                self.result_text.toPlainText().split("\n\n⏳")[0] + "\n\n▶ Audio aperto nel player di sistema"
            )
        except Exception as e:
            self.result_text.setPlainText(f"✗ Errore apertura player: {e}")

    def _on_player_state_changed(self, state):
        """Callback quando cambia lo stato del player."""
        if state == QMediaPlayer.StoppedState:
            self.play_btn.setEnabled(True)
            current = self.result_text.toPlainText()
            if "▶ Audio in riproduzione" in current:
                self.result_text.setPlainText(
                    current.replace("▶ Audio in riproduzione...", "✓ Riproduzione completata")
                )
        elif state == QMediaPlayer.PlayingState:
            self.play_btn.setEnabled(False)

    def _on_player_error(self, error):
        """Callback per errori del player."""
        if error != QMediaPlayer.NoError:
            error_msg = self.player.errorString() if self.player else "Errore sconosciuto"
            self.result_text.setPlainText(f"✗ Errore player: {error_msg}")
            self.play_btn.setEnabled(True)
            # Fallback al player di sistema
            if self.audio_file and self.audio_file.exists():
                self._play_with_system(str(self.audio_file))

    def copy_config(self):
        """Copia configurazione."""
        QApplication.clipboard().setText(self.config_text.toPlainText())
        QMessageBox.information(self, "Copiato", "Configurazione copiata!")

    def apply_config(self):
        """Applica configurazione al docker-compose.yml."""
        compose_file = SCRIPT_DIR / "docker-compose.yml"
        if not compose_file.exists():
            QMessageBox.warning(self, "Errore", "docker-compose.yml non trovato")
            return

        reply = QMessageBox.question(
            self, "Conferma",
            "Vuoi modificare docker-compose.yml per usare le voci italiane locali?\n\n"
            "Verrà creato un backup del file originale.",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            # Backup
            backup_file = SCRIPT_DIR / "docker-compose.yml.backup"
            shutil.copy(compose_file, backup_file)

            # Leggi e modifica
            content = compose_file.read_text()

            # Sostituisci configurazione TTS
            replacements = [
                ("AUDIO_TTS_OPENAI_API_BASE_URL=http://openedai-speech:8000/v1",
                 "AUDIO_TTS_OPENAI_API_BASE_URL=http://host.docker.internal:5556/v1"),
                ("AUDIO_TTS_VOICE=alloy", "AUDIO_TTS_VOICE=paola"),
                ("AUDIO_TTS_OPENAI_API_KEY=sk-111111111", "AUDIO_TTS_OPENAI_API_KEY=sk-local"),
            ]

            for old, new in replacements:
                content = content.replace(old, new)

            compose_file.write_text(content)

            QMessageBox.information(
                self, "Fatto",
                "docker-compose.yml aggiornato!\n\n"
                "Riavvia Open WebUI con:\n"
                "docker compose down && docker compose up -d"
            )


class CloudLocaleWidget(QWidget):
    """Widget Cloud Locale - Archiviazione privata per Open WebUI"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        self.settings = QSettings("OpenWebUI", "Manager")
        self.current_path = None
        self.last_result = None
        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(8, 8, 8, 8)

        # === HEADER: Titolo + Cartella Privata ===
        header_group = QGroupBox("Cartella Privata")
        header_layout = QVBoxLayout(header_group)
        header_layout.setContentsMargins(8, 12, 8, 8)
        header_layout.setSpacing(6)

        # Riga abilitazione + percorso
        enable_row = QHBoxLayout()

        self.enable_checkbox = QCheckBox("Abilita")
        self.enable_checkbox.setChecked(True)
        self.enable_checkbox.setStyleSheet("font-size: 11px;")
        self.enable_checkbox.stateChanged.connect(self.toggle_private_folder)
        enable_row.addWidget(self.enable_checkbox)

        self.path_label = QLabel("Nessuna cartella")
        self.path_label.setStyleSheet("""
            QLabel {
                background-color: #ecf0f1;
                border: 1px solid #bdc3c7;
                border-radius: 3px;
                padding: 5px 8px;
                font-family: Monospace;
                font-size: 10px;
            }
        """)
        enable_row.addWidget(self.path_label, 1)

        self.select_folder_btn = ModernButton("📁 Sfoglia", "blue")
        self.select_folder_btn.setMaximumWidth(80)
        self.select_folder_btn.setMinimumHeight(30)
        self.select_folder_btn.clicked.connect(self.select_private_folder)
        enable_row.addWidget(self.select_folder_btn)

        header_layout.addLayout(enable_row)
        layout.addWidget(header_group)

        # === ESPLORA FILE ===
        browser_group = QGroupBox("Esplora File")
        browser_layout = QVBoxLayout(browser_group)
        browser_layout.setContentsMargins(5, 12, 5, 5)
        browser_layout.setSpacing(5)

        # Toolbar navigazione compatta
        nav_row = QHBoxLayout()
        nav_row.setSpacing(3)

        self.back_btn = QPushButton("◀")
        self.back_btn.setMaximumWidth(30)
        self.back_btn.setMinimumHeight(26)
        self.back_btn.clicked.connect(self.go_back)
        nav_row.addWidget(self.back_btn)

        self.up_btn = QPushButton("▲")
        self.up_btn.setMaximumWidth(30)
        self.up_btn.setMinimumHeight(26)
        self.up_btn.clicked.connect(self.go_up)
        nav_row.addWidget(self.up_btn)

        self.home_btn = QPushButton("⌂")
        self.home_btn.setMaximumWidth(30)
        self.home_btn.setMinimumHeight(26)
        self.home_btn.clicked.connect(self.go_home)
        nav_row.addWidget(self.home_btn)

        self.refresh_btn = QPushButton("↻")
        self.refresh_btn.setMaximumWidth(30)
        self.refresh_btn.setMinimumHeight(26)
        self.refresh_btn.clicked.connect(self.refresh_view)
        nav_row.addWidget(self.refresh_btn)

        self.current_path_label = QLabel("")
        self.current_path_label.setStyleSheet("font-size: 10px; color: #7f8c8d; padding-left: 5px;")
        nav_row.addWidget(self.current_path_label, 1)

        browser_layout.addLayout(nav_row)

        # File System Model e TreeView
        self.file_model = QFileSystemModel()
        self.file_model.setRootPath("")
        self.file_model.setFilter(QDir.AllEntries | QDir.NoDotAndDotDot)

        self.tree_view = QTreeView()
        self.tree_view.setModel(self.file_model)
        self.tree_view.setAlternatingRowColors(True)
        self.tree_view.setSortingEnabled(True)
        self.tree_view.setSelectionMode(QAbstractItemView.SingleSelection)

        # Configura colonne
        self.tree_view.setColumnWidth(0, 250)
        self.tree_view.setColumnHidden(2, True)  # Tipo

        # Stile compatto
        self.tree_view.setStyleSheet("""
            QTreeView {
                border: 1px solid #bdc3c7;
                border-radius: 3px;
                background-color: white;
                font-size: 11px;
            }
            QTreeView::item {
                padding: 2px;
            }
            QTreeView::item:hover {
                background-color: #e8f4fc;
            }
            QTreeView::item:selected {
                background-color: #3498db;
                color: white;
            }
        """)

        self.tree_view.doubleClicked.connect(self.on_item_double_clicked)
        self.tree_view.clicked.connect(self.on_item_clicked)

        browser_layout.addWidget(self.tree_view, 1)  # Stretch per occupare spazio

        # Info file + Azioni in una riga
        info_actions_row = QHBoxLayout()
        info_actions_row.setSpacing(8)

        self.file_info_label = QLabel("Seleziona un file")
        self.file_info_label.setStyleSheet("""
            QLabel {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 3px;
                padding: 6px;
                font-size: 10px;
            }
        """)
        info_actions_row.addWidget(self.file_info_label, 1)

        # Pulsanti azione compatti
        self.export_base64_btn = QPushButton("Base64")
        self.export_base64_btn.setMinimumHeight(28)
        self.export_base64_btn.setStyleSheet("font-size: 10px; padding: 4px 8px;")
        self.export_base64_btn.clicked.connect(self.export_to_base64)
        self.export_base64_btn.setEnabled(False)
        info_actions_row.addWidget(self.export_base64_btn)

        self.open_file_btn = QPushButton("Apri")
        self.open_file_btn.setMinimumHeight(28)
        self.open_file_btn.setStyleSheet("font-size: 10px; padding: 4px 8px;")
        self.open_file_btn.clicked.connect(self.open_selected_file)
        self.open_file_btn.setEnabled(False)
        info_actions_row.addWidget(self.open_file_btn)

        self.copy_path_btn = QPushButton("Percorso")
        self.copy_path_btn.setMinimumHeight(28)
        self.copy_path_btn.setStyleSheet("font-size: 10px; padding: 4px 8px;")
        self.copy_path_btn.clicked.connect(self.copy_file_path)
        self.copy_path_btn.setEnabled(False)
        info_actions_row.addWidget(self.copy_path_btn)

        self.copy_result_btn = QPushButton("📋 Copia")
        self.copy_result_btn.setMinimumHeight(28)
        self.copy_result_btn.setStyleSheet("font-size: 10px; padding: 4px 8px; background-color: #9b59b6; color: white;")
        self.copy_result_btn.clicked.connect(self.copy_result)
        self.copy_result_btn.setEnabled(False)
        info_actions_row.addWidget(self.copy_result_btn)

        browser_layout.addLayout(info_actions_row)

        # Risultato esportazione (compatto)
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setMaximumHeight(50)
        self.result_text.setPlaceholderText("Risultato esportazione...")
        self.result_text.setFont(QFont("Monospace", 9))
        self.result_text.setStyleSheet("border: 1px solid #ddd; border-radius: 3px;")
        browser_layout.addWidget(self.result_text)

        layout.addWidget(browser_group, 1)  # Stretch per occupare spazio

        # === ISTRUZIONI ===
        help_group = QGroupBox("Come usare in Open WebUI")
        help_layout = QVBoxLayout(help_group)
        help_layout.setContentsMargins(8, 12, 8, 8)
        help_layout.setSpacing(6)

        help_text = QLabel(
            "<b>1. Immagini:</b> Seleziona file → Base64 → Copia → Incolla nella chat<br>"
            "<b>2. Documenti:</b> Crea Knowledge Base, poi scrivi nella chat:"
        )
        help_text.setWordWrap(True)
        help_text.setStyleSheet("font-size: 10px;")
        help_layout.addWidget(help_text)

        # Riga comando con pulsante copia
        cmd_row = QHBoxLayout()
        cmd_row.setSpacing(5)

        self.kb_command = QLineEdit("@nome_knowledge dimmi cosa contiene questo documento")
        self.kb_command.setReadOnly(True)
        self.kb_command.setStyleSheet("font-family: Monospace; font-size: 10px; padding: 4px;")
        cmd_row.addWidget(self.kb_command, 1)

        copy_kb_btn = QPushButton("📋")
        copy_kb_btn.setMaximumWidth(30)
        copy_kb_btn.setToolTip("Copia comando")
        copy_kb_btn.clicked.connect(lambda: QApplication.clipboard().setText(self.kb_command.text()))
        cmd_row.addWidget(copy_kb_btn)

        help_layout.addLayout(cmd_row)

        # Nota
        note = QLabel("<i>Sostituisci 'nome_knowledge' con il nome della tua Knowledge Base</i>")
        note.setStyleSheet("font-size: 9px; color: #666;")
        help_layout.addWidget(note)

        layout.addWidget(help_group)

    def toggle_private_folder(self, state):
        """Abilita/disabilita la cartella privata"""
        enabled = state == Qt.Checked
        self.tree_view.setEnabled(enabled)
        self.select_folder_btn.setEnabled(enabled)
        self.back_btn.setEnabled(enabled)
        self.up_btn.setEnabled(enabled)
        self.home_btn.setEnabled(enabled)
        self.refresh_btn.setEnabled(enabled)

        if not enabled:
            self.export_base64_btn.setEnabled(False)
            self.open_file_btn.setEnabled(False)
            self.copy_path_btn.setEnabled(False)

    def load_settings(self):
        """Carica le impostazioni salvate"""
        private_folder = self.settings.value("private_folder", "")
        if private_folder and Path(private_folder).exists():
            self.set_private_folder(private_folder)
        else:
            # Default: cartella home
            home = str(Path.home())
            self.set_private_folder(home)

    def save_settings(self):
        """Salva le impostazioni"""
        if self.current_path:
            self.settings.setValue("private_folder", self.current_path)

    def select_private_folder(self):
        """Apre dialog per selezionare la cartella privata"""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Seleziona Cartella Privata",
            self.current_path or str(Path.home())
        )
        if folder:
            self.set_private_folder(folder)
            self.save_settings()

    def set_private_folder(self, folder_path):
        """Imposta la cartella privata"""
        self.current_path = folder_path
        self.path_label.setText(folder_path)

        # Aggiorna il tree view
        index = self.file_model.setRootPath(folder_path)
        self.tree_view.setRootIndex(index)
        self.current_path_label.setText(folder_path)

    def go_back(self):
        """Torna alla cartella precedente"""
        # Usa la history del modello
        self.go_up()

    def go_up(self):
        """Vai alla cartella superiore"""
        if self.current_path:
            parent = str(Path(self.current_path).parent)
            if Path(parent).exists():
                self.set_private_folder(parent)

    def go_home(self):
        """Torna alla cartella privata principale"""
        private_folder = self.settings.value("private_folder", str(Path.home()))
        if Path(private_folder).exists():
            self.set_private_folder(private_folder)

    def refresh_view(self):
        """Aggiorna la vista"""
        if self.current_path:
            self.set_private_folder(self.current_path)

    def on_item_clicked(self, index):
        """Gestisce il click su un elemento"""
        file_path = self.file_model.filePath(index)
        file_info = QFileInfo(file_path)

        if file_info.isFile():
            size_kb = file_info.size() / 1024
            size_str = f"{size_kb:.1f}KB" if size_kb < 1024 else f"{size_kb/1024:.1f}MB"

            self.file_info_label.setText(
                f"📄 {file_info.fileName()} ({size_str})"
            )

            self.export_base64_btn.setEnabled(True)
            self.open_file_btn.setEnabled(True)
            self.copy_path_btn.setEnabled(True)
        else:
            self.file_info_label.setText(f"📁 {file_info.fileName()}")
            self.export_base64_btn.setEnabled(False)
            self.open_file_btn.setEnabled(True)
            self.copy_path_btn.setEnabled(True)

    def on_item_double_clicked(self, index):
        """Gestisce il doppio click su un elemento"""
        file_path = self.file_model.filePath(index)
        file_info = QFileInfo(file_path)

        if file_info.isDir():
            self.set_private_folder(file_path)
        else:
            self.open_selected_file()

    def get_selected_file_path(self):
        """Ottiene il percorso del file selezionato"""
        indexes = self.tree_view.selectedIndexes()
        if indexes:
            return self.file_model.filePath(indexes[0])
        return None

    def export_to_base64(self):
        """Esporta il file selezionato in Base64"""
        file_path = self.get_selected_file_path()
        if not file_path:
            return

        try:
            import base64
            import mimetypes

            file_info = QFileInfo(file_path)
            file_size = file_info.size()

            # Limite 10 MB
            if file_size > 10 * 1024 * 1024:
                QMessageBox.warning(
                    self, "File troppo grande",
                    "Il file è troppo grande (>10 MB).\n"
                    "Seleziona un file più piccolo."
                )
                return

            # Leggi e converti
            with open(file_path, 'rb') as f:
                data = f.read()

            base64_data = base64.b64encode(data).decode('utf-8')

            # Determina MIME type
            mime_type, _ = mimetypes.guess_type(file_path)
            if not mime_type:
                mime_type = "application/octet-stream"

            # Crea data URI
            data_uri = f"data:{mime_type};base64,{base64_data}"

            self.last_result = data_uri
            self.copy_result_btn.setEnabled(True)

            # Mostra risultato
            base64_len = len(base64_data)
            compatible = "SI" if base64_len < 40000 else "NO (troppo grande per chat)"

            self.result_text.setPlainText(
                f"✓ Esportato: {file_info.fileName()}\n"
                f"Tipo: {mime_type}\n"
                f"Lunghezza Base64: {base64_len:,} caratteri\n"
                f"Compatibile chat: {compatible}"
            )

        except Exception as e:
            self.result_text.setPlainText(f"✗ Errore: {str(e)}")
            self.copy_result_btn.setEnabled(False)

    def open_selected_file(self):
        """Apre il file/cartella selezionato con l'applicazione predefinita"""
        file_path = self.get_selected_file_path()
        if file_path:
            QDesktopServices.openUrl(QUrl.fromLocalFile(file_path))

    def copy_file_path(self):
        """Copia il percorso del file negli appunti"""
        file_path = self.get_selected_file_path()
        if file_path:
            QApplication.clipboard().setText(file_path)
            self.result_text.setPlainText(f"📎 Percorso copiato:\n{file_path}")

    def copy_result(self):
        """Copia il risultato Base64 negli appunti"""
        if self.last_result:
            QApplication.clipboard().setText(self.last_result)
            current = self.result_text.toPlainText()
            self.result_text.setPlainText(current + "\n\n✓ Copiato negli appunti!")


class InfoWidget(QWidget):
    """Widget con informazioni sul progetto"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        # Titolo
        title = QLabel("Open WebUI Manager")
        title.setFont(QFont("Arial", 28, QFont.Bold))
        title.setStyleSheet("color: #2c3e50;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Cosa fa
        desc_group = QGroupBox("Cosa fa questo programma")
        desc_group.setFont(QFont("Arial", 12, QFont.Bold))
        desc_layout = QVBoxLayout(desc_group)
        desc_layout.setContentsMargins(15, 20, 15, 15)

        desc_info = QLabel(
            "Questo programma gestisce un sistema di intelligenza artificiale locale "
            "basato su <b>Open WebUI</b> e <b>Ollama</b>.<br><br>"
            "Permette di:<br>"
            "• Avviare e fermare i servizi AI con un click<br>"
            "• Scaricare e gestire modelli di linguaggio (LLM)<br>"
            "• Convertire immagini per la compatibilità con la chat<br>"
            "• Usare la sintesi vocale italiana offline<br>"
            "• Accedere all'interfaccia web da cellulare e tablet<br><br>"
            "Tutto funziona <b>localmente</b> sul tuo computer, senza inviare dati a server esterni."
        )
        desc_info.setWordWrap(True)
        desc_info.setStyleSheet("font-size: 13px; line-height: 1.5;")
        desc_layout.addWidget(desc_info)
        layout.addWidget(desc_group)

        # Ringraziamenti
        thanks_group = QGroupBox("Ringraziamenti")
        thanks_group.setFont(QFont("Arial", 12, QFont.Bold))
        thanks_layout = QVBoxLayout(thanks_group)
        thanks_layout.setContentsMargins(15, 20, 15, 15)

        thanks_info = QLabel(
            "Grazie per aver scelto di usare questo programma!<br><br>"
            "Spero che ti sia utile per esplorare il mondo dell'intelligenza artificiale "
            "in modo semplice e privato, direttamente dal tuo computer.<br><br>"
            "<b>Autore:</b> Paolo Lo Bello"
        )
        thanks_info.setWordWrap(True)
        thanks_info.setAlignment(Qt.AlignCenter)
        thanks_info.setStyleSheet("font-size: 13px; line-height: 1.5;")
        thanks_layout.addWidget(thanks_info)
        layout.addWidget(thanks_group)

        layout.addStretch()


class MainWindow(QMainWindow):
    """Finestra principale"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Open WebUI Manager")
        self.setMinimumSize(900, 700)
        self.worker = None

        self.setup_ui()
        self.setup_tray()
        self.start_status_checker()

        # Stile globale
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f6fa;
            }
            QGroupBox {
                background-color: white;
                border: 1px solid #dcdde1;
                border-radius: 8px;
                margin-top: 12px;
                padding: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 5px;
                color: #2c3e50;
            }
            QListWidget {
                border: 1px solid #dcdde1;
                border-radius: 6px;
                padding: 5px;
            }
            QLineEdit, QComboBox {
                padding: 8px;
                border: 1px solid #dcdde1;
                border-radius: 6px;
                background: white;
            }
            QLineEdit:focus, QComboBox:focus {
                border-color: #3498db;
            }
            QTabWidget::pane {
                border: none;
                background: transparent;
            }
            QTabBar::tab {
                background: #ecf0f1;
                border: none;
                padding: 12px 20px;
                margin-right: 2px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
            }
            QTabBar::tab:selected {
                background: white;
                color: #3498db;
                font-weight: bold;
            }
            QTabBar::tab:hover:!selected {
                background: #dfe6e9;
            }
        """)

    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)

        # Tab widget
        self.tabs = QTabWidget()
        self.tabs.setFont(QFont("Arial", 11))

        # Pagine
        self.dashboard = DashboardWidget(self)
        self.logs = LogsWidget(self)
        self.models = ModelsWidget(self)
        self.config = ConfigWidget(self)
        self.cloud_locale = CloudLocaleWidget(self)
        self.tts_widget = TTSWidget(self)
        self.info_widget = InfoWidget(self)

        self.tabs.addTab(self.dashboard, "🏠 Dashboard")
        self.tabs.addTab(self.logs, "📜 Log")
        self.tabs.addTab(self.models, "🤖 Modelli")
        self.tabs.addTab(self.cloud_locale, "☁️ Cloud Locale")
        self.tabs.addTab(self.tts_widget, "🔊 Voce")
        self.tabs.addTab(self.config, "⚙️ Configurazione")
        self.tabs.addTab(self.info_widget, "ℹ️ Informazioni")

        layout.addWidget(self.tabs)

        # Status bar
        self.statusBar().showMessage("Pronto")

    def setup_tray(self):
        """Configura icona nel system tray"""
        self.tray = QSystemTrayIcon(self)
        self.tray.setToolTip("Open WebUI Manager")

        # Carica icona da file
        icon_path = SCRIPT_DIR / "ICONA" / "ICONA_Trasparente.png"
        if icon_path.exists():
            icon = QIcon(str(icon_path))
        else:
            # Fallback: crea icona programmaticamente
            pixmap = QPixmap(64, 64)
            pixmap.fill(QColor("#3498db"))
            icon = QIcon(pixmap)

        self.tray.setIcon(icon)
        self.setWindowIcon(icon)

        # Menu tray
        tray_menu = QMenu()

        show_action = QAction("Mostra", self)
        show_action.triggered.connect(self.show)
        tray_menu.addAction(show_action)

        tray_menu.addSeparator()

        start_action = QAction("Avvia Servizi", self)
        start_action.triggered.connect(lambda: self.run_command(f"{DOCKER_COMPOSE} up -d", "Avvio..."))
        tray_menu.addAction(start_action)

        stop_action = QAction("Ferma Servizi", self)
        stop_action.triggered.connect(lambda: self.run_command(f"{DOCKER_COMPOSE} down", "Arresto..."))
        tray_menu.addAction(stop_action)

        browser_action = QAction("Apri Browser", self)
        browser_action.triggered.connect(self.open_browser_tray)
        tray_menu.addAction(browser_action)

        tray_menu.addSeparator()

        quit_action = QAction("Esci", self)
        quit_action.triggered.connect(QApplication.quit)
        tray_menu.addAction(quit_action)

        self.tray.setContextMenu(tray_menu)
        self.tray.activated.connect(self.tray_activated)
        self.tray.show()

    def tray_activated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            self.show()
            self.raise_()  # Funziona meglio su Wayland

    def open_browser_tray(self):
        url = 'http://localhost:3000'
        if IS_WINDOWS:
            os.startfile(url)
        elif IS_MAC:
            subprocess.Popen(['open', url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            subprocess.Popen(['xdg-open', url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def start_status_checker(self):
        """Avvia il thread per controllare lo stato"""
        self.status_checker = StatusChecker()
        self.status_checker.status_signal.connect(self.update_status)
        self.status_checker.start()

    def update_status(self, status):
        self.dashboard.update_status(status)

        # Aggiorna status bar
        ollama = "✓" if status.get('ollama') else "✗"
        webui = "✓" if status.get('openwebui') else "✗"
        tts = "✓" if status.get('tts') else "✗"
        self.statusBar().showMessage(f"Ollama: {ollama}  |  Open WebUI: {webui}  |  TTS: {tts}")

    def run_command(self, command, message="Esecuzione..."):
        """Esegue un comando in background"""
        self.statusBar().showMessage(message)
        self.tabs.setCurrentWidget(self.logs)
        self.logs.clear_logs()
        self.logs.append_log(f"$ {command}\n")

        self.worker = WorkerThread(command, SCRIPT_DIR)
        self.worker.output_signal.connect(self.logs.append_log)
        self.worker.finished_signal.connect(self.command_finished)
        self.worker.start()

    def command_finished(self, code):
        if code == 0:
            self.statusBar().showMessage("Completato con successo")
            self.logs.append_log("\n✓ Completato")
        else:
            self.statusBar().showMessage(f"Completato con errori (codice {code})")
            self.logs.append_log(f"\n✗ Errore (codice {code})")

        # Aggiorna lista modelli se siamo nella tab modelli
        if self.tabs.currentWidget() == self.models:
            QTimer.singleShot(1000, self.models.refresh_models)

    def closeEvent(self, event):
        """Minimizza nel tray invece di chiudere"""
        event.ignore()
        self.hide()
        self.tray.showMessage(
            "Open WebUI Manager",
            "L'applicazione è ancora in esecuzione nel system tray",
            QSystemTrayIcon.Information,
            2000
        )


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Open WebUI Manager")

    # Imposta icona applicazione
    icon_path = SCRIPT_DIR / "ICONA" / "ICONA_Trasparente.png"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))

    # Verifica argomenti (--no-startup per saltare avvio automatico)
    skip_startup = "--no-startup" in sys.argv or "-n" in sys.argv

    if not skip_startup:
        # Mostra dialog di avvio
        startup = StartupDialog()
        startup.start()
        startup.exec_()

    # Mostra finestra principale
    window = MainWindow()
    window.show()

    # Se i servizi sono attivi, apri il browser dopo 2 secondi
    if not skip_startup:
        def open_browser_delayed():
            try:
                result = subprocess.run(
                    ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", "http://localhost:3000"],
                    capture_output=True, timeout=5, text=True
                )
                if result.stdout.strip() in ["200", "302"]:
                    url = 'http://localhost:3000'
                    if IS_WINDOWS:
                        os.startfile(url)
                    elif IS_MAC:
                        subprocess.Popen(['open', url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    else:
                        subprocess.Popen(['xdg-open', url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except:
                pass

        QTimer.singleShot(2000, open_browser_delayed)

        # Avvia automaticamente il servizio TTS dopo che tutto è caricato
        def start_tts_delayed():
            try:
                # Verifica se il servizio TTS è già attivo
                result = subprocess.run(
                    ["curl", "-s", "http://localhost:5556/"],
                    capture_output=True, timeout=2
                )
                if result.returncode != 0:
                    # TTS non attivo, avvialo
                    window.tts_widget.start_tts_service()
            except:
                # Servizio non raggiungibile, avvialo
                window.tts_widget.start_tts_service()

        QTimer.singleShot(4000, start_tts_delayed)

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
