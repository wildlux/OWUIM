"""
Config Widget - Configurazione LAN, HTTPS, lingua, manutenzione.
"""
import os
import subprocess
import shutil
import socket
import threading
import webbrowser

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGroupBox,
    QLineEdit, QFrame, QDialog, QMessageBox, QPushButton,
    QCheckBox, QTextEdit, QApplication
)
from PyQt5.QtCore import Qt, QTimer, QSettings
from PyQt5.QtGui import QFont, QPixmap

try:
    import qrcode
    from io import BytesIO
    HAS_QRCODE = True
except ImportError:
    HAS_QRCODE = False

from config import IS_WINDOWS, IS_MAC, SCRIPT_DIR, SCRIPTS_DIR, DOCKER_COMPOSE, PORT_WEBUI
from ui.components import ModernButton

try:
    from translations import get_text
except ImportError:
    def get_text(key, lang="it", **kwargs): return key


class ConfigWidget(QWidget):
    """Widget per le configurazioni"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        self.settings = QSettings("OpenWebUI", "Manager")
        self.setup_ui()

    def _get_lang(self):
        if self.main_window and hasattr(self.main_window, 'current_lang'):
            return self.main_window.current_lang
        return "it"

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(10, 10, 10, 10)

        lang = self._get_lang()
        t = lambda key, **kw: get_text(key, lang, **kw)

        self._title = QLabel(t("config_title"))
        self._title.setFont(QFont("Arial", 20, QFont.Bold))
        self._title.setStyleSheet("color: #2c3e50;")
        layout.addWidget(self._title)

        # LAN Access - Layout a due colonne
        self._lan_group = QGroupBox(t("lan_access"))
        lan_main_layout = QHBoxLayout(self._lan_group)
        lan_main_layout.setSpacing(15)
        lan_main_layout.setContentsMargins(10, 12, 10, 10)

        # === COLONNA SINISTRA: Pulsanti in verticale (distanziati) ===
        left_col = QVBoxLayout()
        left_col.setSpacing(15)

        self._btn_enable_lan = ModernButton(t("enable_lan"), "green")
        self._btn_enable_lan.setToolTip(t("enable_lan_tooltip"))
        self._btn_enable_lan.clicked.connect(self.enable_lan)
        left_col.addWidget(self._btn_enable_lan)

        self._btn_disable_lan = ModernButton(t("disable_lan"), "orange")
        self._btn_disable_lan.setToolTip(t("disable_lan_tooltip"))
        self._btn_disable_lan.clicked.connect(self.disable_lan)
        left_col.addWidget(self._btn_disable_lan)

        self._btn_refresh_ip = ModernButton(t("refresh_ip_btn"), "blue")
        self._btn_refresh_ip.setToolTip(t("refresh_ip_tooltip"))
        self._btn_refresh_ip.clicked.connect(self.update_lan_info)
        left_col.addWidget(self._btn_refresh_ip)

        left_col.addStretch()
        lan_main_layout.addLayout(left_col)

        # === COLONNA DESTRA: Spiegazione ===
        self._lan_instructions = QLabel(t("lan_instructions"))
        self._lan_instructions.setWordWrap(True)
        self._lan_instructions.setStyleSheet("font-size: 11px;")
        lan_main_layout.addWidget(self._lan_instructions, 1)

        layout.addWidget(self._lan_group)

        # HTTPS
        self._https_group = QGroupBox(t("https_section"))
        https_layout = QVBoxLayout(self._https_group)
        https_layout.setContentsMargins(8, 12, 8, 8)

        self._https_info = QLabel(t("https_info_text"))
        self._https_info.setStyleSheet("font-size: 10px; color: #555;")
        https_layout.addWidget(self._https_info)

        self._btn_https = ModernButton(t("configure_https"), "purple")
        self._btn_https.setToolTip(t("configure_https_tooltip"))
        self._btn_https.clicked.connect(self.configure_https)
        https_layout.addWidget(self._btn_https)

        layout.addWidget(self._https_group)

        # Italiano
        self._lang_group = QGroupBox(t("italian_language"))
        italian_layout = QVBoxLayout(self._lang_group)
        italian_layout.setContentsMargins(8, 12, 8, 8)

        self._btn_italian = ModernButton(t("italian_guide"), "blue")
        self._btn_italian.setToolTip(t("italian_guide_tooltip"))
        self._btn_italian.clicked.connect(self.show_italian_guide)
        italian_layout.addWidget(self._btn_italian)

        layout.addWidget(self._lang_group)

        # Manutenzione
        self._maintenance_group = QGroupBox(t("maintenance"))
        maint_layout = QHBoxLayout(self._maintenance_group)
        maint_layout.setContentsMargins(8, 12, 8, 8)
        maint_layout.setSpacing(8)

        self._btn_update = ModernButton(t("update_button"), "blue")
        self._btn_update.setToolTip(t("update_tooltip"))
        self._btn_update.clicked.connect(self.update_openwebui)
        maint_layout.addWidget(self._btn_update)

        self._btn_repair = ModernButton(t("repair_button"), "orange")
        self._btn_repair.setToolTip(t("repair_tooltip"))
        self._btn_repair.clicked.connect(self.fix_openwebui)
        maint_layout.addWidget(self._btn_repair)

        self._btn_backup = ModernButton(t("backup_usb_button"), "green")
        self._btn_backup.setToolTip(t("backup_tooltip"))
        self._btn_backup.clicked.connect(self.backup_usb)
        maint_layout.addWidget(self._btn_backup)

        self._btn_update_ollama = ModernButton(t("update_ollama_button"), "purple")
        self._btn_update_ollama.setToolTip(t("update_ollama_tooltip"))
        self._btn_update_ollama.clicked.connect(lambda: webbrowser.open("https://ollama.com/download"))
        maint_layout.addWidget(self._btn_update_ollama)

        self._btn_update_docker = ModernButton(t("update_docker_button"), "gray")
        self._btn_update_docker.setToolTip(t("update_docker_tooltip"))
        self._btn_update_docker.clicked.connect(lambda: webbrowser.open("https://docs.docker.com/get-docker/"))
        maint_layout.addWidget(self._btn_update_docker)

        layout.addWidget(self._maintenance_group)
        layout.addStretch()

    def retranslate_ui(self, lang):
        t = lambda key, **kw: get_text(key, lang, **kw)
        self._title.setText(t("config_title"))
        self._lan_group.setTitle(t("lan_access"))
        self._https_group.setTitle(t("https_section"))
        self._lang_group.setTitle(t("italian_language"))
        self._maintenance_group.setTitle(t("maintenance"))
        self._btn_enable_lan.setText(t("enable_lan"))
        self._btn_enable_lan.setToolTip(t("enable_lan_tooltip"))
        self._btn_disable_lan.setText(t("disable_lan"))
        self._btn_disable_lan.setToolTip(t("disable_lan_tooltip"))
        self._btn_refresh_ip.setText(t("refresh_ip_btn"))
        self._btn_refresh_ip.setToolTip(t("refresh_ip_tooltip"))
        self._btn_https.setText(t("configure_https"))
        self._btn_https.setToolTip(t("configure_https_tooltip"))
        self._https_info.setText(t("https_info_text"))
        self._btn_italian.setText(t("italian_guide"))
        self._btn_italian.setToolTip(t("italian_guide_tooltip"))
        self._btn_update.setText(t("update_button"))
        self._btn_update.setToolTip(t("update_tooltip"))
        self._btn_repair.setText(t("repair_button"))
        self._btn_repair.setToolTip(t("repair_tooltip"))
        self._btn_backup.setText(t("backup_usb_button"))
        self._btn_backup.setToolTip(t("backup_tooltip"))
        self._btn_update_ollama.setText(t("update_ollama_button"))
        self._btn_update_ollama.setToolTip(t("update_ollama_tooltip"))
        self._btn_update_docker.setText(t("update_docker_button"))
        self._btn_update_docker.setToolTip(t("update_docker_tooltip"))
        self._lan_instructions.setText(t("lan_instructions"))

    def get_local_ip(self):
        """Ottiene l'IP locale della macchina."""
        import socket
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except OSError:
            return "192.168.1.X"

    def update_lan_info(self):
        """Aggiorna le informazioni LAN visualizzate."""
        ip = self.get_local_ip()
        self.lan_status_label.setText(
            get_text("lan_mobile_info", self._get_lang(), ip=ip, port=PORT_WEBUI)
        )

    def show_lan_qr_dialog(self, ip):
        """Mostra dialog con QR code per connessione LAN."""
        url = f"http://{ip}:3000"

        dialog = QDialog(self)
        lang = self._get_lang()
        dialog.setWindowTitle(get_text("lan_enabled_title", lang))
        dialog.setMinimumWidth(400)

        layout = QVBoxLayout(dialog)

        # Titolo
        title = QLabel(get_text("scan_qr_title", lang))
        title.setFont(QFont("Arial", 12, QFont.Bold))
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
            no_qr = QLabel(get_text("no_qr_install", lang))
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
        pwa_info = QLabel(get_text("pwa_instructions", lang))
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
            get_text("enabling_lan", self._get_lang())
        )
        # Mostra dialog con QR code
        self.show_lan_qr_dialog(ip)
        self.update_lan_info()

    def disable_lan(self):
        self.main_window.run_command(
            f"sed -i 's/0\\.0\\.0\\.0:3000/127.0.0.1:3000/g' docker-compose.yml && "
            f"sed -i 's/0\\.0\\.0\\.0:11434/127.0.0.1:11434/g' docker-compose.yml && "
            f"{DOCKER_COMPOSE} down && {DOCKER_COMPOSE} up -d",
            get_text("disabling_lan", self._get_lang())
        )
        lang = self._get_lang()
        QMessageBox.information(
            self,
            get_text("lan_disabled_title", lang),
            get_text("lan_disabled_msg", lang)
        )

    def configure_https(self):
        script = SCRIPTS_DIR / "enable_https.sh"
        if script.exists():
            self.main_window.run_command(f"bash {script}", get_text("configuring_https", self._get_lang()))
        else:
            QMessageBox.warning(self, get_text("error", self._get_lang()), get_text("https_script_error", self._get_lang()))

    def save_qr_setting(self, state):
        """Salva l'impostazione QR-Code LAN"""
        enabled = state == Qt.Checked
        self.settings.setValue("qr_lan_enabled", enabled)

    def show_italian_guide(self):
        lang = self._get_lang()
        guide = get_text("italian_guide_html", lang)
        msg = QMessageBox(self)
        msg.setWindowTitle(get_text("italian_guide_title", lang))
        msg.setTextFormat(Qt.RichText)
        msg.setText(guide)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    def update_openwebui(self):
        """Controlla se c'e' una nuova versione e propone l'aggiornamento."""
        import threading

        QApplication.setOverrideCursor(Qt.WaitCursor)
        self._update_btn_ref = self.sender()
        if self._update_btn_ref:
            self._update_btn_ref.setEnabled(False)
            self._update_btn_ref.setText(get_text("checking", self._get_lang()))

        def _check_versions():
            current = "?"
            latest = "?"
            latest_date = ""
            changelog_url = ""
            error = None

            try:
                import requests
                # Versione attuale
                try:
                    resp = requests.get("http://localhost:3000/api/config", timeout=5)
                    if resp.status_code == 200:
                        current = resp.json().get("version", "?")
                except (requests.RequestException, ValueError, KeyError):
                    current = "non raggiungibile"

                # Ultima versione da GitHub
                resp = requests.get(
                    "https://api.github.com/repos/open-webui/open-webui/releases/latest",
                    timeout=10
                )
                if resp.status_code == 200:
                    data = resp.json()
                    latest = data.get("tag_name", "?").lstrip("v")
                    latest_date = data.get("published_at", "")[:10]
                    changelog_url = data.get("html_url", "")
            except Exception as e:
                error = str(e)

            QTimer.singleShot(0, lambda: self._show_update_dialog(current, latest, latest_date, changelog_url, error))

        threading.Thread(target=_check_versions, daemon=True).start()

    def _show_update_dialog(self, current, latest, latest_date, changelog_url, error):
        """Mostra il dialog di aggiornamento con confronto versioni."""
        lang = self._get_lang()
        t = lambda key, **kw: get_text(key, lang, **kw)
        QApplication.restoreOverrideCursor()
        if self._update_btn_ref:
            self._update_btn_ref.setEnabled(True)
            self._update_btn_ref.setText(t("update_button"))

        if error:
            QMessageBox.warning(self, t("version_check_error_title"),
                t("version_check_error_msg", error=error))
            return

        is_up_to_date = (current == latest)

        msg = QMessageBox(self)
        msg.setWindowTitle(t("update_title"))

        changelog_text = t("update_changelog")

        if is_up_to_date:
            msg.setIcon(QMessageBox.Information)
            msg.setText(f"<b>{t('update_up_to_date')}</b>")
            msg.setInformativeText(
                f"{t('update_version_installed', current=current)}\n"
                f"{t('update_version_latest', latest=latest, date=latest_date)}\n\n"
                f"{t('update_no_action')}"
            )
            msg.setStandardButtons(QMessageBox.Ok)
            if changelog_url:
                msg.addButton(changelog_text, QMessageBox.HelpRole)
        else:
            msg.setIcon(QMessageBox.Question)
            msg.setText(f"<b>{t('update_available')}</b>")
            msg.setInformativeText(
                f"{t('update_version_installed', current=current)}\n"
                f"{t('update_version_latest', latest=latest, date=latest_date)}\n\n"
                f"{t('update_details')}"
            )
            update_now_text = t("update_now")
            update_btn = msg.addButton(update_now_text, QMessageBox.AcceptRole)
            msg.addButton(t("update_not_now"), QMessageBox.RejectRole)
            if changelog_url:
                msg.addButton(changelog_text, QMessageBox.HelpRole)

        result = msg.exec_()
        clicked = msg.clickedButton()

        if clicked and clicked.text() == changelog_text and changelog_url:
            import webbrowser
            webbrowser.open(changelog_url)
            return

        if not is_up_to_date and clicked and hasattr(self, '_update_btn_ref'):
            update_now_text = t("update_now")
            if clicked.text() == update_now_text:
                self.main_window.run_command(
                    f"{DOCKER_COMPOSE} pull && {DOCKER_COMPOSE} up -d",
                    t("updating_openwebui")
                )

    def fix_openwebui(self):
        self.main_window.run_command(f"{DOCKER_COMPOSE} down && {DOCKER_COMPOSE} up -d --force-recreate", get_text("repairing_openwebui", self._get_lang()))

    def backup_usb(self):
        lang = self._get_lang()
        script = SCRIPTS_DIR / "backup_to_usb.sh"
        if IS_WINDOWS:
            QMessageBox.information(
                self, get_text("backup_title", lang),
                get_text("backup_windows_msg", lang, path=str(SCRIPT_DIR))
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
            QMessageBox.warning(self, get_text("error", lang), get_text("script_not_found", lang))
