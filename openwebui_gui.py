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
    QTreeView, QFileDialog, QHeaderView, QAbstractItemView, QCheckBox,
    QTableWidget, QTableWidgetItem
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

# System Profiler per monitoraggio risorse
import sys
sys.path.insert(0, str(SCRIPTS_DIR))
try:
    from system_profiler import get_system_profile, SystemTier
    HAS_PROFILER = True
except ImportError:
    HAS_PROFILER = False

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

        # === RISORSE SISTEMA ===
        if HAS_PROFILER:
            system_group = QGroupBox("Risorse Sistema")
            system_group.setFont(QFont("Arial", 12, QFont.Bold))
            system_layout = QHBoxLayout(system_group)
            system_layout.setSpacing(20)

            # Colonna sinistra: RAM e CPU
            left_col = QVBoxLayout()

            # RAM
            ram_row = QHBoxLayout()
            self.ram_label = QLabel("RAM: --")
            self.ram_label.setFont(QFont("Arial", 10))
            ram_row.addWidget(self.ram_label)
            self.ram_bar = QProgressBar()
            self.ram_bar.setMaximumWidth(150)
            self.ram_bar.setMaximumHeight(18)
            self.ram_bar.setStyleSheet("""
                QProgressBar {
                    border: 1px solid #bdc3c7;
                    border-radius: 5px;
                    text-align: center;
                }
                QProgressBar::chunk {
                    background-color: #3498db;
                    border-radius: 4px;
                }
            """)
            ram_row.addWidget(self.ram_bar)
            left_col.addLayout(ram_row)

            # Tier sistema
            tier_row = QHBoxLayout()
            tier_row.addWidget(QLabel("Tier:"))
            self.tier_label = QLabel("--")
            self.tier_label.setFont(QFont("Arial", 10, QFont.Bold))
            tier_row.addWidget(self.tier_label)
            tier_row.addStretch()
            left_col.addLayout(tier_row)

            system_layout.addLayout(left_col)

            # Separatore
            vsep = QFrame()
            vsep.setFrameShape(QFrame.VLine)
            vsep.setStyleSheet("background-color: #ddd;")
            system_layout.addWidget(vsep)

            # Colonna destra: Limiti
            right_col = QVBoxLayout()
            self.limits_label = QLabel("Timeout TTS: -- sec")
            self.limits_label.setFont(QFont("Arial", 9))
            self.limits_label.setStyleSheet("color: #7f8c8d;")
            right_col.addWidget(self.limits_label)

            self.protection_label = QLabel("")
            self.protection_label.setFont(QFont("Arial", 9))
            right_col.addWidget(self.protection_label)

            system_layout.addLayout(right_col)

            layout.addWidget(system_group)

            # Aggiorna subito e poi ogni 5 secondi
            self.update_system_info()
            self.system_timer = QTimer()
            self.system_timer.timeout.connect(self.update_system_info)
            self.system_timer.start(5000)

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
        info_group = QGroupBox("Dettagli e links locali del tuo Computer")
        info_group.setFont(QFont("Arial", 11, QFont.Bold))
        info_layout = QVBoxLayout(info_group)
        info_layout.setSpacing(6)

        info_text = QLabel(
            "🌐 Open WebUI: <a href='http://localhost:3000'>http://localhost:3000</a><br>"
            "🤖 Ollama API: <a href='http://localhost:11434'>http://localhost:11434</a><br>"
            "🔊 TTS API: <a href='http://localhost:8000'>http://localhost:8000</a><br>"
            f"📁 Directory: {SCRIPT_DIR}<br><br>"
            "📁 <b>Archivio:</b> Gestisci file locali da usare come Knowledge Base in Open WebUI<br>"
            "🔊 <b>Voce:</b> Sintesi vocale italiana offline con Piper TTS"
        )
        info_text.setOpenExternalLinks(True)
        info_text.setFont(QFont("Arial", 10))
        info_text.setWordWrap(True)
        info_layout.addWidget(info_text)

        # Nota cellulare + link configurazione
        mobile_row = QHBoxLayout()
        mobile_row.setSpacing(8)
        mobile_label = QLabel("📱 <i>Puoi usare Open WebUI anche da iPhone e Android!</i>")
        mobile_label.setStyleSheet("font-size: 10px; color: #27ae60;")
        mobile_row.addWidget(mobile_label)
        mobile_row.addStretch()

        config_link = QPushButton("👉 Clicca per mostrare il menù")
        config_link.setStyleSheet("""
            QPushButton {
                background: none;
                border: none;
                color: #3498db;
                font-size: 10px;
                text-decoration: underline;
            }
            QPushButton:hover {
                color: #2980b9;
            }
        """)
        config_link.setCursor(Qt.PointingHandCursor)
        config_link.clicked.connect(lambda: self.main_window.tabs.setCurrentIndex(5))  # Tab Configurazione
        mobile_row.addWidget(config_link)

        info_layout.addLayout(mobile_row)
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

    def update_system_info(self):
        """Aggiorna le informazioni sul sistema."""
        if not HAS_PROFILER:
            return

        try:
            profile = get_system_profile()

            # RAM
            self.ram_label.setText(f"RAM: {profile.ram_available_gb:.1f}/{profile.ram_total_gb:.1f} GB")
            self.ram_bar.setValue(int(profile.ram_percent_used))

            # Colore barra RAM basato su utilizzo
            if profile.ram_percent_used >= profile.ram_critical_threshold:
                bar_color = "#e74c3c"  # Rosso
            elif profile.ram_percent_used >= profile.ram_warning_threshold:
                bar_color = "#f39c12"  # Arancione
            else:
                bar_color = "#27ae60"  # Verde
            self.ram_bar.setStyleSheet(f"""
                QProgressBar {{
                    border: 1px solid #bdc3c7;
                    border-radius: 5px;
                    text-align: center;
                }}
                QProgressBar::chunk {{
                    background-color: {bar_color};
                    border-radius: 4px;
                }}
            """)

            # Tier
            tier_colors = {
                SystemTier.MINIMAL: ("#e74c3c", "MINIMAL - Risorse critiche!"),
                SystemTier.LOW: ("#f39c12", "LOW - Timeout ridotti"),
                SystemTier.MEDIUM: ("#27ae60", "MEDIUM - OK"),
                SystemTier.HIGH: ("#3498db", "HIGH - Potente")
            }
            color, text = tier_colors.get(profile.tier, ("#7f8c8d", profile.tier.value))
            self.tier_label.setText(text)
            self.tier_label.setStyleSheet(f"color: {color};")

            # Limiti
            self.limits_label.setText(f"Timeout TTS: {profile.timeout_tts}s | LLM: {profile.timeout_llm}s")

            # Stato protezione
            if profile.ram_percent_used >= profile.ram_critical_threshold:
                self.protection_label.setText("⚠️ RAM critica - operazioni bloccate")
                self.protection_label.setStyleSheet("color: #e74c3c; font-weight: bold;")
            elif profile.ram_percent_used >= profile.ram_warning_threshold:
                self.protection_label.setText("⚡ RAM alta - chiudi app non necessarie")
                self.protection_label.setStyleSheet("color: #f39c12;")
            else:
                self.protection_label.setText("✓ Sistema OK")
                self.protection_label.setStyleSheet("color: #27ae60;")

        except Exception as e:
            self.tier_label.setText(f"Errore: {e}")


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
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        # Layout a due colonne
        columns = QHBoxLayout()
        columns.setSpacing(12)

        # === COLONNA SINISTRA: Modelli Installati ===
        left_col = QVBoxLayout()
        left_col.setSpacing(8)

        models_group = QGroupBox("Modelli Installati")
        models_layout = QVBoxLayout(models_group)
        models_layout.setContentsMargins(10, 12, 10, 10)

        self.models_list = QListWidget()
        self.models_list.setFont(QFont("Monospace", 10))
        self.models_list.setStyleSheet("QListWidget::item { padding: 4px; }")
        models_layout.addWidget(self.models_list)

        btn_refresh = ModernButton("🔄 Aggiorna Lista", "blue")
        btn_refresh.clicked.connect(self.refresh_models)
        models_layout.addWidget(btn_refresh)

        left_col.addWidget(models_group)
        columns.addLayout(left_col, 1)

        # === COLONNA DESTRA: Modelli Consigliati + Azioni ===
        right_col = QVBoxLayout()
        right_col.setSpacing(8)

        recommend_group = QGroupBox("Modelli Consigliati")
        recommend_layout = QVBoxLayout(recommend_group)
        recommend_layout.setContentsMargins(10, 12, 10, 10)
        recommend_layout.setSpacing(6)

        # Tabella capacità modelli
        # Colonne: Quotid., Generale, Coding, Vision, Math, Sentiment, Scrittura, Traduzioni, Ragionam., Agenti, Robotica
        capabilities = ["📅", "🤖", "💻", "👁️", "🔢", "💌", "✍️", "🌍", "🧠", "🤝", "⚙️"]
        cap_tooltips = ["Quotidiano", "Generale", "Coding", "Vision", "Matematica", "Sentiment", "Scrittura", "Traduzioni", "Ragionamento", "Agenti", "Robotica"]

        # Modelli con le loro capacità (True = buono, False = non adatto)
        # Ordine: Quotid, Generale, Coding, Vision, Math, Sentiment, Scrittura, Traduzioni, Ragionam, Agenti, Robotica
        models_data = {
            "llama3.1:8b":        [True,  True,  True,  False, True,  True,  True,  True,  True,  True,  True],
            "llama3.1:70b":       [True,  True,  True,  False, True,  True,  True,  True,  True,  True,  True],
            "mistral:7b":         [True,  True,  True,  False, False, True,  True,  True,  False, True,  True],
            "mixtral:8x7b":       [True,  True,  True,  False, True,  True,  True,  True,  True,  True,  True],
            "qwen2.5:7b":         [True,  True,  True,  False, True,  True,  True,  True,  True,  True,  True],
            "qwen2.5:14b":        [True,  True,  True,  False, True,  True,  True,  True,  True,  True,  True],
            "gemma2:9b":          [True,  True,  True,  False, False, True,  True,  True,  False, False, True],
            "gemma2:27b":         [True,  True,  True,  False, True,  True,  True,  True,  True,  True,  True],
            "phi3:medium":        [True,  True,  True,  False, True,  False, True,  False, True,  False, True],
            "yi:9b":              [True,  True,  True,  False, True,  True,  True,  True,  True,  True,  True],
            "yi:34b":             [True,  True,  True,  False, True,  True,  True,  True,  True,  True,  True],
            "deepseek-coder:6.7b":[False, False, True,  False, True,  False, False, False, False, False, False],
            "deepseek-coder:33b": [False, False, True,  False, True,  False, False, False, True,  False, False],
            "codellama:7b":       [False, False, True,  False, False, False, False, False, False, False, False],
            "codellama:13b":      [False, False, True,  False, False, False, False, False, False, False, False],
            "qwen2.5-coder:7b":   [False, False, True,  False, True,  False, False, False, False, True,  True],
            "codegemma:7b":       [False, False, True,  False, False, False, False, False, False, False, False],
            "starcoder2:7b":      [False, False, True,  False, False, False, False, False, False, False, False],
            "llava:7b":           [True,  True,  False, True,  False, True,  True,  False, False, False, False],
            "llava:13b":          [True,  True,  False, True,  False, True,  True,  False, True,  False, False],
            "llava:34b":          [True,  True,  False, True,  True,  True,  True,  False, True,  False, False],
            "bakllava:7b":        [True,  False, False, True,  False, True,  True,  False, False, False, False],
            "moondream:1.8b":     [False, False, False, True,  False, False, False, False, False, False, False],
            "deepseek-math:7b":   [False, False, False, False, True,  False, False, False, True,  False, False],
            "mathstral:7b":       [False, False, False, False, True,  False, False, False, True,  False, False],
            "wizard-math:7b":     [False, False, False, False, True,  False, False, False, True,  False, False],
            "stablelm2:1.6b":     [False, False, False, False, False, True,  False, False, False, False, False],
            "tinyllama:1.1b":     [False, False, False, False, False, True,  False, False, False, False, False],
            "aya:8b":             [True,  True,  False, False, False, False, True,  True,  False, False, False],
            "nous-hermes2:10.7b": [True,  True,  True,  False, False, True,  True,  True,  True,  True,  True],
            "openhermes:7b":      [True,  True,  True,  False, False, True,  True,  False, False, True,  False],
            "dolphin-mistral:7b": [True,  True,  True,  False, False, True,  True,  False, False, True,  False],
            "wizardlm2:7b":       [True,  True,  True,  False, False, True,  True,  False, True,  True,  False],
            "zephyr:7b":          [True,  True,  False, False, False, True,  True,  False, False, False, False],
            "internlm2:7b":       [True,  True,  True,  False, True,  True,  True,  True,  True,  True,  True],
            "glm4:9b":            [True,  True,  True,  False, True,  True,  True,  True,  True,  True,  True],
            "deepseek-llm:7b":    [True,  True,  True,  False, False, True,  True,  False, True,  True,  True],
        }

        self.cap_table = QTableWidget(len(models_data), len(capabilities) + 1)
        self.cap_table.setHorizontalHeaderLabels(["Modello"] + capabilities)
        self.cap_table.horizontalHeader().setDefaultSectionSize(28)
        self.cap_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.cap_table.verticalHeader().setVisible(False)
        self.cap_table.setSelectionMode(QTableWidget.NoSelection)
        self.cap_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.cap_table.setStyleSheet("""
            QTableWidget { font-size: 10px; gridline-color: #ddd; }
            QHeaderView::section { font-size: 10px; padding: 2px; }
        """)

        # Imposta tooltip per header
        for i, tip in enumerate(cap_tooltips):
            self.cap_table.horizontalHeaderItem(i + 1).setToolTip(tip)

        row = 0
        for model, caps in models_data.items():
            # Nome modello cliccabile
            model_btn = QPushButton(model)
            model_btn.setStyleSheet("""
                QPushButton {
                    font-size: 9px; text-align: left; padding: 2px 4px;
                    background: transparent; border: none; color: #2980b9;
                }
                QPushButton:hover { text-decoration: underline; background: #ecf0f1; }
            """)
            model_btn.setCursor(Qt.PointingHandCursor)
            model_btn.setToolTip(f"Clicca per scaricare {model}")
            model_btn.clicked.connect(lambda checked, m=model: self.quick_download(m))
            self.cap_table.setCellWidget(row, 0, model_btn)

            # Spunte capacità
            for col, capable in enumerate(caps):
                item = QTableWidgetItem("✓" if capable else "✗")
                item.setTextAlignment(Qt.AlignCenter)
                item.setForeground(QColor("#27ae60") if capable else QColor("#e74c3c"))
                self.cap_table.setItem(row, col + 1, item)

            self.cap_table.setRowHeight(row, 24)
            row += 1

        recommend_layout.addWidget(self.cap_table)

        # Note e links
        note_label = QLabel("<i>💡 Clicca sul nome del modello per scaricarlo · Legenda: 📅Quotidiano 💻Coding 👁️Vision 🔢Math 💌Sentiment ✍️Scrittura 🌍Traduzioni</i>")
        note_label.setStyleSheet("font-size: 8px; color: #7f8c8d;")
        note_label.setWordWrap(True)
        recommend_layout.addWidget(note_label)

        links_label = QLabel(
            "<i>🌐 Per modelli più aggiornati: "
            "<a href='https://ollama.com/library'>ollama.com</a> · "
            "<a href='https://huggingface.co/models'>huggingface.co</a> · "
            "<a href='https://kaggle.com/models'>kaggle.com</a></i>"
        )
        links_label.setOpenExternalLinks(True)
        links_label.setStyleSheet("font-size: 9px; color: #7f8c8d;")
        recommend_layout.addWidget(links_label)

        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("background-color: #ddd;")
        recommend_layout.addWidget(sep)

        # === AZIONI (dentro Modelli Consigliati) ===
        actions_label = QLabel("<b>Azioni Manuali</b>")
        actions_label.setStyleSheet("font-size: 10px; color: #2980b9;")
        recommend_layout.addWidget(actions_label)

        # Download manuale
        download_row = QHBoxLayout()
        download_row.setSpacing(6)
        self.model_combo = QComboBox()
        self.model_combo.setFont(QFont("Arial", 10))
        self.model_combo.setEditable(True)
        self.model_combo.setPlaceholderText("Scrivi nome modello...")
        download_row.addWidget(self.model_combo, 1)
        btn_download = ModernButton("⬇️ Scarica", "green")
        btn_download.clicked.connect(self.download_model)
        download_row.addWidget(btn_download)
        recommend_layout.addLayout(download_row)

        # Rimuovi (combobox con modelli installati)
        remove_row = QHBoxLayout()
        remove_row.setSpacing(6)
        self.remove_combo = QComboBox()
        self.remove_combo.setFont(QFont("Arial", 10))
        self.remove_combo.setPlaceholderText("Seleziona modello da rimuovere...")
        remove_row.addWidget(self.remove_combo, 1)
        btn_remove = ModernButton("🗑️ Rimuovi", "red")
        btn_remove.clicked.connect(self.remove_model)
        remove_row.addWidget(btn_remove)
        recommend_layout.addLayout(remove_row)

        right_col.addWidget(recommend_group)
        columns.addLayout(right_col, 1)

        layout.addLayout(columns, 1)

        # Carica modelli all'avvio
        self.refresh_models()

    def refresh_models(self):
        self.models_list.clear()
        self.remove_combo.clear()
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
                        # Estrai nome modello per il combobox rimozione
                        model_name = line.split()[0] if line.split() else ""
                        if model_name:
                            self.remove_combo.addItem(model_name)
        except Exception as e:
            self.models_list.addItem(f"Errore: {str(e)}")

    def download_model(self):
        model = self.model_combo.currentText().strip()
        if model:
            self.main_window.run_command(
                f"ollama pull {model} 2>/dev/null || docker exec -it ollama ollama pull {model}",
                f"Download {model}..."
            )

    def quick_download(self, model):
        """Scarica un modello dalla lista consigliati"""
        self.main_window.run_command(
            f"ollama pull {model} 2>/dev/null || docker exec -it ollama ollama pull {model}",
            f"Download {model}..."
        )

    def remove_model(self):
        model = self.remove_combo.currentText().strip()
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
                # Aggiorna lista dopo rimozione
                QTimer.singleShot(2000, self.refresh_models)


class ConfigWidget(QWidget):
    """Widget per le configurazioni"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        self.settings = QSettings("OpenWebUI", "Manager")
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(10, 10, 10, 10)

        title = QLabel("Configurazione")
        title.setFont(QFont("Arial", 20, QFont.Bold))
        title.setStyleSheet("color: #2c3e50;")
        layout.addWidget(title)

        # LAN Access - Layout a due colonne
        lan_group = QGroupBox("Accesso LAN (Cellulare/Tablet)")
        lan_main_layout = QHBoxLayout(lan_group)
        lan_main_layout.setSpacing(15)
        lan_main_layout.setContentsMargins(10, 12, 10, 10)

        # === COLONNA SINISTRA: Pulsanti in verticale (distanziati) ===
        left_col = QVBoxLayout()
        left_col.setSpacing(15)

        btn_lan_enable = ModernButton("🌐 Abilita LAN", "green")
        btn_lan_enable.setToolTip("Permette l'accesso da altri dispositivi sulla rete")
        btn_lan_enable.clicked.connect(self.enable_lan)
        left_col.addWidget(btn_lan_enable)

        btn_lan_disable = ModernButton("🔒 Solo Localhost", "orange")
        btn_lan_disable.setToolTip("Limita l'accesso solo a questo computer")
        btn_lan_disable.clicked.connect(self.disable_lan)
        left_col.addWidget(btn_lan_disable)

        btn_lan_refresh = ModernButton("🔄 Aggiorna IP", "blue")
        btn_lan_refresh.setToolTip("Aggiorna indirizzo IP")
        btn_lan_refresh.clicked.connect(self.update_lan_info)
        left_col.addWidget(btn_lan_refresh)

        left_col.addStretch()
        lan_main_layout.addLayout(left_col)

        # === COLONNA DESTRA: Spiegazione ===
        instructions = QLabel(
            "<div style='background-color: #e8f4fc; padding: 12px; border-radius: 6px;'>"
            "<b style='font-size: 12px;'>📱 Come collegarsi dal cellulare:</b><br><br>"
            "<b>1.</b> Connetti il cellulare alla <b>stessa rete WiFi</b> del PC<br><br>"
            "<b>2.</b> Clicca il pulsante verde <b>\"🌐 Abilita LAN\"</b><br><br>"
            "<b>3.</b> Scansiona il <b>QR code</b> oppure digita l'indirizzo mostrato<br><br>"
            "<hr style='border: 1px solid #bdd7ea;'>"
            "<small>💡 Per tornare alla modalità sicura, clicca <b>\"🔒 Solo Localhost\"</b></small>"
            "</div>"
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("font-size: 11px;")
        lan_main_layout.addWidget(instructions, 1)

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

        btn_update = ModernButton("⬆️ Aggiorna OpenWebUI", "blue")
        btn_update.setToolTip("Scarica l'ultima versione di Open WebUI")
        btn_update.clicked.connect(self.update_openwebui)
        maint_layout.addWidget(btn_update)

        btn_fix = ModernButton("🔧 Ripara", "orange")
        btn_fix.setToolTip("Riavvia i container e pulisce la cache")
        btn_fix.clicked.connect(self.fix_openwebui)
        maint_layout.addWidget(btn_fix)

        btn_backup = ModernButton("💾 Backup in USB", "green")
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

    def save_qr_setting(self, state):
        """Salva l'impostazione QR-Code LAN"""
        enabled = state == Qt.Checked
        self.settings.setValue("qr_lan_enabled", enabled)

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
        self.main_window.run_command(f"{DOCKER_COMPOSE} down && {DOCKER_COMPOSE} up -d --force-recreate", "Riparazione Open WebUI...")

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

        # === STATO SERVIZIO ===
        status_group = QGroupBox("Stato Servizio")
        status_main_layout = QVBoxLayout(status_group)
        status_main_layout.setSpacing(8)
        status_main_layout.setContentsMargins(10, 12, 10, 10)

        # Riga stato + pulsanti
        status_row = QHBoxLayout()
        self.status_indicator = QLabel("●")
        self.status_indicator.setFont(QFont("Arial", 14))
        self.status_indicator.setStyleSheet("color: #f39c12;")
        status_row.addWidget(self.status_indicator)

        self.status_label = QLabel("Verifica in corso...")
        self.status_label.setFont(QFont("Arial", 10))
        status_row.addWidget(self.status_label)
        status_row.addStretch()

        self.start_service_btn = ModernButton("Avvia Servizio", "green")
        self.start_service_btn.clicked.connect(self.start_tts_service)
        status_row.addWidget(self.start_service_btn)

        self.refresh_btn = ModernButton("Aggiorna", "gray")
        self.refresh_btn.clicked.connect(self.check_service_status)
        status_row.addWidget(self.refresh_btn)

        status_main_layout.addLayout(status_row)

        # Layout a due colonne: Voci | Test
        columns_layout = QHBoxLayout()
        columns_layout.setSpacing(15)

        # === COLONNA SINISTRA: Voci disponibili ===
        left_column = QVBoxLayout()
        left_column.setSpacing(8)

        voices_label = QLabel("<b>Voci Italiane Disponibili</b>")
        voices_label.setStyleSheet("font-size: 11px; color: #2980b9;")
        left_column.addWidget(voices_label)

        # Voce Paola
        paola_row = QHBoxLayout()
        paola_row.setSpacing(6)
        self.paola_status = QLabel("●")
        self.paola_status.setFixedWidth(14)
        self.paola_status.setStyleSheet("color: #bdc3c7;")
        paola_row.addWidget(self.paola_status)
        paola_row.addWidget(QLabel("👩 <b>Paola</b>"))
        paola_row.addStretch()
        self.install_paola_btn = ModernButton("Scarica", "purple")
        self.install_paola_btn.setFixedWidth(70)
        self.install_paola_btn.clicked.connect(lambda: self.install_voice("paola"))
        paola_row.addWidget(self.install_paola_btn)
        left_column.addLayout(paola_row)

        # Voce Riccardo
        riccardo_row = QHBoxLayout()
        riccardo_row.setSpacing(6)
        self.riccardo_status = QLabel("●")
        self.riccardo_status.setFixedWidth(14)
        self.riccardo_status.setStyleSheet("color: #bdc3c7;")
        riccardo_row.addWidget(self.riccardo_status)
        riccardo_row.addWidget(QLabel("👨 <b>Riccardo</b>"))
        riccardo_row.addStretch()
        self.install_riccardo_btn = ModernButton("Scarica", "purple")
        self.install_riccardo_btn.setFixedWidth(70)
        self.install_riccardo_btn.clicked.connect(lambda: self.install_voice("riccardo"))
        riccardo_row.addWidget(self.install_riccardo_btn)
        left_column.addLayout(riccardo_row)

        # Pulsante scarica tutte
        script_btn = ModernButton("📥 Scarica Tutte", "blue")
        script_btn.clicked.connect(self.run_download_script)
        left_column.addWidget(script_btn)

        left_column.addStretch()
        columns_layout.addLayout(left_column, 1)

        # Separatore verticale
        vsep = QFrame()
        vsep.setFrameShape(QFrame.VLine)
        vsep.setStyleSheet("background-color: #ddd;")
        columns_layout.addWidget(vsep)

        # === COLONNA DESTRA: Test voce ===
        right_column = QVBoxLayout()
        right_column.setSpacing(6)

        test_label = QLabel("<b>Test Voce</b>")
        test_label.setStyleSheet("font-size: 11px; color: #27ae60;")
        right_column.addWidget(test_label)

        # Layout orizzontale: controlli | risultato
        test_h_layout = QHBoxLayout()
        test_h_layout.setSpacing(10)

        # Controlli a sinistra (compatti)
        controls_layout = QVBoxLayout()
        controls_layout.setSpacing(5)

        # Voce
        voice_row = QHBoxLayout()
        voice_row.addWidget(QLabel("Voce:"))
        self.voice_combo = QComboBox()
        self.voice_combo.addItems(["paola", "riccardo"])
        self.voice_combo.setMinimumWidth(90)
        voice_row.addWidget(self.voice_combo)
        controls_layout.addLayout(voice_row)

        # Testo
        self.test_text = QLineEdit("Ciao!")
        self.test_text.setPlaceholderText("Testo...")
        self.test_text.setMinimumWidth(120)
        controls_layout.addWidget(self.test_text)

        # Pulsanti
        self.test_btn = ModernButton("🔊 Test", "blue")
        self.test_btn.clicked.connect(self.test_voice)
        controls_layout.addWidget(self.test_btn)

        self.play_btn = ModernButton("▶ Play", "green")
        self.play_btn.clicked.connect(self.play_test_audio)
        self.play_btn.setEnabled(False)
        controls_layout.addWidget(self.play_btn)

        controls_layout.addStretch()
        test_h_layout.addLayout(controls_layout)

        # Risultato a destra (più largo)
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setPlaceholderText("Risultato...")
        self.result_text.setStyleSheet("background: #f5f5f5; border: 1px solid #ddd; border-radius: 3px; font-size: 10px;")
        test_h_layout.addWidget(self.result_text, 1)

        right_column.addLayout(test_h_layout, 1)

        columns_layout.addLayout(right_column, 1)

        status_main_layout.addLayout(columns_layout, 1)

        layout.addWidget(status_group)

        # === CONFIGURAZIONE ===
        config_group = QGroupBox("Come configurare Open WebUI")
        config_main = QVBoxLayout(config_group)
        config_main.setSpacing(6)
        config_main.setContentsMargins(10, 10, 10, 10)

        # Istruzioni
        instructions = QLabel(
            "<b>Vai in:</b> Open WebUI → Impostazioni → Audio → Sintesi Vocale (TTS)"
        )
        instructions.setStyleSheet("font-size: 10px; padding: 3px;")
        config_main.addWidget(instructions)

        # Layout a due colonne
        columns = QHBoxLayout()
        columns.setSpacing(15)

        # === COLONNA SINISTRA: Parametri ===
        left_col = QVBoxLayout()
        left_col.setSpacing(4)

        def create_param_row(label_text, value, parent_layout):
            row = QHBoxLayout()
            row.setSpacing(4)
            label = QLabel(f"<b>{label_text}:</b>")
            label.setMinimumWidth(65)
            label.setStyleSheet("font-size: 9px;")
            row.addWidget(label)
            field = QLineEdit(value)
            field.setReadOnly(True)
            field.setStyleSheet("font-family: Monospace; font-size: 9px; padding: 2px; background: #f5f5f5;")
            row.addWidget(field, 1)
            copy_btn = QPushButton("📋")
            copy_btn.setMaximumWidth(24)
            copy_btn.setMaximumHeight(22)
            copy_btn.clicked.connect(lambda: QApplication.clipboard().setText(value))
            row.addWidget(copy_btn)
            parent_layout.addLayout(row)
            return field

        create_param_row("Motore", "OpenAI", left_col)
        create_param_row("URL API", "http://localhost:5556/v1", left_col)
        create_param_row("Chiave", "sk-local", left_col)
        create_param_row("Voce", "paola", left_col)

        left_col.addStretch()
        columns.addLayout(left_col, 1)

        # Separatore verticale
        vsep = QFrame()
        vsep.setFrameShape(QFrame.VLine)
        vsep.setStyleSheet("background-color: #ddd;")
        columns.addWidget(vsep)

        # === COLONNA DESTRA: Docker ===
        right_col = QVBoxLayout()
        right_col.setSpacing(4)

        docker_title = QLabel("<b style='color: #e67e22;'>Per Docker:</b>")
        docker_title.setStyleSheet("font-size: 10px;")
        right_col.addWidget(docker_title)

        # Docker URL
        docker_row = QHBoxLayout()
        docker_row.setSpacing(4)
        docker_field = QLineEdit("http://host.docker.internal:5556/v1")
        docker_field.setReadOnly(True)
        docker_field.setStyleSheet("font-family: Monospace; font-size: 9px; padding: 2px; background: #fef5e7;")
        docker_row.addWidget(docker_field, 1)
        docker_copy = QPushButton("📋")
        docker_copy.setMaximumWidth(24)
        docker_copy.setMaximumHeight(22)
        docker_copy.clicked.connect(lambda: QApplication.clipboard().setText("http://host.docker.internal:5556/v1"))
        docker_row.addWidget(docker_copy)
        right_col.addLayout(docker_row)

        # docker-compose.yml
        self.config_text = QTextEdit()
        self.config_text.setReadOnly(True)
        self.config_text.setMaximumHeight(55)
        self.config_text.setFont(QFont("Monospace", 8))
        self.config_text.setPlainText(
            "AUDIO_TTS_ENGINE=openai\n"
            "AUDIO_TTS_OPENAI_API_BASE_URL=http://host.docker.internal:5556/v1\n"
            "AUDIO_TTS_OPENAI_API_KEY=sk-local\n"
            "AUDIO_TTS_VOICE=paola"
        )
        right_col.addWidget(self.config_text)

        # Pulsanti
        btn_row = QHBoxLayout()
        btn_row.setSpacing(5)
        copy_btn = ModernButton("📋 Copia", "blue")
        copy_btn.clicked.connect(self.copy_config)
        btn_row.addWidget(copy_btn)
        apply_btn = ModernButton("⚙️ Applica", "orange")
        apply_btn.clicked.connect(self.apply_config)
        btn_row.addWidget(apply_btn)
        right_col.addLayout(btn_row)

        columns.addLayout(right_col, 1)

        config_main.addLayout(columns)
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
            # Usa il nuovo endpoint /voices/check per info complete
            resp = requests.get(f"{self.tts_service_url}/voices/check", timeout=3)
            if resp.status_code == 200:
                data = resp.json()
                ready = data.get("ready", False)
                models = data.get("voices_installed", [])
                missing = data.get("voices_missing", [])
                piper_available = data.get("piper_available", False)
                message = data.get("message", "")

                if ready:
                    # Sistema pronto - tutto OK
                    self.status_indicator.setStyleSheet("color: #27ae60;")
                    self.status_label.setText(f"PRONTO - {len(models)} voci installate")
                    self.test_btn.setEnabled(True)
                    self.play_btn.setEnabled(False)  # Reset play button
                    self.result_text.setPlainText(f"TTS pronto.\nVoci: {', '.join(models)}")
                elif not models:
                    # Nessuna voce installata
                    self.status_indicator.setStyleSheet("color: #e74c3c;")
                    self.status_label.setText("VOCI MANCANTI - Scarica sotto!")
                    self.test_btn.setEnabled(False)
                    self.result_text.setPlainText(
                        "⚠️ ATTENZIONE: La sintesi vocale NON funzionerà!\n\n"
                        "Devi scaricare almeno una voce italiana.\n"
                        "Usa i pulsanti 'Scarica' qui sotto."
                    )
                elif not piper_available:
                    # Piper non disponibile
                    self.status_indicator.setStyleSheet("color: #f39c12;")
                    self.status_label.setText("PIPER MANCANTE")
                    self.test_btn.setEnabled(False)
                    self.result_text.setPlainText(
                        "Piper TTS non installato.\n"
                        "Clicca 'Scarica Tutte' per installare."
                    )
                else:
                    # Stato parziale
                    self.status_indicator.setStyleSheet("color: #f39c12;")
                    self.status_label.setText(f"Parziale - {len(models)} voci")
                    self.test_btn.setEnabled(bool(models))

                self.start_service_btn.setEnabled(False)

                # Aggiorna stato voci
                if "paola" in models:
                    self.paola_status.setStyleSheet("color: #27ae60;")
                    self.paola_status.setToolTip("Installata")
                    self.install_paola_btn.setText("✓ OK")
                    self.install_paola_btn.setEnabled(False)
                else:
                    self.paola_status.setStyleSheet("color: #e74c3c;")
                    self.paola_status.setToolTip("Non installata - Clicca Scarica")
                    self.install_paola_btn.setText("Scarica")
                    self.install_paola_btn.setEnabled(True)

                if "riccardo" in models:
                    self.riccardo_status.setStyleSheet("color: #27ae60;")
                    self.riccardo_status.setToolTip("Installato")
                    self.install_riccardo_btn.setText("✓ OK")
                    self.install_riccardo_btn.setEnabled(False)
                else:
                    self.riccardo_status.setStyleSheet("color: #e74c3c;")
                    self.riccardo_status.setToolTip("Non installato - Clicca Scarica")
                    self.install_riccardo_btn.setText("Scarica")
                    self.install_riccardo_btn.setEnabled(True)
            else:
                self._set_service_offline()
        except Exception:
            self._set_service_offline()

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


class ArchivioWidget(QWidget):
    """Widget Archivio - Gestione file locali per Open WebUI"""
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
        layout.setContentsMargins(10, 10, 10, 10)

        # === ESPLORA FILE ===
        browser_group = QGroupBox("Esplora File")
        browser_layout = QVBoxLayout(browser_group)
        browser_layout.setContentsMargins(10, 12, 10, 10)
        browser_layout.setSpacing(8)

        # Toolbar navigazione con percorso e preferiti
        nav_row = QHBoxLayout()
        nav_row.setSpacing(5)

        self.back_btn = QPushButton("◀")
        self.back_btn.setMaximumWidth(32)
        self.back_btn.setMinimumHeight(28)
        self.back_btn.setToolTip("Indietro")
        self.back_btn.clicked.connect(self.go_back)
        nav_row.addWidget(self.back_btn)

        self.up_btn = QPushButton("▲")
        self.up_btn.setMaximumWidth(32)
        self.up_btn.setMinimumHeight(28)
        self.up_btn.setToolTip("Cartella superiore")
        self.up_btn.clicked.connect(self.go_up)
        nav_row.addWidget(self.up_btn)

        self.home_btn = QPushButton("⌂")
        self.home_btn.setMaximumWidth(32)
        self.home_btn.setMinimumHeight(28)
        self.home_btn.setToolTip("Vai alla cartella preferita")
        self.home_btn.clicked.connect(self.go_home)
        nav_row.addWidget(self.home_btn)

        self.refresh_btn = QPushButton("↻")
        self.refresh_btn.setMaximumWidth(32)
        self.refresh_btn.setMinimumHeight(28)
        self.refresh_btn.setToolTip("Aggiorna")
        self.refresh_btn.clicked.connect(self.refresh_view)
        nav_row.addWidget(self.refresh_btn)

        # Percorso corrente
        self.path_label = QLineEdit()
        self.path_label.setReadOnly(True)
        self.path_label.setPlaceholderText("Nessuna cartella selezionata")
        self.path_label.setStyleSheet("""
            QLineEdit {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 3px;
                padding: 4px 8px;
                font-family: Monospace;
                font-size: 10px;
            }
        """)
        nav_row.addWidget(self.path_label, 1)

        # Pulsante preferiti (imposta cartella home)
        self.star_btn = QPushButton("⭐")
        self.star_btn.setMaximumWidth(32)
        self.star_btn.setMinimumHeight(28)
        self.star_btn.setToolTip("Imposta come cartella preferita")
        self.star_btn.clicked.connect(self.set_as_favorite)
        nav_row.addWidget(self.star_btn)

        # Pulsante sfoglia
        self.select_folder_btn = QPushButton("📁")
        self.select_folder_btn.setMaximumWidth(32)
        self.select_folder_btn.setMinimumHeight(28)
        self.select_folder_btn.setToolTip("Sfoglia cartelle")
        self.select_folder_btn.clicked.connect(self.select_private_folder)
        nav_row.addWidget(self.select_folder_btn)

        browser_layout.addLayout(nav_row)

        # Layout a due colonne: TreeView | Azioni + Risultato
        columns_layout = QHBoxLayout()
        columns_layout.setSpacing(10)

        # === COLONNA SINISTRA: File Manager ===
        self.file_model = QFileSystemModel()
        self.file_model.setRootPath("")
        self.file_model.setFilter(QDir.AllEntries | QDir.NoDotAndDotDot)

        self.tree_view = QTreeView()
        self.tree_view.setModel(self.file_model)
        self.tree_view.setAlternatingRowColors(True)
        self.tree_view.setSortingEnabled(True)
        self.tree_view.setSelectionMode(QAbstractItemView.SingleSelection)

        # Configura colonne
        self.tree_view.setColumnWidth(0, 200)
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

        columns_layout.addWidget(self.tree_view, 1)

        # === COLONNA DESTRA: Info + Pulsanti + Risultato ===
        right_column = QVBoxLayout()
        right_column.setSpacing(8)

        # Info file selezionato
        self.file_info_label = QLabel("Seleziona un file")
        self.file_info_label.setStyleSheet("""
            QLabel {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 3px;
                padding: 8px;
                font-size: 11px;
            }
        """)
        self.file_info_label.setMinimumHeight(40)
        right_column.addWidget(self.file_info_label)

        # Pulsanti azione in griglia 2x2
        btn_grid = QGridLayout()
        btn_grid.setSpacing(5)

        self.export_base64_btn = QPushButton("📄 Base64")
        self.export_base64_btn.setMinimumHeight(32)
        self.export_base64_btn.setStyleSheet("font-size: 11px; padding: 6px;")
        self.export_base64_btn.clicked.connect(self.export_to_base64)
        self.export_base64_btn.setEnabled(False)
        btn_grid.addWidget(self.export_base64_btn, 0, 0)

        self.open_file_btn = QPushButton("📂 Apri")
        self.open_file_btn.setMinimumHeight(32)
        self.open_file_btn.setStyleSheet("font-size: 11px; padding: 6px;")
        self.open_file_btn.clicked.connect(self.open_selected_file)
        self.open_file_btn.setEnabled(False)
        btn_grid.addWidget(self.open_file_btn, 0, 1)

        self.copy_path_btn = QPushButton("📋 Percorso")
        self.copy_path_btn.setMinimumHeight(32)
        self.copy_path_btn.setStyleSheet("font-size: 11px; padding: 6px;")
        self.copy_path_btn.clicked.connect(self.copy_file_path)
        self.copy_path_btn.setEnabled(False)
        btn_grid.addWidget(self.copy_path_btn, 1, 0)

        self.copy_result_btn = QPushButton("📋 Copia Risultato")
        self.copy_result_btn.setMinimumHeight(32)
        self.copy_result_btn.setStyleSheet("font-size: 11px; padding: 6px; background-color: #9b59b6; color: white;")
        self.copy_result_btn.clicked.connect(self.copy_result)
        self.copy_result_btn.setEnabled(False)
        btn_grid.addWidget(self.copy_result_btn, 1, 1)

        right_column.addLayout(btn_grid)

        # Risultato esportazione
        result_label = QLabel("Risultato esportazione:")
        result_label.setStyleSheet("font-size: 10px; font-weight: bold; color: #555;")
        right_column.addWidget(result_label)

        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setPlaceholderText("Seleziona un file e clicca Base64...")
        self.result_text.setFont(QFont("Monospace", 9))
        self.result_text.setStyleSheet("border: 1px solid #ddd; border-radius: 3px;")
        right_column.addWidget(self.result_text, 1)

        columns_layout.addLayout(right_column, 1)

        browser_layout.addLayout(columns_layout, 1)

        layout.addWidget(browser_group, 1)  # Stretch per occupare spazio

        # === COME FUNZIONA (layout a due colonne) ===
        config_group = QGroupBox("💡 Come Funziona?")
        config_layout = QHBoxLayout(config_group)
        config_layout.setContentsMargins(10, 15, 10, 10)
        config_layout.setSpacing(15)

        # === COLONNA SINISTRA: Spiegazione ===
        left_col = QVBoxLayout()
        left_col.setSpacing(8)

        intro_box = QLabel(
            "<div style='background-color: #e8f6e8; padding: 12px; border-radius: 6px;'>"
            "<b style='font-size: 12px;'>🎯 A cosa serve?</b><br><br>"
            "Open WebUI ha dei <b>bug</b> quando importi file dal browser.<br><br>"
            "Questa funzione crea un <b>\"cloud privato\"</b> sul tuo PC:<br><br>"
            "✅ I tuoi file <b>restano sul computer</b><br>"
            "✅ Niente upload su internet<br>"
            "✅ Open WebUI li vede senza errori<br>"
            "✅ Bypassa i problemi di importazione</div>"
        )
        intro_box.setWordWrap(True)
        intro_box.setStyleSheet("font-size: 11px;")
        left_col.addWidget(intro_box)

        # Nota chat in basso a sinistra
        note_box = QLabel(
            "<div style='background-color: #e3f2fd; padding: 10px; border-radius: 6px;'>"
            "<b>💬 Per usare i file in chat:</b><br>"
            "<code style='background: #fff; padding: 2px 5px;'>@nome_knowledge descrivi questo</code></div>"
        )
        note_box.setWordWrap(True)
        note_box.setStyleSheet("font-size: 10px;")
        left_col.addWidget(note_box)

        left_col.addStretch()
        config_layout.addLayout(left_col, 1)

        # === COLONNA DESTRA: 3 Passaggi ===
        right_col = QVBoxLayout()
        right_col.setSpacing(10)

        steps_label = QLabel("<b style='font-size: 13px;'>📋 3 Passi Semplicissimi</b>")
        steps_label.setStyleSheet("color: #2c3e50;")
        right_col.addWidget(steps_label)

        step1 = QLabel(
            "<div style='background: #fff; padding: 8px; border-left: 3px solid #27ae60; margin: 2px 0;'>"
            "<b style='color: #27ae60;'>1.</b> <b>Scegli la cartella</b><br>"
            "Naviga e clicca ⭐ sulla cartella desiderata</div>"
        )
        step1.setWordWrap(True)
        step1.setStyleSheet("font-size: 11px;")
        right_col.addWidget(step1)

        step2 = QLabel(
            "<div style='background: #fff; padding: 8px; border-left: 3px solid #f39c12; margin: 2px 0;'>"
            "<b style='color: #f39c12;'>2.</b> <b>Copia nel docker-compose.yml</b></div>"
        )
        step2.setWordWrap(True)
        step2.setStyleSheet("font-size: 11px;")
        right_col.addWidget(step2)

        # Volume path con pulsante copia
        volume_row = QHBoxLayout()
        volume_row.setSpacing(5)

        self.volume_field = QLineEdit("- /percorso/cartella:/app/backend/data/uploads")
        self.volume_field.setReadOnly(True)
        self.volume_field.setStyleSheet("font-family: Monospace; font-size: 9px; padding: 6px; background: #fff3cd; border: 1px solid #ffc107;")
        volume_row.addWidget(self.volume_field, 1)

        copy_volume_btn = QPushButton("📋")
        copy_volume_btn.setMaximumWidth(35)
        copy_volume_btn.setToolTip("Copia configurazione")
        copy_volume_btn.clicked.connect(self.copy_volume_config)
        volume_row.addWidget(copy_volume_btn)

        right_col.addLayout(volume_row)

        step3 = QLabel(
            "<div style='background: #fff; padding: 8px; border-left: 3px solid #3498db; margin: 2px 0;'>"
            "<b style='color: #3498db;'>3.</b> <b>Riavvia Docker</b><br>"
            "Fatto! I file ⭐ saranno visibili in Open WebUI</div>"
        )
        step3.setWordWrap(True)
        step3.setStyleSheet("font-size: 11px;")
        right_col.addWidget(step3)

        right_col.addStretch()
        config_layout.addLayout(right_col, 1)

        layout.addWidget(config_group)

    def set_as_favorite(self):
        """Imposta la cartella corrente come preferita"""
        if self.current_path:
            self.settings.setValue("private_folder", self.current_path)
            self.star_btn.setStyleSheet("background-color: #f1c40f;")
            if self.main_window:
                self.main_window.statusBar().showMessage(f"⭐ Cartella preferita: {self.current_path}", 3000)
        else:
            if self.main_window:
                self.main_window.statusBar().showMessage("Seleziona prima una cartella", 3000)

    def copy_volume_config(self):
        """Copia la configurazione del volume Docker con il percorso attuale"""
        if self.current_path:
            volume_config = f"- {self.current_path}:/app/backend/data/uploads"
            QApplication.clipboard().setText(volume_config)
            self.volume_field.setText(volume_config)
            if self.main_window:
                self.main_window.statusBar().showMessage("Configurazione volume copiata!", 3000)
        else:
            if self.main_window:
                self.main_window.statusBar().showMessage("Seleziona prima una cartella", 3000)

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

        # Aggiorna il campo volume Docker
        if hasattr(self, 'volume_field'):
            self.volume_field.setText(f"- {folder_path}:/app/backend/data/uploads")

        # Evidenzia stellina se è la cartella preferita
        favorite = self.settings.value("private_folder", "")
        if hasattr(self, 'star_btn'):
            if folder_path == favorite:
                self.star_btn.setStyleSheet("background-color: #f1c40f;")
            else:
                self.star_btn.setStyleSheet("")

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
            "<div style='text-align: center;'>"
            "<p style='font-size: 14px; color: #2c3e50;'>"
            "Grazie per aver scelto <b>Open WebUI Manager</b>.</p>"
            "<p style='font-size: 12px; color: #555; margin-top: 10px;'>"
            "Questo progetto nasce con l'obiettivo di rendere l'intelligenza artificiale "
            "accessibile a tutti, garantendo <b>privacy</b> e <b>semplicità d'uso</b>.<br><br>"
            "Tutti i dati rimangono sul tuo dispositivo. Nessuna informazione viene condivisa con terzi.</p>"
            "<hr style='border: 1px solid #eee; margin: 15px 0;'>"
            "<p style='font-size: 11px; color: #777;'>"
            "<b>Sviluppato da:</b> Paolo Lo Bello<br>"
            "<b>Licenza:</b> Open Source<br>"
            "<b>Versione:</b> 1.1.0</p>"
            "<hr style='border: 1px solid #eee; margin: 15px 0;'>"
            "<p style='font-size: 11px;'>"
            "<a href='https://github.com/wildlux/OWUIM' style='color: #333;'>🐙 GitHub</a> · "
            "<a href='https://wildlux.pythonanywhere.com/' style='color: #27ae60;'>🌐 Sito Test Django</a> · "
            "<a href='https://paololobello.altervista.org/' style='color: #e74c3c;'>📝 Blog</a> · "
            "<a href='https://www.linkedin.com/in/paololobello/' style='color: #0077b5;'>💼 LinkedIn</a>"
            "</p>"
            "</div>"
        )
        thanks_info.setWordWrap(True)
        thanks_info.setAlignment(Qt.AlignCenter)
        thanks_info.setOpenExternalLinks(True)
        thanks_layout.addWidget(thanks_info)
        layout.addWidget(thanks_group)

        layout.addStretch()


class MCPWidget(QWidget):
    """Widget per gestire il servizio MCP Bridge."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        self.mcp_service_url = "http://localhost:5558"
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

        # Ottieni IP locale (usato in più posti)
        try:
            import socket
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            self.local_ip = s.getsockname()[0]
            s.close()
        except:
            self.local_ip = "localhost"

        # ╔════════════════════════════════════════════════════════════╗
        # ║  RIGA 1: Warning (sinistra) | Risorse Sistema (destra)    ║
        # ╚════════════════════════════════════════════════════════════╝
        row1 = QHBoxLayout()
        row1.setSpacing(10)

        # === WARNING BOX (sinistra) ===
        warning_group = QGroupBox("⚠️ Avviso Importante")
        warning_group.setStyleSheet("""
            QGroupBox {
                background-color: #fff3cd;
                border: 2px solid #ffc107;
                border-radius: 8px;
            }
            QGroupBox::title {
                color: #856404;
            }
        """)
        warning_layout = QVBoxLayout(warning_group)
        warning_layout.setContentsMargins(10, 12, 10, 10)

        warning_label = QLabel(
            "<b style='color: #856404;'>Il servizio MCP richiede risorse di sistema.</b><br>"
            "<span style='color: #856404; font-size: 10px;'>"
            "Se il PC non ha abbastanza RAM o VRAM, il sistema potrebbe "
            "rallentare o bloccarsi. Verifica le risorse prima di avviare.</span>"
        )
        warning_label.setWordWrap(True)
        warning_layout.addWidget(warning_label)
        row1.addWidget(warning_group, 1)

        # === RISORSE SISTEMA (destra) ===
        resources_group = QGroupBox("📊 Risorse Sistema")
        resources_layout = QVBoxLayout(resources_group)
        resources_layout.setSpacing(4)
        resources_layout.setContentsMargins(10, 12, 10, 10)

        # RAM
        ram_row = QHBoxLayout()
        ram_row.addWidget(QLabel("<b>RAM:</b>"))
        self.ram_label = QLabel("--")
        self.ram_label.setStyleSheet("font-family: monospace; font-size: 10px;")
        ram_row.addWidget(self.ram_label)
        ram_row.addStretch()
        self.ram_status = QLabel("●")
        self.ram_status.setFont(QFont("Arial", 12))
        ram_row.addWidget(self.ram_status)
        resources_layout.addLayout(ram_row)

        # VRAM
        vram_row = QHBoxLayout()
        vram_row.addWidget(QLabel("<b>VRAM:</b>"))
        self.vram_label = QLabel("--")
        self.vram_label.setStyleSheet("font-family: monospace; font-size: 10px;")
        vram_row.addWidget(self.vram_label)
        vram_row.addStretch()
        self.vram_status = QLabel("●")
        self.vram_status.setFont(QFont("Arial", 12))
        vram_row.addWidget(self.vram_status)
        resources_layout.addLayout(vram_row)

        # Pulsante aggiorna
        refresh_res_btn = ModernButton("🔄 Rileva", "gray")
        refresh_res_btn.clicked.connect(self.detect_system_resources)
        resources_layout.addWidget(refresh_res_btn)

        row1.addWidget(resources_group, 1)
        layout.addLayout(row1)

        # ╔════════════════════════════════════════════════════════════╗
        # ║  RIGA 2: Stato Servizio (intera larghezza)                ║
        # ╚════════════════════════════════════════════════════════════╝
        status_group = QGroupBox("🔌 MCP Bridge Service (porta 5558)")
        status_main_layout = QHBoxLayout(status_group)
        status_main_layout.setSpacing(10)
        status_main_layout.setContentsMargins(10, 12, 10, 10)

        # Indicatore stato
        self.status_indicator = QLabel("●")
        self.status_indicator.setFont(QFont("Arial", 16))
        self.status_indicator.setStyleSheet("color: #bdc3c7;")
        status_main_layout.addWidget(self.status_indicator)

        self.status_label = QLabel("Non avviato")
        self.status_label.setFont(QFont("Arial", 10))
        status_main_layout.addWidget(self.status_label)

        status_main_layout.addStretch()

        # Pulsanti
        self.start_service_btn = ModernButton("🚀 Avvia", "green")
        self.start_service_btn.clicked.connect(self.confirm_and_start_mcp_service)
        status_main_layout.addWidget(self.start_service_btn)

        self.stop_service_btn = ModernButton("⏹️ Ferma", "red")
        self.stop_service_btn.clicked.connect(self.stop_mcp_service)
        self.stop_service_btn.setEnabled(False)
        status_main_layout.addWidget(self.stop_service_btn)

        self.refresh_btn = ModernButton("🔄", "gray")
        self.refresh_btn.setFixedWidth(40)
        self.refresh_btn.clicked.connect(self.check_service_status)
        status_main_layout.addWidget(self.refresh_btn)

        layout.addWidget(status_group)

        # ╔════════════════════════════════════════════════════════════╗
        # ║  RIGA 3: Servizi (sx) | Tools + LAN (dx)                  ║
        # ╚════════════════════════════════════════════════════════════╝
        row3 = QHBoxLayout()
        row3.setSpacing(10)

        # === SERVIZI COLLEGATI (sinistra) ===
        services_group = QGroupBox("Servizi Collegati")
        services_layout = QVBoxLayout(services_group)
        services_layout.setSpacing(6)
        services_layout.setContentsMargins(10, 12, 10, 10)

        # TTS Service
        tts_row = QHBoxLayout()
        self.tts_status = QLabel("●")
        self.tts_status.setFixedWidth(14)
        self.tts_status.setStyleSheet("color: #bdc3c7;")
        tts_row.addWidget(self.tts_status)
        tts_row.addWidget(QLabel("🔊 <b>TTS</b> :5556"))
        tts_row.addStretch()
        services_layout.addLayout(tts_row)

        # Image Service
        img_row = QHBoxLayout()
        self.img_status = QLabel("●")
        self.img_status.setFixedWidth(14)
        self.img_status.setStyleSheet("color: #bdc3c7;")
        img_row.addWidget(self.img_status)
        img_row.addWidget(QLabel("🖼️ <b>Image</b> :5555"))
        img_row.addStretch()
        services_layout.addLayout(img_row)

        # Document Service
        doc_row = QHBoxLayout()
        self.doc_status = QLabel("●")
        self.doc_status.setFixedWidth(14)
        self.doc_status.setStyleSheet("color: #bdc3c7;")
        doc_row.addWidget(self.doc_status)
        doc_row.addWidget(QLabel("📄 <b>Document</b> :5557"))
        doc_row.addStretch()
        services_layout.addLayout(doc_row)

        services_layout.addStretch()
        row3.addWidget(services_group, 1)

        # === COLONNA DESTRA: Tools + LAN ===
        right_col = QVBoxLayout()
        right_col.setSpacing(10)

        # Tools MCP
        tools_group = QGroupBox("Tools MCP Disponibili")
        tools_layout = QVBoxLayout(tools_group)
        tools_layout.setSpacing(4)
        tools_layout.setContentsMargins(10, 12, 10, 10)

        self.tools_list = QTextEdit()
        self.tools_list.setReadOnly(True)
        self.tools_list.setMaximumHeight(80)
        self.tools_list.setStyleSheet("font-size: 9px; font-family: monospace;")
        self.tools_list.setPlainText("Avvia il servizio per vedere i tools...")
        tools_layout.addWidget(self.tools_list)
        right_col.addWidget(tools_group)

        # Accesso LAN
        lan_group = QGroupBox("🌐 Accesso LAN")
        lan_layout = QVBoxLayout(lan_group)
        lan_layout.setSpacing(4)
        lan_layout.setContentsMargins(10, 12, 10, 10)

        lan_info = QLabel(
            f"<b>Locale:</b> <code>http://localhost:5558</code><br>"
            f"<b>LAN:</b> <code>http://{self.local_ip}:5558</code>"
        )
        lan_info.setStyleSheet("font-size: 10px;")
        lan_info.setTextInteractionFlags(Qt.TextSelectableByMouse)
        lan_layout.addWidget(lan_info)

        lan_buttons = QHBoxLayout()
        copy_btn = ModernButton("📋 Copia URL", "blue")
        copy_btn.clicked.connect(lambda: self._copy_to_clipboard(f"http://{self.local_ip}:5558"))
        lan_buttons.addWidget(copy_btn)

        docs_btn = ModernButton("📚 Docs", "purple")
        docs_btn.clicked.connect(lambda: webbrowser.open(f"{self.mcp_service_url}/docs"))
        lan_buttons.addWidget(docs_btn)
        lan_layout.addLayout(lan_buttons)

        right_col.addWidget(lan_group)
        row3.addLayout(right_col, 2)

        layout.addLayout(row3)

        # ╔════════════════════════════════════════════════════════════╗
        # ║  RIGA 4: Test Rapidi                                      ║
        # ╚════════════════════════════════════════════════════════════╝
        test_group = QGroupBox("🧪 Test Rapidi")
        test_main_layout = QVBoxLayout(test_group)
        test_main_layout.setSpacing(8)
        test_main_layout.setContentsMargins(10, 12, 10, 10)

        # Riga input testo
        text_row = QHBoxLayout()
        text_row.addWidget(QLabel("Testo:"))
        self.test_text_input = QLineEdit("Ciao, questo è un test!")
        self.test_text_input.setPlaceholderText("Inserisci testo per il test TTS...")
        text_row.addWidget(self.test_text_input, 1)
        test_main_layout.addLayout(text_row)

        # Riga pulsanti test
        test_buttons = QHBoxLayout()
        test_buttons.setSpacing(8)

        test_tts_btn = ModernButton("🔊 Test TTS", "green")
        test_tts_btn.clicked.connect(self.run_test_tts)
        test_buttons.addWidget(test_tts_btn)

        test_services_btn = ModernButton("🔍 Check Servizi", "blue")
        test_services_btn.clicked.connect(self.run_test_services)
        test_buttons.addWidget(test_services_btn)

        open_docs_btn = ModernButton("📚 Apri Swagger", "purple")
        open_docs_btn.clicked.connect(lambda: webbrowser.open(f"{self.mcp_service_url}/docs"))
        test_buttons.addWidget(open_docs_btn)

        test_buttons.addStretch()
        test_main_layout.addLayout(test_buttons)

        # Area risultato test
        self.test_result = QTextEdit()
        self.test_result.setReadOnly(True)
        self.test_result.setMaximumHeight(60)
        self.test_result.setStyleSheet("font-size: 10px; font-family: monospace; background-color: #f8f9fa;")
        self.test_result.setPlaceholderText("I risultati dei test appariranno qui...")
        test_main_layout.addWidget(self.test_result)

        layout.addWidget(test_group)

        layout.addStretch()

        scroll.setWidget(content)
        main_layout.addWidget(scroll)

        # Rileva risorse all'avvio
        QTimer.singleShot(500, self.detect_system_resources)

    def detect_system_resources(self):
        """Rileva RAM e VRAM disponibili."""
        # Rileva RAM
        try:
            if IS_WINDOWS:
                import ctypes
                kernel32 = ctypes.windll.kernel32
                c_ulonglong = ctypes.c_ulonglong
                class MEMORYSTATUSEX(ctypes.Structure):
                    _fields_ = [
                        ('dwLength', ctypes.c_ulong),
                        ('dwMemoryLoad', ctypes.c_ulong),
                        ('ullTotalPhys', c_ulonglong),
                        ('ullAvailPhys', c_ulonglong),
                        ('ullTotalPageFile', c_ulonglong),
                        ('ullAvailPageFile', c_ulonglong),
                        ('ullTotalVirtual', c_ulonglong),
                        ('ullAvailVirtual', c_ulonglong),
                        ('ullAvailExtendedVirtual', c_ulonglong),
                    ]
                stat = MEMORYSTATUSEX()
                stat.dwLength = ctypes.sizeof(stat)
                kernel32.GlobalMemoryStatusEx(ctypes.byref(stat))
                total_ram = stat.ullTotalPhys / (1024**3)
                avail_ram = stat.ullAvailPhys / (1024**3)
            else:
                with open('/proc/meminfo', 'r') as f:
                    meminfo = f.read()
                total_match = [line for line in meminfo.split('\n') if 'MemTotal' in line]
                avail_match = [line for line in meminfo.split('\n') if 'MemAvailable' in line]
                total_ram = int(total_match[0].split()[1]) / (1024**2) if total_match else 0
                avail_ram = int(avail_match[0].split()[1]) / (1024**2) if avail_match else 0

            self.ram_label.setText(f"{avail_ram:.1f} GB liberi / {total_ram:.1f} GB totali")
            self.total_ram = total_ram
            self.avail_ram = avail_ram

            # Stato RAM
            if avail_ram >= 8:
                self.ram_status.setStyleSheet("color: #27ae60;")  # Verde
                self.ram_risk = "basso"
            elif avail_ram >= 4:
                self.ram_status.setStyleSheet("color: #f39c12;")  # Arancione
                self.ram_risk = "medio"
            else:
                self.ram_status.setStyleSheet("color: #e74c3c;")  # Rosso
                self.ram_risk = "alto"

        except Exception as e:
            self.ram_label.setText(f"Errore: {e}")
            self.ram_status.setStyleSheet("color: #bdc3c7;")
            self.total_ram = 0
            self.avail_ram = 0
            self.ram_risk = "sconosciuto"

        # Rileva VRAM (GPU NVIDIA)
        try:
            result = subprocess.run(
                ['nvidia-smi', '--query-gpu=memory.total,memory.free,name', '--format=csv,noheader,nounits'],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if lines and lines[0]:
                    parts = lines[0].split(', ')
                    total_vram = int(parts[0]) / 1024  # MB to GB
                    free_vram = int(parts[1]) / 1024
                    gpu_name = parts[2] if len(parts) > 2 else "GPU"
                    self.vram_label.setText(f"{free_vram:.1f} GB liberi / {total_vram:.1f} GB ({gpu_name})")
                    self.total_vram = total_vram
                    self.free_vram = free_vram

                    # Stato VRAM
                    if free_vram >= 6:
                        self.vram_status.setStyleSheet("color: #27ae60;")
                        self.vram_risk = "basso"
                    elif free_vram >= 3:
                        self.vram_status.setStyleSheet("color: #f39c12;")
                        self.vram_risk = "medio"
                    else:
                        self.vram_status.setStyleSheet("color: #e74c3c;")
                        self.vram_risk = "alto"
                else:
                    raise Exception("Nessuna GPU rilevata")
            else:
                raise Exception("nvidia-smi non disponibile")
        except Exception:
            self.vram_label.setText("Non rilevata (no GPU NVIDIA o driver)")
            self.vram_status.setStyleSheet("color: #bdc3c7;")
            self.total_vram = 0
            self.free_vram = 0
            self.vram_risk = "N/A"

    def get_risk_assessment(self):
        """Calcola la valutazione del rischio complessivo."""
        risks = []
        risk_level = "BASSO"
        color = "#27ae60"

        # Verifica RAM
        if hasattr(self, 'avail_ram'):
            if self.avail_ram < 2:
                risks.append("❌ RAM disponibile CRITICA (<2 GB) - ALTO RISCHIO DI FREEZE")
                risk_level = "CRITICO"
                color = "#c0392b"
            elif self.avail_ram < 4:
                risks.append("⚠️ RAM disponibile bassa (<4 GB) - Possibili rallentamenti")
                if risk_level != "CRITICO":
                    risk_level = "ALTO"
                    color = "#e74c3c"
            elif self.avail_ram < 8:
                risks.append("⚡ RAM disponibile moderata (<8 GB) - Monitorare le prestazioni")
                if risk_level not in ["CRITICO", "ALTO"]:
                    risk_level = "MEDIO"
                    color = "#f39c12"
            else:
                risks.append("✅ RAM sufficiente (≥8 GB)")

        # Verifica VRAM (solo se si usa Image Analysis)
        if hasattr(self, 'free_vram') and self.free_vram > 0:
            if self.free_vram < 2:
                risks.append("❌ VRAM bassa (<2 GB) - Image Analysis potrebbe causare freeze")
                if risk_level not in ["CRITICO"]:
                    risk_level = "ALTO"
                    color = "#e74c3c"
            elif self.free_vram < 4:
                risks.append("⚠️ VRAM moderata (<4 GB) - LLaVA potrebbe essere lento")
                if risk_level not in ["CRITICO", "ALTO"]:
                    risk_level = "MEDIO"
                    color = "#f39c12"
            else:
                risks.append("✅ VRAM sufficiente per Image Analysis")
        else:
            risks.append("ℹ️ Nessuna GPU NVIDIA - Image Analysis userà CPU (più lento)")

        return risk_level, color, risks

    def confirm_and_start_mcp_service(self):
        """Mostra dialog di conferma con valutazione rischi prima di avviare."""
        # Aggiorna le risorse
        self.detect_system_resources()

        # Calcola rischi
        risk_level, color, risks = self.get_risk_assessment()

        # Costruisci messaggio
        risk_text = "\n".join(risks)

        msg = QMessageBox(self)
        msg.setWindowTitle("⚠️ Conferma Avvio MCP Service")
        msg.setIcon(QMessageBox.Warning if risk_level in ["ALTO", "CRITICO"] else QMessageBox.Information)

        detail_text = f"""
<h3 style='color: {color};'>Livello di Rischio: {risk_level}</h3>

<p><b>Valutazione Sistema:</b></p>
<pre style='font-size: 11px;'>{risk_text}</pre>

<hr>

<p><b>Cosa succede avviando il servizio:</b></p>
<ul>
<li>Il servizio MCP Bridge userà ~200-500 MB di RAM</li>
<li>Se Image Analysis è attivo, LLaVA userà 2-8 GB di VRAM</li>
<li>Se la RAM/VRAM è insufficiente, il PC potrebbe rallentare o bloccarsi</li>
</ul>

<p><b>Raccomandazioni:</b></p>
<ul>
{"<li style='color: #c0392b;'><b>SCONSIGLIATO</b> - Chiudi altre applicazioni prima di procedere</li>" if risk_level == "CRITICO" else ""}
{"<li style='color: #e74c3c;'>Chiudi browser e altre app pesanti prima di procedere</li>" if risk_level == "ALTO" else ""}
{"<li>Monitora l'uso della memoria durante l'utilizzo</li>" if risk_level == "MEDIO" else ""}
{"<li style='color: #27ae60;'>Il sistema sembra avere risorse sufficienti</li>" if risk_level == "BASSO" else ""}
</ul>
"""

        msg.setTextFormat(Qt.RichText)
        msg.setText(f"<b>Vuoi avviare il servizio MCP Bridge?</b>")
        msg.setInformativeText(f"Livello di rischio: <b style='color: {color};'>{risk_level}</b>")
        msg.setDetailedText(f"Risorse rilevate:\n- RAM libera: {getattr(self, 'avail_ram', 0):.1f} GB\n- VRAM libera: {getattr(self, 'free_vram', 0):.1f} GB\n\n{risk_text}")

        # Pulsanti
        if risk_level == "CRITICO":
            msg.setStandardButtons(QMessageBox.Cancel)
            force_btn = msg.addButton("⚠️ Avvia comunque (RISCHIOSO)", QMessageBox.AcceptRole)
        else:
            msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            msg.setDefaultButton(QMessageBox.No if risk_level in ["ALTO", "CRITICO"] else QMessageBox.Yes)

        result = msg.exec_()

        # Verifica risposta
        if risk_level == "CRITICO":
            if msg.clickedButton() and "Avvia" in msg.clickedButton().text():
                self._do_start_mcp_service()
        else:
            if result == QMessageBox.Yes:
                self._do_start_mcp_service()

    def _do_start_mcp_service(self):
        """Avvia effettivamente il servizio MCP."""
        try:
            # Usa il venv per avere MCP SDK disponibile
            mcp_script = SCRIPT_DIR / "mcp_service" / "mcp_service.py"
            if IS_WINDOWS:
                python_exe = SCRIPT_DIR / "venv" / "Scripts" / "python.exe"
                if python_exe.exists():
                    subprocess.Popen(
                        ["cmd", "/c", "start", "MCP Bridge", str(python_exe), str(mcp_script)],
                        cwd=str(SCRIPT_DIR),
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL
                    )
                else:
                    # Fallback allo script batch
                    script = SCRIPT_DIR / "mcp_service" / "start_mcp_service.bat"
                    subprocess.Popen(
                        ["cmd", "/c", "start", "", str(script)],
                        cwd=str(SCRIPT_DIR),
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL
                    )
            else:
                python_exe = SCRIPT_DIR / "venv" / "bin" / "python"
                if python_exe.exists():
                    subprocess.Popen(
                        ["gnome-terminal", "--title=MCP Bridge", "--", str(python_exe), str(mcp_script)],
                        cwd=str(SCRIPT_DIR),
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL
                    )
                else:
                    # Fallback allo script shell
                    script = SCRIPT_DIR / "mcp_service" / "start_mcp_service.sh"
                    subprocess.Popen(
                        ["gnome-terminal", "--", "bash", str(script)],
                        cwd=str(SCRIPT_DIR),
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL
                    )
            self.status_label.setText("Avvio in corso...")
            self.status_indicator.setStyleSheet("color: #f39c12;")

            # Avvia timer per check stato (solo dopo avvio manuale)
            if not hasattr(self, 'check_timer') or not self.check_timer.isActive():
                self.check_timer = QTimer()
                self.check_timer.timeout.connect(self.check_service_status)
                self.check_timer.start(5000)

            QTimer.singleShot(3000, self.check_service_status)
        except Exception as e:
            QMessageBox.warning(self, "Errore", f"Impossibile avviare il servizio:\n{e}")

    def stop_mcp_service(self):
        """Ferma il servizio MCP."""
        try:
            # Trova e termina il processo
            if IS_WINDOWS:
                subprocess.run(["taskkill", "/f", "/im", "python.exe", "/fi", "WINDOWTITLE eq MCP*"],
                              capture_output=True)
            else:
                subprocess.run(["pkill", "-f", "mcp_service.py"], capture_output=True)

            self.status_label.setText("Servizio fermato")
            self.status_indicator.setStyleSheet("color: #bdc3c7;")
            self.stop_service_btn.setEnabled(False)
            self.start_service_btn.setEnabled(True)

            # Ferma il timer
            if hasattr(self, 'check_timer'):
                self.check_timer.stop()

        except Exception as e:
            QMessageBox.warning(self, "Errore", f"Impossibile fermare il servizio:\n{e}")

    def check_service_status(self):
        """Verifica lo stato del servizio MCP e dei servizi collegati."""
        try:
            import requests
            resp = requests.get(self.mcp_service_url, timeout=3)
            if resp.status_code == 200:
                data = resp.json()
                self.status_indicator.setStyleSheet("color: #27ae60;")
                self.status_label.setText(f"Attivo - {data.get('tools_count', 0)} tools disponibili")
                self.start_service_btn.setEnabled(False)
                self.stop_service_btn.setEnabled(True)

                # Aggiorna stato servizi
                services = data.get("services", {})
                self._update_service_status(self.tts_status, services.get("tts", {}).get("available", False))
                self._update_service_status(self.img_status, services.get("image", {}).get("available", False))
                self._update_service_status(self.doc_status, services.get("document", {}).get("available", False))

                # Aggiorna lista tools
                self._update_tools_list()
            else:
                self._set_offline()
        except:
            self._set_offline()

    def _set_offline(self):
        """Imposta stato offline."""
        self.status_indicator.setStyleSheet("color: #bdc3c7;")
        self.status_label.setText("Non attivo")
        self.start_service_btn.setEnabled(True)
        self.stop_service_btn.setEnabled(False)
        self.tts_status.setStyleSheet("color: #bdc3c7;")
        self.img_status.setStyleSheet("color: #bdc3c7;")
        self.doc_status.setStyleSheet("color: #bdc3c7;")

    def _update_service_status(self, indicator, available):
        """Aggiorna indicatore servizio."""
        if available:
            indicator.setStyleSheet("color: #27ae60;")
        else:
            indicator.setStyleSheet("color: #e74c3c;")

    def _update_tools_list(self):
        """Aggiorna lista tools."""
        try:
            import requests
            resp = requests.get(f"{self.mcp_service_url}/tools", timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                tools = data.get("tools", [])
                text = "\n".join([f"• {t['name']}: {t['description']}" for t in tools])
                self.tools_list.setPlainText(text if text else "Nessun tool disponibile")
        except:
            pass

    def _copy_to_clipboard(self, text):
        """Copia testo negli appunti."""
        from PyQt5.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        clipboard.setText(text)
        QMessageBox.information(self, "Copiato", f"Copiato negli appunti:\n{text}")

    def run_test_tts(self):
        """Esegue test TTS via MCP Bridge."""
        text = self.test_text_input.text().strip()
        if not text:
            text = "Ciao, questo è un test!"

        self.test_result.setPlainText("⏳ Test TTS in corso...")

        try:
            import requests
            resp = requests.post(
                f"{self.mcp_service_url}/test/tts",
                params={"text": text},
                timeout=30
            )
            data = resp.json()

            if data.get("success"):
                result = (
                    f"✅ TTS OK!\n"
                    f"Voce: {data.get('voice', 'N/A')}\n"
                    f"Audio: {data.get('audio_size', 0)} bytes\n"
                    f"File: {data.get('audio_path', 'N/A')}"
                )
                self.test_result.setPlainText(result)

                # Prova a riprodurre l'audio
                audio_path = data.get('audio_path')
                if audio_path and os.path.exists(audio_path):
                    if IS_WINDOWS:
                        os.startfile(audio_path)
                    else:
                        subprocess.Popen(["xdg-open", audio_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            else:
                self.test_result.setPlainText(f"❌ Errore TTS:\n{data.get('error', 'Errore sconosciuto')}")

        except requests.exceptions.ConnectionError:
            self.test_result.setPlainText("❌ Servizio MCP non raggiungibile.\nAvvia il servizio prima di testare.")
        except Exception as e:
            self.test_result.setPlainText(f"❌ Errore: {e}")

    def run_test_services(self):
        """Verifica stato di tutti i servizi."""
        self.test_result.setPlainText("⏳ Verifica servizi in corso...")

        try:
            import requests
            resp = requests.get(f"{self.mcp_service_url}/services", timeout=5)
            data = resp.json()

            lines = ["📊 Stato Servizi:\n"]
            for name, info in data.items():
                status = "✅" if info.get("available") else "❌"
                port = info.get("port", "?")
                lines.append(f"{status} {name.upper()}: porta {port}")

            self.test_result.setPlainText("\n".join(lines))

        except requests.exceptions.ConnectionError:
            self.test_result.setPlainText("❌ Servizio MCP non raggiungibile.\nAvvia il servizio prima di testare.")
        except Exception as e:
            self.test_result.setPlainText(f"❌ Errore: {e}")

    def open_readme(self):
        """Apre il README del servizio MCP."""
        readme_path = SCRIPT_DIR / "mcp_service" / "README.md"
        if readme_path.exists():
            if IS_WINDOWS:
                os.startfile(str(readme_path))
            else:
                subprocess.run(["xdg-open", str(readme_path)])
        else:
            QMessageBox.warning(self, "Errore", "README non trovato")


class MainWindow(QMainWindow):
    """Finestra principale"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Open WebUI Manager")
        self.setMinimumSize(1000, 750)
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
        self.tabs.setFont(QFont("Arial", 10))
        self.tabs.setUsesScrollButtons(True)

        # Pagine
        self.dashboard = DashboardWidget(self)
        self.logs = LogsWidget(self)
        self.models = ModelsWidget(self)
        self.config = ConfigWidget(self)
        self.archivio = ArchivioWidget(self)
        self.tts_widget = TTSWidget(self)
        self.mcp_widget = MCPWidget(self)
        self.info_widget = InfoWidget(self)

        self.tabs.addTab(self.dashboard, "🏠 Dashboard")
        self.tabs.addTab(self.logs, "📜 Log")
        self.tabs.addTab(self.models, "🤖 Modelli")
        self.tabs.addTab(self.archivio, "📁 Archivio")
        self.tabs.addTab(self.tts_widget, "🔊 Voce")
        self.tabs.addTab(self.mcp_widget, "🔌 MCP")
        self.tabs.addTab(self.config, "⚙️ Configurazione")
        self.tabs.addTab(self.info_widget, "ℹ️ Informazioni")

        layout.addWidget(self.tabs)

        # Barra inferiore con info + controlli
        bottom_bar = QHBoxLayout()
        bottom_bar.setContentsMargins(10, 5, 10, 5)
        bottom_bar.setSpacing(15)

        # === SINISTRA: Status QR-Code LAN ===
        self.qr_status_label = QLabel("QR-Code LAN: --")
        self.qr_status_label.setStyleSheet("font-size: 10px; color: #7f8c8d;")
        bottom_bar.addWidget(self.qr_status_label)

        bottom_bar.addStretch()

        # === DESTRA: Font size + Dark mode ===
        font_label = QLabel("Font:")
        font_label.setStyleSheet("font-size: 10px; color: #7f8c8d;")
        bottom_bar.addWidget(font_label)

        self.font_minus_btn = QPushButton("−")
        self.font_minus_btn.setFixedSize(24, 24)
        self.font_minus_btn.setStyleSheet("""
            QPushButton {
                font-size: 14px; font-weight: bold;
                border: 1px solid #bdc3c7; border-radius: 4px;
                background: #ecf0f1;
            }
            QPushButton:hover { background: #3498db; color: white; }
        """)
        self.font_minus_btn.clicked.connect(self.decrease_font_size)
        bottom_bar.addWidget(self.font_minus_btn)

        self.font_size_label = QLabel("100%")
        self.font_size_label.setStyleSheet("font-size: 10px; min-width: 35px; text-align: center;")
        self.font_size_label.setAlignment(Qt.AlignCenter)
        bottom_bar.addWidget(self.font_size_label)

        self.font_plus_btn = QPushButton("+")
        self.font_plus_btn.setFixedSize(24, 24)
        self.font_plus_btn.setStyleSheet("""
            QPushButton {
                font-size: 14px; font-weight: bold;
                border: 1px solid #bdc3c7; border-radius: 4px;
                background: #ecf0f1;
            }
            QPushButton:hover { background: #3498db; color: white; }
        """)
        self.font_plus_btn.clicked.connect(self.increase_font_size)
        bottom_bar.addWidget(self.font_plus_btn)

        # Separatore
        sep = QFrame()
        sep.setFrameShape(QFrame.VLine)
        sep.setStyleSheet("color: #bdc3c7;")
        bottom_bar.addWidget(sep)

        self.dark_mode_btn = QPushButton("🌙 Dark Mode")
        self.dark_mode_btn.setCheckable(True)
        self.dark_mode_btn.setStyleSheet("""
            QPushButton {
                font-size: 10px;
                padding: 5px 10px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                background: #ecf0f1;
            }
            QPushButton:checked {
                background: #2c3e50;
                color: white;
                border-color: #2c3e50;
            }
        """)
        self.dark_mode_btn.clicked.connect(self.toggle_dark_mode)
        bottom_bar.addWidget(self.dark_mode_btn)

        layout.addLayout(bottom_bar)

        # Status bar
        self.statusBar().showMessage("Pronto")
        self.is_dark_mode = False

        # Font size settings
        self.settings = QSettings("OpenWebUI", "Manager")
        self.base_font_size = 10  # Font size di base
        self.font_scale = self.settings.value("font_scale", 100, type=int)
        self.font_save_timer = QTimer()
        self.font_save_timer.setSingleShot(True)
        self.font_save_timer.timeout.connect(self.save_font_setting)
        self.apply_font_scale()

        # Timer per aggiornare status QR-Code LAN
        QTimer.singleShot(500, self.update_qr_status)

        # Timer per controllo voci TTS all'avvio
        QTimer.singleShot(2000, self.check_tts_voices_on_startup)

    def check_tts_voices_on_startup(self):
        """
        Controlla se le voci TTS sono installate all'avvio.
        Se non lo sono, mostra un avviso e porta l'utente al tab Voce.
        """
        try:
            import requests
            # Controlla se il servizio TTS è attivo
            resp = requests.get("http://localhost:5556/voices/check", timeout=3)
            if resp.status_code == 200:
                data = resp.json()
                if not data.get("ready", False):
                    # TTS non pronto - mostra avviso
                    message = data.get("message", "Voci TTS non installate")
                    voices_missing = data.get("voices_missing", [])

                    msg_box = QMessageBox(self)
                    msg_box.setIcon(QMessageBox.Warning)
                    msg_box.setWindowTitle("Sintesi Vocale Non Configurata")
                    msg_box.setText(f"<b>{message}</b>")
                    msg_box.setInformativeText(
                        "La sintesi vocale di Open WebUI non funzionerà finché non installi le voci.\n\n"
                        f"Voci mancanti: {', '.join(voices_missing) if voices_missing else 'tutte'}\n\n"
                        "Vuoi andare al tab 'Voce' per installarle ora?"
                    )
                    msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
                    msg_box.setDefaultButton(QMessageBox.Yes)

                    if msg_box.exec_() == QMessageBox.Yes:
                        # Trova l'indice del tab Voce e selezionalo
                        for i in range(self.tabs.count()):
                            if "Voce" in self.tabs.tabText(i):
                                self.tabs.setCurrentIndex(i)
                                break
        except requests.exceptions.ConnectionError:
            # Servizio TTS non attivo - non è un errore critico all'avvio
            pass
        except Exception as e:
            # Ignora altri errori silenziosamente
            print(f"[TTS Check] Errore: {e}")

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

    def toggle_dark_mode(self):
        """Attiva/disattiva dark mode"""
        self.is_dark_mode = self.dark_mode_btn.isChecked()
        if self.is_dark_mode:
            self.dark_mode_btn.setText("☀️ Light Mode")
            self.setStyleSheet("""
                QMainWindow { background-color: #1a1a2e; }
                QWidget { background-color: #1a1a2e; color: #eaeaea; }
                QGroupBox {
                    background-color: #16213e;
                    border: 1px solid #0f3460;
                    border-radius: 8px;
                    margin-top: 12px;
                    padding: 15px;
                    color: #eaeaea;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 15px;
                    padding: 0 5px;
                    color: #e94560;
                }
                QListWidget {
                    background-color: #16213e;
                    border: 1px solid #0f3460;
                    border-radius: 6px;
                    color: #eaeaea;
                }
                QLineEdit, QComboBox {
                    padding: 8px;
                    border: 1px solid #0f3460;
                    border-radius: 6px;
                    background: #16213e;
                    color: #eaeaea;
                }
                QLineEdit:focus, QComboBox:focus { border-color: #e94560; }
                QTextEdit {
                    background-color: #16213e;
                    border: 1px solid #0f3460;
                    color: #eaeaea;
                }
                QLabel { color: #eaeaea; }
                QTabWidget::pane { border: none; background: transparent; }
                QTabBar::tab {
                    background: #16213e;
                    border: none;
                    padding: 12px 20px;
                    margin-right: 2px;
                    border-top-left-radius: 6px;
                    border-top-right-radius: 6px;
                    color: #eaeaea;
                }
                QTabBar::tab:selected {
                    background: #0f3460;
                    color: #e94560;
                    font-weight: bold;
                }
                QTabBar::tab:hover:!selected { background: #1a1a2e; }
                QPushButton {
                    background-color: #16213e;
                    border: 1px solid #0f3460;
                    color: #eaeaea;
                }
                QPushButton:hover { background-color: #0f3460; }
                QTableWidget {
                    background-color: #16213e;
                    gridline-color: #0f3460;
                    color: #eaeaea;
                }
                QHeaderView::section {
                    background-color: #0f3460;
                    color: #eaeaea;
                    border: 1px solid #16213e;
                }
            """)
        else:
            self.dark_mode_btn.setText("🌙 Dark Mode")
            self.setStyleSheet("""
                QMainWindow { background-color: #f5f6fa; }
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
                QLineEdit:focus, QComboBox:focus { border-color: #3498db; }
                QTabWidget::pane { border: none; background: transparent; }
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
                QTabBar::tab:hover:!selected { background: #dfe6e9; }
            """)

    def start_status_checker(self):
        """Avvia il thread per controllare lo stato"""
        self.status_checker = StatusChecker()
        self.status_checker.status_signal.connect(self.update_status)
        self.status_checker.start()

    def update_status(self, status):
        self.dashboard.update_status(status)

        # Aggiorna status bar (senza TTS, che è nella barra inferiore)
        ollama = "✓" if status.get('ollama') else "✗"
        webui = "✓" if status.get('openwebui') else "✗"
        self.statusBar().showMessage(f"Ollama: {ollama}  |  Open WebUI: {webui}")

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

    def increase_font_size(self):
        """Aumenta la dimensione del font (max 150%)"""
        if self.font_scale < 150:
            self.font_scale += 10
            self.apply_font_scale()
            self.font_save_timer.start(10000)  # Salva dopo 10 secondi

    def decrease_font_size(self):
        """Diminuisce la dimensione del font (min 70%)"""
        if self.font_scale > 70:
            self.font_scale -= 10
            self.apply_font_scale()
            self.font_save_timer.start(10000)  # Salva dopo 10 secondi

    def apply_font_scale(self):
        """Applica la scala del font a tutta l'applicazione"""
        self.font_size_label.setText(f"{self.font_scale}%")
        scaled_size = int(self.base_font_size * self.font_scale / 100)

        # Usa stylesheet globale per forzare il font-size su tutti i widget
        app = QApplication.instance()
        current_style = app.styleSheet() or ""

        # Rimuovi eventuali font-size precedenti
        import re
        current_style = re.sub(r'\* \{ font-size: \d+px; \}', '', current_style)

        # Aggiungi nuovo font-size globale
        global_font_style = f"* {{ font-size: {scaled_size}px; }}"
        app.setStyleSheet(global_font_style + current_style)

        # Applica anche con setFont per i widget che non rispettano lo stylesheet
        font = QFont()
        font.setPointSize(scaled_size)
        app.setFont(font)

        # Forza aggiornamento visuale
        for widget in app.allWidgets():
            widget.update()

        self.update()
        self.repaint()

    def save_font_setting(self):
        """Salva la preferenza del font"""
        self.settings.setValue("font_scale", self.font_scale)
        self.statusBar().showMessage(f"Font {self.font_scale}% salvato come predefinito", 3000)

    def update_qr_status(self):
        """Aggiorna lo status QR-Code LAN nella barra inferiore"""
        qr_enabled = self.config.qr_checkbox.isChecked() if hasattr(self.config, 'qr_checkbox') else False
        qr_icon = "✓" if qr_enabled else "✗"
        self.qr_status_label.setText(f"QR-Code LAN: {qr_icon}")
        # Aggiorna ogni 5 secondi
        QTimer.singleShot(5000, self.update_qr_status)

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
