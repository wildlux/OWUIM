"""
MainWindow - Finestra principale dell'applicazione.

Principi applicati:
- SRP: Solo orchestrazione dei widget, non logica business
- Encapsulation: Widget accedono a MainWindow tramite metodi pubblici
- Programmazione difensiva: Eccezioni specifiche
"""

import os
import sys
import re
import subprocess
import time
import logging

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QPushButton, QLabel, QFrame, QMessageBox,
    QSystemTrayIcon, QMenu, QAction, QCheckBox, QShortcut
)
from PyQt5.QtCore import Qt, QTimer, QSettings
from PyQt5.QtGui import QIcon, QFont, QFontDatabase, QPixmap, QColor, QKeySequence

from config import (
    IS_WINDOWS, IS_MAC, SCRIPT_DIR, DOCKER_COMPOSE,
    URL_WEBUI, APP_NAME, APP_VERSION, ensure_env_file,
)

# Import condizionali
try:
    from translations import get_text
    HAS_TRANSLATIONS = True
except ImportError:
    HAS_TRANSLATIONS = False
    def get_text(key, lang="it", **kwargs):
        return key

from ui.threads import StatusChecker, WorkerThread
from ui.widgets.dashboard import DashboardWidget
from ui.widgets.logs import LogsWidget
from ui.widgets.models import ModelsWidget
from ui.widgets.config_widget import ConfigWidget
from ui.widgets.tts import TTSWidget
from ui.widgets.archivio import ArchivioWidget
from ui.widgets.info import InfoWidget
from ui.widgets.mcp import MCPWidget

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """Finestra principale."""

    def __init__(self):
        super().__init__()
        # Genera .env con WEBUI_SECRET_KEY se mancante (serve prima di docker compose)
        ensure_env_file()
        self._load_bundled_fonts()
        self.setWindowTitle(APP_NAME)
        self.setMinimumSize(1000, 750)
        self.worker = None
        self._last_service_status = {}
        self.current_lang = "it"
        self.setup_ui()
        self.setup_tray()
        self.start_status_checker()

        QTimer.singleShot(500, self._check_first_run)

        # Stile globale
        self.setStyleSheet(self._get_light_theme())

    def _load_bundled_fonts(self):
        """Carica i font inclusi nel progetto per portabilita'."""
        fonts_dir = SCRIPT_DIR / "fonts"
        if not fonts_dir.exists():
            return
        for font_file in fonts_dir.glob("*.ttf"):
            font_id = QFontDatabase.addApplicationFont(str(font_file))
            if font_id < 0:
                logger.warning("Font non caricato: %s", font_file.name)

    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)

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

        self.tabs.addTab(self.dashboard, "\U0001f3e0 Dashboard")
        self.tabs.addTab(self.models, "\U0001f916 Modelli")
        self.tabs.addTab(self.tts_widget, "\U0001f50a Voce")
        self.tabs.addTab(self.archivio, "\U0001f4c1 Archivio")
        self.tabs.addTab(self.mcp_widget, "\U0001f50c MCP")
        self.tabs.addTab(self.config, "\u2699\ufe0f Configurazione")
        self.tabs.addTab(self.logs, "\U0001f4dc Log")
        self.tabs.addTab(self.info_widget, "\u2139\ufe0f Informazioni")

        layout.addWidget(self.tabs)

        self._setup_tab_help()
        self._setup_shortcuts()
        self._setup_bottom_bar(layout)
        self._setup_status_bar()

        self.is_dark_mode = False

        # Font size
        self.settings = QSettings("OpenWebUI", "Manager")
        self.base_font_size = 10
        self.font_scale = self.settings.value("font_scale", 100, type=int)

        # Font family ciclabile con Ctrl+F
        self._font_families = ["Arial", "OpenDyslexic", "DejaVu Sans Mono"]
        saved_font = self.settings.value("font_family", "Arial")
        if saved_font in self._font_families:
            self._current_font_idx = self._font_families.index(saved_font)
        else:
            self._current_font_idx = 0

        # Lingua
        saved_lang = self.settings.value("language", "it")
        if saved_lang == "en":
            self.current_lang = "en"
            self.lang_btn.setText("\U0001f1ec\U0001f1e7")
            QTimer.singleShot(100, self.retranslate_ui)
        else:
            self.current_lang = "it"

        self.font_save_timer = QTimer()
        self.font_save_timer.setSingleShot(True)
        self.font_save_timer.timeout.connect(self.save_font_setting)
        self.apply_font_scale()

        QTimer.singleShot(500, self.update_qr_status)
        QTimer.singleShot(2000, self.check_tts_voices_on_startup)
        QTimer.singleShot(4000, self.check_mcp_suggestion)

    def _setup_tab_help(self):
        # Chiavi per tab help - tradotte dinamicamente in _show_tab_help
        self._tab_help_keys = {
            0: ("tab_dashboard", "tab_help_dashboard"),
            1: ("tab_models", "tab_help_models"),
            2: ("tab_voice", "tab_help_voice"),
            3: ("tab_archive", "tab_help_archive"),
            4: ("tab_mcp", "tab_help_mcp"),
            5: ("tab_config", "tab_help_config"),
            6: ("tab_logs", "tab_help_logs"),
            7: ("tab_info", "tab_help_info"),
        }
        # Help disponibile tramite F1 (shortcut globale)

    def _setup_shortcuts(self):
        for i in range(min(8, self.tabs.count())):
            shortcut = QShortcut(QKeySequence(f"Ctrl+{i+1}"), self)
            shortcut.activated.connect(lambda idx=i: self.tabs.setCurrentIndex(idx))

        QShortcut(QKeySequence("Ctrl+R"), self).activated.connect(self.dashboard.update_system_info)
        QShortcut(QKeySequence("Ctrl+B"), self).activated.connect(self.dashboard.open_browser)
        QShortcut(QKeySequence("Ctrl+Q"), self).activated.connect(self.confirm_and_quit)
        QShortcut(QKeySequence("Ctrl+D"), self).activated.connect(lambda: self.dark_mode_btn.click())
        QShortcut(QKeySequence("Ctrl+F"), self).activated.connect(self.cycle_font)
        QShortcut(QKeySequence("F5"), self).activated.connect(self.dashboard.update_system_info)
        QShortcut(QKeySequence("F1"), self).activated.connect(self.show_global_help)

    def _setup_bottom_bar(self, layout):
        bottom_bar = QHBoxLayout()
        bottom_bar.setContentsMargins(10, 5, 10, 5)
        bottom_bar.setSpacing(15)

        # Mini indicatori
        self.mini_ollama = QLabel("\u25cf Ollama")
        self.mini_ollama.setStyleSheet("font-size: 10px; color: #bdc3c7;")
        bottom_bar.addWidget(self.mini_ollama)

        self.mini_webui = QLabel("\u25cf WebUI")
        self.mini_webui.setStyleSheet("font-size: 10px; color: #bdc3c7;")
        bottom_bar.addWidget(self.mini_webui)

        self.mini_tts = QLabel("\u25cf TTS")
        self.mini_tts.setStyleSheet("font-size: 10px; color: #bdc3c7;")
        bottom_bar.addWidget(self.mini_tts)

        mini_sep = QFrame()
        mini_sep.setFrameShape(QFrame.VLine)
        mini_sep.setStyleSheet("color: #bdc3c7;")
        bottom_bar.addWidget(mini_sep)

        self.qr_status_label = QLabel("QR-Code LAN: --")
        self.qr_status_label.setStyleSheet("font-size: 10px; color: #7f8c8d;")
        bottom_bar.addWidget(self.qr_status_label)

        bottom_bar.addStretch()

        # Font size
        self._font_label = QLabel(get_text("font_label", self.current_lang))
        self._font_label.setStyleSheet("font-size: 10px; color: #7f8c8d;")
        bottom_bar.addWidget(self._font_label)

        self.font_minus_btn = QPushButton("\u2212")
        self.font_minus_btn.setFixedSize(24, 24)
        self.font_minus_btn.setStyleSheet("""
            QPushButton { font-size: 14px; font-weight: bold; border: 1px solid #bdc3c7; border-radius: 4px; background: #ecf0f1; }
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
            QPushButton { font-size: 14px; font-weight: bold; border: 1px solid #bdc3c7; border-radius: 4px; background: #ecf0f1; }
            QPushButton:hover { background: #3498db; color: white; }
        """)
        self.font_plus_btn.clicked.connect(self.increase_font_size)
        bottom_bar.addWidget(self.font_plus_btn)

        sep = QFrame()
        sep.setFrameShape(QFrame.VLine)
        sep.setStyleSheet("color: #bdc3c7;")
        bottom_bar.addWidget(sep)

        self.dark_mode_btn = QPushButton("\U0001f319 Dark Mode")
        self.dark_mode_btn.setCheckable(True)
        self.dark_mode_btn.setStyleSheet("""
            QPushButton { font-size: 10px; padding: 5px 10px; border: 1px solid #bdc3c7; border-radius: 4px; background: #ecf0f1; }
            QPushButton:checked { background: #2c3e50; color: white; border-color: #2c3e50; }
        """)
        self.dark_mode_btn.clicked.connect(self.toggle_dark_mode)
        bottom_bar.addWidget(self.dark_mode_btn)

        self.current_lang = "it"
        self.lang_btn = QPushButton("\U0001f1ee\U0001f1f9")
        self.lang_btn.setFixedSize(32, 28)
        self.lang_btn.setStyleSheet("""
            QPushButton { font-size: 16px; border: 1px solid #bdc3c7; border-radius: 4px; background: #ecf0f1; padding: 0px; }
            QPushButton:hover { background: #3498db; border-color: #3498db; }
        """)
        self.lang_btn.setToolTip("Cambia lingua / Change language")
        self.lang_btn.clicked.connect(self.toggle_language)
        bottom_bar.addWidget(self.lang_btn)

        layout.addLayout(bottom_bar)

    def _setup_status_bar(self):
        self.statusBar().showMessage(get_text("ready", self.current_lang))
        self._operation_active = False
        self._op_start_time = 0

        self.cancel_btn = QPushButton(get_text("cancel", self.current_lang))
        self.cancel_btn.setStyleSheet("""
            QPushButton { background-color: #e74c3c; color: white; border: none; border-radius: 4px; padding: 3px 12px; font-size: 11px; font-weight: bold; }
            QPushButton:hover { background-color: #c0392b; }
        """)
        self.cancel_btn.setCursor(Qt.PointingHandCursor)
        self.cancel_btn.setVisible(False)
        self.cancel_btn.clicked.connect(self.cancel_operation)
        self.statusBar().addPermanentWidget(self.cancel_btn)

        self.elapsed_timer = QTimer()
        self.elapsed_timer.setInterval(1000)
        self.elapsed_timer.timeout.connect(self._update_elapsed)
        self._current_op_message = ""

    # === Metodi TTS/MCP Startup ===

    def check_tts_voices_on_startup(self):
        try:
            import requests
            t = self.tr_text
            resp = requests.get(f"{URL_WEBUI.replace(str(URL_WEBUI.split(':')[-1]), '5556')}/voices/check", timeout=3)
            if resp.status_code != 200:
                return
            data = resp.json()
            if not data.get("ready", False):
                message = data.get("message", t("tts_not_configured"))
                voices_missing = data.get("voices_missing", [])
                missing_str = ', '.join(voices_missing) if voices_missing else 'all'
                msg_box = QMessageBox(self)
                msg_box.setIcon(QMessageBox.Warning)
                msg_box.setWindowTitle(t("tts_not_configured"))
                msg_box.setText(f"<b>{message}</b>")
                msg_box.setInformativeText(
                    t("tts_install_prompt", missing=missing_str)
                )
                msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
                msg_box.setDefaultButton(QMessageBox.Yes)
                if msg_box.exec_() == QMessageBox.Yes:
                    for i in range(self.tabs.count()):
                        tab_text = self.tabs.tabText(i)
                        if "Voce" in tab_text or "Voice" in tab_text:
                            self.tabs.setCurrentIndex(i)
                            break
        except Exception:
            pass

    def check_mcp_suggestion(self):
        try:
            t = self.tr_text
            sys.path.insert(0, str(SCRIPT_DIR / "scripts"))
            from system_profiler import get_system_profile, SystemTier
            profile = get_system_profile()
            if profile.tier not in (SystemTier.MEDIUM, SystemTier.HIGH):
                return
            try:
                import requests
                resp = requests.get(f"{URL_WEBUI.replace(str(URL_WEBUI.split(':')[-1]), '5558')}/", timeout=2)
                if resp.status_code == 200:
                    return
            except Exception:
                pass
            settings = QSettings("OpenWebUI", "Manager")
            if settings.value("mcp_suggestion_dismissed", False, type=bool):
                return
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Information)
            msg_box.setWindowTitle(t("mcp_suggestion_title"))
            gpu_text = f" e GPU {profile.gpu_name}" if profile.has_gpu and profile.gpu_name else ""
            msg_box.setText(f"{t('mcp_suggestion_text')}<br>({profile.ram_total_gb:.0f} GB RAM{gpu_text})")
            msg_box.setInformativeText(t("mcp_suggestion_info"))
            btn_enable = msg_box.addButton(t("mcp_enable"), QMessageBox.AcceptRole)
            msg_box.addButton(t("mcp_not_now"), QMessageBox.RejectRole)
            msg_box.exec_()
            if msg_box.clickedButton() == btn_enable:
                subprocess.Popen(
                    ['python3', 'mcp_service/mcp_service.py'],
                    cwd=SCRIPT_DIR, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                )
                self.statusBar().showMessage(t("mcp_bridge_started"))
                for i in range(self.tabs.count()):
                    if "MCP" in self.tabs.tabText(i):
                        self.tabs.setCurrentIndex(i)
                        break
            else:
                settings.setValue("mcp_suggestion_dismissed", True)
        except ImportError:
            pass
        except Exception as e:
            logger.debug("MCP check: %s", e)

    # === Tray ===

    def setup_tray(self):
        self.tray = QSystemTrayIcon(self)
        self.tray.setToolTip(APP_NAME)

        icon_path = SCRIPT_DIR / "ICONA" / "ICONA_Trasparente.png"
        if icon_path.exists():
            icon = QIcon(str(icon_path))
        else:
            pixmap = QPixmap(64, 64)
            pixmap.fill(QColor("#3498db"))
            icon = QIcon(pixmap)

        self.tray.setIcon(icon)
        self.setWindowIcon(icon)

        tray_menu = QMenu()
        self._tray_show_action = QAction(get_text("tray_show", self.current_lang), self)
        self._tray_show_action.triggered.connect(self.show)
        tray_menu.addAction(self._tray_show_action)
        tray_menu.addSeparator()

        self._tray_start_action = QAction(get_text("tray_start", self.current_lang), self)
        self._tray_start_action.triggered.connect(lambda: self.run_command(f"{DOCKER_COMPOSE} up -d", self.tr_text("starting_msg")))
        tray_menu.addAction(self._tray_start_action)

        self._tray_stop_action = QAction(get_text("tray_stop", self.current_lang), self)
        self._tray_stop_action.triggered.connect(lambda: self.run_command(f"{DOCKER_COMPOSE} down", self.tr_text("stopping_msg")))
        tray_menu.addAction(self._tray_stop_action)

        self._tray_browser_action = QAction(get_text("tray_browser", self.current_lang), self)
        self._tray_browser_action.triggered.connect(self._open_browser_tray)
        tray_menu.addAction(self._tray_browser_action)
        tray_menu.addSeparator()

        self._tray_quit_action = QAction(get_text("tray_quit", self.current_lang), self)
        self._tray_quit_action.triggered.connect(self.confirm_and_quit)
        tray_menu.addAction(self._tray_quit_action)

        self.tray.setContextMenu(tray_menu)
        self.tray.activated.connect(self._tray_activated)
        self.tray.show()

    def _tray_activated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            self.show()
            self.raise_()

    def _open_browser_tray(self):
        if IS_WINDOWS:
            os.startfile(URL_WEBUI)
        elif IS_MAC:
            subprocess.Popen(['open', URL_WEBUI], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            subprocess.Popen(['xdg-open', URL_WEBUI], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # === Dark Mode ===

    def toggle_dark_mode(self):
        self.is_dark_mode = self.dark_mode_btn.isChecked()
        if self.is_dark_mode:
            self.dark_mode_btn.setText("\u2600\ufe0f Light Mode")
            self.setStyleSheet(self._get_dark_theme())
        else:
            self.dark_mode_btn.setText("\U0001f319 Dark Mode")
            self.setStyleSheet(self._get_light_theme())

    def _get_light_theme(self):
        return """
            QMainWindow { background-color: #f5f6fa; }
            QGroupBox { background-color: white; border: 1px solid #dcdde1; border-radius: 8px; margin-top: 12px; padding: 15px; }
            QGroupBox::title { subcontrol-origin: margin; left: 15px; padding: 0 5px; color: #2c3e50; }
            QListWidget { border: 1px solid #dcdde1; border-radius: 6px; padding: 5px; }
            QLineEdit, QComboBox { padding: 8px; border: 1px solid #dcdde1; border-radius: 6px; background: white; }
            QLineEdit:focus, QComboBox:focus { border-color: #3498db; }
            QTabWidget::pane { border: none; background: transparent; }
            QTabBar::tab { background: #ecf0f1; border: none; padding: 12px 20px; margin-right: 2px; border-top-left-radius: 6px; border-top-right-radius: 6px; }
            QTabBar::tab:selected { background: white; color: #3498db; font-weight: bold; }
            QTabBar::tab:hover:!selected { background: #dfe6e9; }
        """

    def _get_dark_theme(self):
        return """
            QMainWindow { background-color: #1a1a2e; }
            QWidget { background-color: #1a1a2e; color: #eaeaea; }
            QGroupBox { background-color: #16213e; border: 1px solid #0f3460; border-radius: 8px; margin-top: 12px; padding: 15px; color: #eaeaea; }
            QGroupBox::title { subcontrol-origin: margin; left: 15px; padding: 0 5px; color: #e94560; }
            QListWidget { background-color: #16213e; border: 1px solid #0f3460; border-radius: 6px; color: #eaeaea; }
            QLineEdit, QComboBox { padding: 8px; border: 1px solid #0f3460; border-radius: 6px; background: #16213e; color: #eaeaea; }
            QLineEdit:focus, QComboBox:focus { border-color: #e94560; }
            QTextEdit { background-color: #16213e; border: 1px solid #0f3460; color: #eaeaea; }
            QLabel { color: #eaeaea; }
            QTabWidget::pane { border: none; background: transparent; }
            QTabBar::tab { background: #16213e; border: none; padding: 12px 20px; margin-right: 2px; border-top-left-radius: 6px; border-top-right-radius: 6px; color: #eaeaea; }
            QTabBar::tab:selected { background: #0f3460; color: #e94560; font-weight: bold; }
            QTabBar::tab:hover:!selected { background: #1a1a2e; }
            QPushButton { background-color: #16213e; border: 1px solid #0f3460; color: #eaeaea; }
            QPushButton:hover { background-color: #0f3460; }
            QTableWidget { background-color: #16213e; gridline-color: #0f3460; color: #eaeaea; }
            QHeaderView::section { background-color: #0f3460; color: #eaeaea; border: 1px solid #16213e; }
        """

    # === Status Checker ===

    def start_status_checker(self):
        self.status_checker = StatusChecker()
        self.status_checker.status_signal.connect(self.update_status)
        self.status_checker.start()

    def update_status(self, status):
        self.dashboard.update_status(status)
        self._last_service_status = status

        for key, widget in [('ollama', self.mini_ollama), ('openwebui', self.mini_webui), ('tts', self.mini_tts)]:
            active = status.get(key)
            name = widget.text().split(" ", 1)[-1]
            if active:
                widget.setText(f"\u25cf {name}")
                widget.setStyleSheet("font-size: 10px; color: #27ae60;")
            else:
                widget.setText(f"\u25cf {name}")
                widget.setStyleSheet("font-size: 10px; color: #e74c3c;")

        if not self._operation_active:
            any_active = status.get('ollama') or status.get('openwebui')
            self.dashboard.btn_stop.setEnabled(bool(any_active))
            self.dashboard.btn_open_browser.setEnabled(bool(status.get('openwebui')))

        if not self._operation_active:
            self.statusBar().showMessage(self.tr_text("ready"))

    # === Command Execution ===

    def _set_operation_in_progress(self, active):
        self._operation_active = active
        for btn in [self.dashboard.btn_start, self.dashboard.btn_stop,
                     self.dashboard.btn_restart, self.dashboard.btn_open_browser]:
            btn.setEnabled(not active)
        self.cancel_btn.setVisible(active)

    def _update_elapsed(self):
        elapsed = int(time.time() - self._op_start_time)
        self.statusBar().showMessage(f"{self._current_op_message} ({elapsed}s)")

    def cancel_operation(self):
        if self.worker and self.worker.isRunning():
            self.worker.cancel()
            self.logs.append_log(f"\n\u26a0 {self.tr_text('op_cancelled_user')}")

    def run_command(self, command, message=None):
        if message is None:
            message = self.tr_text("executing")
        QApplication.setOverrideCursor(Qt.WaitCursor)
        self._current_op_message = message
        self._op_start_time = time.time()
        self._last_command = command
        self.statusBar().showMessage(message)
        self.statusBar().setStyleSheet("")
        self._set_operation_in_progress(True)
        self.elapsed_timer.start()
        self.tabs.setCurrentWidget(self.logs)
        self.logs.clear_logs()
        self.logs.append_log(f"$ {command}\n")

        self.worker = WorkerThread(command, SCRIPT_DIR)
        self.worker.output_signal.connect(self.logs.append_log)
        self.worker.finished_signal.connect(self.command_finished)
        self.worker.start()

    def command_finished(self, code):
        QApplication.restoreOverrideCursor()
        self.elapsed_timer.stop()
        elapsed = int(time.time() - self._op_start_time)
        self._set_operation_in_progress(False)
        t = self.tr_text

        if code == -1:
            self.statusBar().showMessage(f"{t('cancelled')} ({elapsed}s)")
            self.statusBar().setStyleSheet("background-color: #ffeaa7;")
            self.logs.append_log(f"\n\u26a0 {t('cancelled')} {elapsed}s")
        elif code == 0:
            self.statusBar().showMessage(f"{t('completed_success')} ({elapsed}s)")
            self.statusBar().setStyleSheet("background-color: #d4edda;")
            self.logs.append_log(f"\n\u2713 {t('completed_success')} {elapsed}s")
        else:
            self.statusBar().showMessage(f"{t('error')} ({code}, {elapsed}s)")
            self.statusBar().setStyleSheet("background-color: #fadbd8;")
            self.logs.append_log(f"\n\u2717 {t('error')} ({code}) {elapsed}s")
            self._show_error_dialog(code)

        reset_delay = 5000 if code == 0 else 10000
        QTimer.singleShot(reset_delay, lambda: self.statusBar().setStyleSheet(""))

        if not self.isVisible() or self.isMinimized():
            title = t("op_completed") if code == 0 else t("op_error")
            error_text = t('op_success') if code == 0 else f"{t('error')} ({code})"
            msg = f"{error_text} - {elapsed}s"
            self.tray.showMessage(title, msg, QSystemTrayIcon.Information if code == 0 else QSystemTrayIcon.Warning, 4000)

        if self.tabs.currentWidget() == self.models:
            QTimer.singleShot(1000, self.models.refresh_models)

    def _show_error_dialog(self, code):
        t = self.tr_text
        cmd = getattr(self, '_last_command', '')
        if 'docker' in cmd:
            suggestions = [t("error_docker_check"), t("error_docker_restart"), t("error_disk_space")]
        elif 'ollama pull' in cmd or 'ollama run' in cmd:
            suggestions = [t("error_ollama_check"), t("error_internet"), t("error_model_name")]
        elif 'ollama rm' in cmd:
            suggestions = [t("error_already_removed"), t("error_ollama_check")]
        else:
            suggestions = [t("error_check_logs"), t("error_check_services")]

        text = t("error_dialog_msg", code=code) + "\n"
        for s in suggestions:
            text += f"  - {s}\n"

        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle(t("error_dialog_title"))
        msg.setText(text)
        retry_btn = msg.addButton(t("retry"), QMessageBox.AcceptRole)
        log_btn = msg.addButton(t("view_log"), QMessageBox.ActionRole)
        msg.addButton(t("close"), QMessageBox.RejectRole)
        msg.exec_()
        clicked = msg.clickedButton()
        if clicked == retry_btn and cmd:
            self.run_command(cmd, self._current_op_message)
        elif clicked == log_btn:
            self.tabs.setCurrentWidget(self.logs)

    # === Font ===

    def increase_font_size(self):
        if self.font_scale < 150:
            self.font_scale += 10
            self.apply_font_scale()
            self.font_save_timer.start(10000)

    def decrease_font_size(self):
        if self.font_scale > 70:
            self.font_scale -= 10
            self.apply_font_scale()
            self.font_save_timer.start(10000)

    def apply_font_scale(self):
        self.font_size_label.setText(f"{self.font_scale}%")
        scaled_size = int(self.base_font_size * self.font_scale / 100)

        app = QApplication.instance()
        current_style = app.styleSheet() or ""
        current_style = re.sub(r'\* \{ font-size: \d+px; \}', '', current_style)
        global_font_style = f"* {{ font-size: {scaled_size}px; }}"
        app.setStyleSheet(global_font_style + current_style)

        family = self._font_families[self._current_font_idx]
        font = QFont(family, scaled_size)
        app.setFont(font)

        for widget in app.allWidgets():
            widget.update()
        self.update()
        self.repaint()

    def save_font_setting(self):
        self.settings.setValue("font_scale", self.font_scale)
        self.statusBar().showMessage(self.tr_text("font_saved", scale=self.font_scale), 3000)

    def cycle_font(self):
        """Cicla tra i font disponibili (Ctrl+F)."""
        self._current_font_idx = (self._current_font_idx + 1) % len(self._font_families)
        family = self._font_families[self._current_font_idx]
        self.settings.setValue("font_family", family)

        app = QApplication.instance()
        scaled_size = int(self.base_font_size * self.font_scale / 100)
        font = QFont(family, scaled_size)
        app.setFont(font)

        for widget in app.allWidgets():
            widget.update()
        self.update()
        self.repaint()

        self.statusBar().showMessage(
            self.tr_text("font_changed", font=family), 3000)

    # === QR / Language ===

    def update_qr_status(self):
        qr_enabled = self.config.qr_checkbox.isChecked() if hasattr(self.config, 'qr_checkbox') else False
        qr_icon = "\u2713" if qr_enabled else "\u2717"
        self.qr_status_label.setText(f"QR-Code LAN: {qr_icon}")
        QTimer.singleShot(5000, self.update_qr_status)

    def toggle_language(self):
        if self.current_lang == "it":
            self.current_lang = "en"
            self.lang_btn.setText("\U0001f1ec\U0001f1e7")
        else:
            self.current_lang = "it"
            self.lang_btn.setText("\U0001f1ee\U0001f1f9")
        self.settings.setValue("language", self.current_lang)
        self.retranslate_ui()

    def tr_text(self, key, **kwargs):
        return get_text(key, self.current_lang, **kwargs)

    def retranslate_ui(self):
        lang = self.current_lang
        t = lambda key, **kw: get_text(key, lang, **kw)
        tab_keys = ["tab_dashboard", "tab_models", "tab_voice", "tab_archive",
                     "tab_mcp", "tab_config", "tab_logs", "tab_info"]
        for i, key in enumerate(tab_keys):
            if i < self.tabs.count():
                self.tabs.setTabText(i, t(key))
        self.setWindowTitle(t("window_title"))
        self.statusBar().showMessage(t("ready"))
        if not self.dark_mode_btn.isChecked():
            self.dark_mode_btn.setText(t("dark_mode"))
        else:
            self.dark_mode_btn.setText(t("light_mode"))

        # Bottom bar
        self._font_label.setText(t("font_label"))
        self.cancel_btn.setText(t("cancel"))
        if hasattr(self, '_tray_show_action'):
            self._tray_show_action.setText(t("tray_show"))
            self._tray_start_action.setText(t("tray_start"))
            self._tray_stop_action.setText(t("tray_stop"))
            self._tray_browser_action.setText(t("tray_browser"))
            self._tray_quit_action.setText(t("tray_quit"))

        # Propaga traduzione a tutti i widget figli
        for widget in [self.dashboard, self.logs, self.models,
                       self.config, self.tts_widget, self.archivio,
                       self.info_widget, self.mcp_widget]:
            if hasattr(widget, 'retranslate_ui'):
                widget.retranslate_ui(lang)

    # === Help / First Run ===

    def _check_first_run(self):
        settings = QSettings("OpenWebUI", "Manager")
        if settings.value("first_run_completed", False, type=bool):
            return
        t = self.tr_text
        msg = QMessageBox(self)
        msg.setWindowTitle(t("first_run_title"))
        msg.setTextFormat(Qt.RichText)
        msg.setText(
            f"<h3>{t('first_run_welcome')}</h3>"
            f"<p>{t('first_run_intro')}</p>"
            "<ol>"
            f"<li><b>{t('first_run_step1')}</b> - {t('first_run_step1_desc')}</li>"
            f"<li><b>{t('first_run_step2')}</b> - {t('first_run_step2_desc')}</li>"
            f"<li><b>{t('first_run_step3')}</b> - {t('first_run_step3_desc')}</li>"
            "</ol>"
            f"<p><small>{t('first_run_ok_hint')}</small></p>"
        )
        dont_show = QCheckBox(t("dont_show_again"))
        msg.setCheckBox(dont_show)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()
        if dont_show.isChecked():
            settings.setValue("first_run_completed", True)
        self.tabs.setCurrentIndex(1)

    def _show_tab_help(self):
        idx = self.tabs.currentIndex()
        t = self.tr_text
        title_key, text_key = self._tab_help_keys.get(idx, ("tab_info", "tab_help_none"))
        # Rimuovi emoji dal nome tab per il titolo
        tab_name = t(title_key)
        # Rimuovi emoji all'inizio (formato "emoji Nome")
        clean_name = tab_name.split(" ", 1)[-1] if " " in tab_name else tab_name
        QMessageBox.information(self, f"{t('help_guide_prefix')} - {clean_name}", t(text_key))

    def show_global_help(self):
        t = self.tr_text
        help_html = f"""
        <h2>{APP_NAME} - {t('help_title')}</h2>
        <h3>{t('help_shortcuts')}</h3>
        <table style='border-collapse: collapse; width: 100%;'>
        <tr><td style='padding: 4px;'><b>Ctrl+1..8</b></td><td>{t('help_nav_tabs')}</td></tr>
        <tr><td style='padding: 4px;'><b>Ctrl+R / F5</b></td><td>{t('help_refresh')}</td></tr>
        <tr><td style='padding: 4px;'><b>Ctrl+B</b></td><td>{t('help_open_browser')}</td></tr>
        <tr><td style='padding: 4px;'><b>Ctrl+D</b></td><td>{t('help_dark_mode')}</td></tr>
        <tr><td style='padding: 4px;'><b>Ctrl+Q</b></td><td>{t('help_quit')}</td></tr>
        <tr><td style='padding: 4px;'><b>F1</b></td><td>{t('help_this_guide')}</td></tr>
        </table>
        <h3>{t('help_first_start')}</h3>
        <ol>
        <li>{t('help_step1')}</li>
        <li>{t('help_step2')}</li>
        <li>{t('help_step3')}</li>
        </ol>
        <h3>{t('help_useful_links')}</h3>
        <ul>
        <li>Open WebUI: <a href='{URL_WEBUI}'>{URL_WEBUI}</a></li>
        <li>Ollama: <a href='{URL_WEBUI.replace(str(URL_WEBUI.split(":")[-1]), "11434")}'>http://localhost:11434</a></li>
        </ul>
        """
        msg = QMessageBox(self)
        msg.setWindowTitle(f"{t('help_guide_prefix')} - {APP_NAME}")
        msg.setTextFormat(Qt.RichText)
        msg.setText(help_html)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    # === Close ===

    def confirm_and_quit(self):
        status = getattr(self, '_last_service_status', {})
        services_active = status.get('ollama') or status.get('openwebui')
        t = self.tr_text

        if services_active:
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Question)
            msg.setWindowTitle(t("close_title"))
            msg.setText(t("close_services_active"))
            close_btn = msg.addButton(t("close_manager"), QMessageBox.AcceptRole)
            stop_btn = msg.addButton(t("stop_and_close"), QMessageBox.DestructiveRole)
            msg.addButton(t("cancel"), QMessageBox.RejectRole)
            msg.exec_()
            clicked = msg.clickedButton()
            if clicked == close_btn:
                QApplication.quit()
            elif clicked == stop_btn:
                try:
                    subprocess.run(f"{DOCKER_COMPOSE} down", shell=True, cwd=SCRIPT_DIR, timeout=30)
                except subprocess.TimeoutExpired:
                    logger.warning("Timeout fermando container Docker")
                QApplication.quit()
        else:
            QApplication.quit()

    def closeEvent(self, event):
        event.ignore()
        self.hide()
        self.tray.showMessage(
            APP_NAME,
            self.tr_text("tray_still_running"),
            QSystemTrayIcon.Information, 2000
        )
