"""
Dashboard Widget - Panoramica stato servizi e risorse sistema.
"""

import os
import subprocess
from datetime import datetime

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGroupBox,
    QGridLayout, QProgressBar, QFrame, QPushButton
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont

from config import (
    IS_WINDOWS, IS_MAC, SCRIPT_DIR, DOCKER_COMPOSE,
    URL_WEBUI, URL_OLLAMA, SPACING_MEDIUM,
)
from ui.components import ModernButton, StatusIndicator

try:
    from translations import get_text
except ImportError:
    def get_text(key, lang="it", **kwargs): return key

import sys
sys.path.insert(0, str(SCRIPT_DIR / "scripts"))
try:
    from system_profiler import get_system_profile, SystemTier
    HAS_PROFILER = True
except ImportError:
    HAS_PROFILER = False


class DashboardWidget(QWidget):
    """Widget Dashboard principale."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        self.setup_ui()

    def _get_lang(self):
        if self.main_window and hasattr(self.main_window, 'current_lang'):
            return self.main_window.current_lang
        return "it"

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)

        self._title = QLabel(get_text("dashboard_title", self._get_lang()))
        self._title.setFont(QFont("Arial", 20, QFont.Bold))
        self._title.setStyleSheet("color: #2c3e50;")
        layout.addWidget(self._title)

        # Stato servizi
        self._services_group = QGroupBox(get_text("service_status", self._get_lang()))
        self._services_group.setFont(QFont("Arial", 12, QFont.Bold))
        status_layout = QVBoxLayout(self._services_group)

        self.ollama_status = StatusIndicator("Ollama")
        self.openwebui_status = StatusIndicator("Open WebUI")
        self.tts_status = StatusIndicator("TTS (Speech)")

        status_layout.addWidget(self.ollama_status)
        status_layout.addWidget(self.openwebui_status)
        status_layout.addWidget(self.tts_status)

        self.last_check_label = QLabel(f"{get_text('last_check', self._get_lang())} --")
        self.last_check_label.setStyleSheet("font-size: 10px; color: #95a5a6; margin-top: 2px;")
        status_layout.addWidget(self.last_check_label)

        layout.addWidget(self._services_group)

        # Risorse Sistema
        if HAS_PROFILER:
            self._setup_system_resources(layout)

        # Azioni rapide
        self._actions_group = QGroupBox(get_text("quick_actions", self._get_lang()))
        self._actions_group.setFont(QFont("Arial", 12, QFont.Bold))
        actions_layout = QGridLayout(self._actions_group)
        actions_layout.setSpacing(15)
        actions_layout.setContentsMargins(8, 12, 8, 8)

        self.btn_start = ModernButton(get_text("start_button", self._get_lang()), "green")
        self.btn_stop = ModernButton(get_text("stop_button", self._get_lang()), "red")
        self.btn_restart = ModernButton(get_text("restart_button", self._get_lang()), "orange")
        self.btn_open_browser = ModernButton(get_text("open_browser", self._get_lang()), "blue")

        self.btn_start.setToolTip(get_text("start_tooltip", self._get_lang()))
        self.btn_stop.setToolTip(get_text("stop_tooltip", self._get_lang()))
        self.btn_restart.setToolTip(get_text("restart_tooltip", self._get_lang()))
        self.btn_open_browser.setToolTip(get_text("open_browser_tooltip", self._get_lang()))

        self.btn_start.clicked.connect(self.start_services)
        self.btn_stop.clicked.connect(self.stop_services)
        self.btn_restart.clicked.connect(self.restart_services)
        self.btn_open_browser.clicked.connect(self.open_browser)

        actions_layout.addWidget(self.btn_start, 0, 0)
        actions_layout.addWidget(self.btn_stop, 0, 1)
        actions_layout.addWidget(self.btn_restart, 1, 0)
        actions_layout.addWidget(self.btn_open_browser, 1, 1)
        layout.addWidget(self._actions_group)

        # Info
        self._details_group = QGroupBox(get_text("details_links", self._get_lang()))
        self._details_group.setFont(QFont("Arial", 12, QFont.Bold))
        info_layout = QVBoxLayout(self._details_group)
        info_layout.setSpacing(6)

        from config import URL_WEBUI, URL_OLLAMA
        self._info_text = QLabel(
            f"🌐 Open WebUI: <a href='{URL_WEBUI}'>{URL_WEBUI}</a><br>"
            f"🤖 Ollama API: <a href='{URL_OLLAMA}'>{URL_OLLAMA}</a><br>"
            f"🔊 TTS API: <a href='http://localhost:5556'>http://localhost:5556</a><br>"
            f"📁 Directory: {SCRIPT_DIR}<br><br>"
            f"{get_text('archive_desc', self._get_lang())}<br>"
            f"{get_text('voice_desc', self._get_lang())}"
        )
        self._info_text.setOpenExternalLinks(True)
        self._info_text.setFont(QFont("Arial", 10))
        self._info_text.setWordWrap(True)
        info_layout.addWidget(self._info_text)

        # Nota cellulare
        mobile_row = QHBoxLayout()
        mobile_row.setSpacing(8)
        self._mobile_label = QLabel(get_text("mobile_note", self._get_lang()))
        self._mobile_label.setStyleSheet("font-size: 10px; color: #27ae60;")
        mobile_row.addWidget(self._mobile_label)
        mobile_row.addStretch()

        self._config_link = QPushButton(get_text("config_menu_link", self._get_lang()))
        self._config_link.setStyleSheet("""
            QPushButton {
                background: none; border: none; color: #3498db;
                font-size: 10px; text-decoration: underline;
            }
            QPushButton:hover { color: #2980b9; }
        """)
        self._config_link.setCursor(Qt.PointingHandCursor)
        self._config_link.clicked.connect(lambda: self.main_window.tabs.setCurrentIndex(5))
        mobile_row.addWidget(self._config_link)

        info_layout.addLayout(mobile_row)
        layout.addWidget(self._details_group)
        layout.addStretch()

    def _setup_system_resources(self, layout):
        """Crea la sezione risorse sistema."""
        self._resources_group = QGroupBox(get_text("system_resources", self._get_lang()))
        self._resources_group.setFont(QFont("Arial", 12, QFont.Bold))
        system_layout = QHBoxLayout(self._resources_group)
        system_layout.setSpacing(20)

        # Colonna sinistra
        left_col = QVBoxLayout()

        self.gpu_label = QLabel(get_text("gpu_detecting", self._get_lang()))
        self.gpu_label.setFont(QFont("Arial", 10))
        self.gpu_label.setStyleSheet("color: #2c3e50;")
        left_col.addWidget(self.gpu_label)

        cpu_ram_row = QHBoxLayout()
        self.cpu_label = QLabel("CPU: --")
        self.cpu_label.setFont(QFont("Arial", 10))
        self.cpu_label.setStyleSheet("color: #555;")
        cpu_ram_row.addWidget(self.cpu_label)
        cpu_ram_row.addSpacing(15)
        self.ram_label = QLabel("RAM: --")
        self.ram_label.setFont(QFont("Arial", 10))
        self.ram_label.setStyleSheet("color: #555;")
        cpu_ram_row.addWidget(self.ram_label)
        self.ram_bar = QProgressBar()
        self.ram_bar.setMaximumWidth(120)
        self.ram_bar.setMaximumHeight(16)
        self.ram_bar.setStyleSheet("""
            QProgressBar { border: 1px solid #bdc3c7; border-radius: 5px; text-align: center; font-size: 10px; }
            QProgressBar::chunk { background-color: #3498db; border-radius: 4px; }
        """)
        cpu_ram_row.addWidget(self.ram_bar)
        cpu_ram_row.addStretch()
        left_col.addLayout(cpu_ram_row)

        tier_row = QHBoxLayout()
        self.tier_label = QLabel("--")
        self.tier_label.setFont(QFont("Arial", 10, QFont.Bold))
        tier_row.addWidget(self.tier_label)
        tier_row.addSpacing(10)
        self.protection_label = QLabel("")
        self.protection_label.setFont(QFont("Arial", 10))
        tier_row.addWidget(self.protection_label)
        tier_row.addStretch()
        left_col.addLayout(tier_row)

        system_layout.addLayout(left_col)

        vsep = QFrame()
        vsep.setFrameShape(QFrame.VLine)
        vsep.setStyleSheet("background-color: #ddd;")
        system_layout.addWidget(vsep)

        right_col = QVBoxLayout()
        self.limits_label = QLabel("Timeout TTS: -- sec")
        self.limits_label.setFont(QFont("Arial", 10))
        self.limits_label.setStyleSheet("color: #7f8c8d;")
        right_col.addWidget(self.limits_label)

        self.ai_ready_label = QLabel("")
        self.ai_ready_label.setFont(QFont("Arial", 10, QFont.Bold))
        right_col.addWidget(self.ai_ready_label)

        system_layout.addLayout(right_col)
        layout.addWidget(self._resources_group)

        self.update_system_info()
        self.system_timer = QTimer()
        self.system_timer.timeout.connect(self.update_system_info)
        self.system_timer.start(5000)

    def retranslate_ui(self, lang):
        t = lambda key, **kw: get_text(key, lang, **kw)
        self._title.setText(t("dashboard_title"))
        self._services_group.setTitle(t("service_status"))
        if hasattr(self, '_resources_group'):
            self._resources_group.setTitle(t("system_resources"))
        self._actions_group.setTitle(t("quick_actions"))
        self._details_group.setTitle(t("details_links"))
        self.btn_start.setText(t("start_button"))
        self.btn_stop.setText(t("stop_button"))
        self.btn_restart.setText(t("restart_button"))
        self.btn_open_browser.setText(t("open_browser"))

        # Tooltip
        self.btn_start.setToolTip(t("start_tooltip"))
        self.btn_stop.setToolTip(t("stop_tooltip"))
        self.btn_restart.setToolTip(t("restart_tooltip"))
        self.btn_open_browser.setToolTip(t("open_browser_tooltip"))

        # Info text
        from config import URL_WEBUI, URL_OLLAMA
        self._info_text.setText(
            f"🌐 Open WebUI: <a href='{URL_WEBUI}'>{URL_WEBUI}</a><br>"
            f"🤖 Ollama API: <a href='{URL_OLLAMA}'>{URL_OLLAMA}</a><br>"
            f"🔊 TTS API: <a href='http://localhost:5556'>http://localhost:5556</a><br>"
            f"📁 Directory: {SCRIPT_DIR}<br><br>"
            f"{t('archive_desc')}<br>"
            f"{t('voice_desc')}"
        )
        self._mobile_label.setText(t("mobile_note"))
        self._config_link.setText(t("config_menu_link"))

        # Status indicators
        for indicator in [self.ollama_status, self.openwebui_status, self.tts_status]:
            indicator.set_lang(lang)

        # Aggiorna system info con nuova lingua
        if HAS_PROFILER:
            self.update_system_info()

    def update_status(self, status):
        self.ollama_status.set_status(status.get('ollama'))
        self.openwebui_status.set_status(status.get('openwebui'))
        self.tts_status.set_status(status.get('tts'))

    def start_services(self):
        t = lambda key, **kw: get_text(key, self._get_lang(), **kw)
        self.main_window.run_command(f"{DOCKER_COMPOSE} up -d", t("starting_msg"))

    def stop_services(self):
        t = lambda key, **kw: get_text(key, self._get_lang(), **kw)
        self.main_window.run_command(f"{DOCKER_COMPOSE} down", t("stopping_msg"))

    def restart_services(self):
        t = lambda key, **kw: get_text(key, self._get_lang(), **kw)
        self.main_window.run_command(f"{DOCKER_COMPOSE} down && {DOCKER_COMPOSE} up -d", t("restarting_msg"))

    def open_browser(self):
        if IS_WINDOWS:
            os.startfile(URL_WEBUI)
        elif IS_MAC:
            subprocess.Popen(['open', URL_WEBUI], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            subprocess.Popen(['xdg-open', URL_WEBUI], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def update_system_info(self):
        """Aggiorna le informazioni sul sistema."""
        lang = self._get_lang()
        t = lambda key, **kw: get_text(key, lang, **kw)
        self.last_check_label.setText(f"{t('last_check')} {datetime.now().strftime('%H:%M:%S')}")
        if not HAS_PROFILER:
            return

        try:
            profile = get_system_profile()

            # GPU
            if profile.has_gpu and profile.gpu_name:
                vram_text = f" ({profile.gpu_vram_gb} GB VRAM)" if profile.gpu_vram_gb > 0 else ""
                self.gpu_label.setText(f"GPU: {profile.gpu_name}{vram_text}")
                self.gpu_label.setStyleSheet("color: #27ae60; font-weight: bold;")
            else:
                self.gpu_label.setText(t("gpu_not_detected_label"))
                self.gpu_label.setStyleSheet("color: #e67e22;")

            # CPU
            cpu_short = profile.cpu_name[:40] + "..." if len(profile.cpu_name) > 40 else profile.cpu_name
            self.cpu_label.setText(f"CPU: {cpu_short} ({profile.cpu_cores} core)")

            # RAM
            self.ram_label.setText(f"RAM: {profile.ram_available_gb:.1f}/{profile.ram_total_gb:.1f} GB")
            self.ram_bar.setValue(int(profile.ram_percent_used))

            if profile.ram_percent_used >= profile.ram_critical_threshold:
                bar_color = "#e74c3c"
            elif profile.ram_percent_used >= profile.ram_warning_threshold:
                bar_color = "#f39c12"
            else:
                bar_color = "#27ae60"
            self.ram_bar.setStyleSheet(f"""
                QProgressBar {{ border: 1px solid #bdc3c7; border-radius: 5px; text-align: center; font-size: 10px; }}
                QProgressBar::chunk {{ background-color: {bar_color}; border-radius: 4px; }}
            """)

            # Tier
            tier_keys = {
                SystemTier.MINIMAL: ("#e74c3c", "tier_minimal"),
                SystemTier.LOW: ("#f39c12", "tier_low"),
                SystemTier.MEDIUM: ("#27ae60", "tier_medium"),
                SystemTier.HIGH: ("#3498db", "tier_high")
            }
            color, key = tier_keys.get(profile.tier, ("#7f8c8d", profile.tier.value))
            self.tier_label.setText(t(key))
            self.tier_label.setStyleSheet(f"color: {color};")

            self.limits_label.setText(t("tts_timeout_label", tts=profile.timeout_tts, llm=profile.timeout_llm))

            if profile.ram_percent_used >= profile.ram_critical_threshold:
                self.protection_label.setText(t("protection_critical"))
                self.protection_label.setStyleSheet("color: #e74c3c; font-weight: bold;")
                self.ai_ready_label.setText(t("close_apps"))
                self.ai_ready_label.setStyleSheet("color: #e74c3c;")
            elif profile.ram_percent_used >= profile.ram_warning_threshold:
                self.protection_label.setText(t("protection_high"))
                self.protection_label.setStyleSheet("color: #f39c12;")
                self.ai_ready_label.setText(t("system_working"))
                self.ai_ready_label.setStyleSheet("color: #f39c12;")
            else:
                self.protection_label.setText(t("protection_ok"))
                self.protection_label.setStyleSheet("color: #27ae60;")
                if profile.has_gpu:
                    self.ai_ready_label.setText(t("system_ready_gpu"))
                else:
                    self.ai_ready_label.setText(t("system_ready"))
                self.ai_ready_label.setStyleSheet("color: #27ae60;")

        except Exception as e:
            self.tier_label.setText(f"{t('error')}: {e}")
