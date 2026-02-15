"""
TTS Widget - Sintesi vocale italiana locale con Piper.
"""
import os
import subprocess
import logging
import shutil
from pathlib import Path

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGroupBox,
    QComboBox, QLineEdit, QTextEdit, QFrame, QScrollArea,
    QPushButton, QMessageBox, QApplication
)
from PyQt5.QtCore import Qt, QTimer, QUrl
from PyQt5.QtGui import QFont

try:
    from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
    HAS_MULTIMEDIA = True
except ImportError:
    HAS_MULTIMEDIA = False

try:
    from translations import get_text
except ImportError:
    def get_text(key, lang="it", **kwargs): return key

from config import (
    IS_WINDOWS, IS_MAC, SCRIPT_DIR, URL_TTS, URL_TTS_DOCKER,
    URL_OPENEDAI_SPEECH_DOCKER, PYTHON_EXE, TTS_SCRIPT, PORT_TTS,
)
from ui.components import ModernButton

logger = logging.getLogger(__name__)


class TTSWidget(QWidget):
    """Widget per configurare e testare la sintesi vocale italiana LOCALE."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        self.tts_service_url = URL_TTS
        self.audio_file = None  # Path del file audio temporaneo

        # Media player per riproduzione audio
        if HAS_MULTIMEDIA:
            self.player = QMediaPlayer()
            self.player.stateChanged.connect(self._on_player_state_changed)
            self.player.error.connect(self._on_player_error)
        else:
            self.player = None

        self.setup_ui()

    def _get_lang(self):
        if self.main_window and hasattr(self.main_window, 'current_lang'):
            return self.main_window.current_lang
        return "it"

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

        lang = self._get_lang()
        t = lambda key, **kw: get_text(key, lang, **kw)

        # === STATO SERVIZIO ===
        status_group = QGroupBox(t("tts_status"))
        self._status_group = status_group
        status_main_layout = QVBoxLayout(status_group)
        status_main_layout.setSpacing(8)
        status_main_layout.setContentsMargins(10, 12, 10, 10)

        # Riga stato + toggle + pulsanti
        status_row = QHBoxLayout()
        self.status_indicator = QLabel("●")
        self.status_indicator.setFont(QFont("Arial", 14))
        self.status_indicator.setStyleSheet("color: #f39c12;")
        status_row.addWidget(self.status_indicator)

        self.status_label = QLabel(t("tts_verifying"))
        self.status_label.setFont(QFont("Arial", 10))
        status_row.addWidget(self.status_label)
        status_row.addStretch()

        # Toggle TTS On/Off
        self.tts_toggle_btn = QPushButton(t("tts_on"))
        self.tts_toggle_btn.setCheckable(True)
        self.tts_toggle_btn.setChecked(True)
        self.tts_toggle_btn.setStyleSheet("""
            QPushButton {
                font-size: 10px; font-weight: bold;
                padding: 5px 12px;
                border: 2px solid #27ae60;
                border-radius: 12px;
                background: #27ae60;
                color: white;
            }
            QPushButton:checked {
                background: #27ae60;
                border-color: #27ae60;
            }
            QPushButton:!checked {
                background: #e74c3c;
                border-color: #e74c3c;
            }
        """)
        self.tts_toggle_btn.clicked.connect(self.toggle_tts_service)
        status_row.addWidget(self.tts_toggle_btn)

        self.start_service_btn = ModernButton(t("start_service"), "green")
        self.start_service_btn.clicked.connect(self.start_tts_service)
        status_row.addWidget(self.start_service_btn)

        self.refresh_btn = ModernButton(t("refresh"), "gray")
        self.refresh_btn.clicked.connect(self.check_service_status)
        status_row.addWidget(self.refresh_btn)

        status_main_layout.addLayout(status_row)

        # Layout a due colonne: Voci | Test
        columns_layout = QHBoxLayout()
        columns_layout.setSpacing(15)

        # === COLONNA SINISTRA: Voci disponibili ===
        left_column = QVBoxLayout()
        left_column.setSpacing(8)

        voices_label = QLabel(t("available_voices"))
        self._voices_label = voices_label
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
        self.install_paola_btn = ModernButton(t("download_voice"), "purple")
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
        self.install_riccardo_btn = ModernButton(t("download_voice"), "purple")
        self.install_riccardo_btn.setFixedWidth(70)
        self.install_riccardo_btn.clicked.connect(lambda: self.install_voice("riccardo"))
        riccardo_row.addWidget(self.install_riccardo_btn)
        left_column.addLayout(riccardo_row)

        # Pulsante scarica tutte
        script_btn = ModernButton(t("download_all"), "blue")
        self._btn_download_all = script_btn
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

        test_label = QLabel(f"<b>{t('voice_test')}</b>")
        self._test_label = test_label
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
        self._voice_selector_label = QLabel(t("voice_label"))
        voice_row.addWidget(self._voice_selector_label)
        self.voice_combo = QComboBox()
        self.voice_combo.addItems(["paola", "riccardo"])
        self.voice_combo.setMinimumWidth(90)
        voice_row.addWidget(self.voice_combo)
        controls_layout.addLayout(voice_row)

        # Testo
        self.test_text = QLineEdit("Ciao!")
        self.test_text.setPlaceholderText(t("test_text_placeholder"))
        self.test_text.setMinimumWidth(120)
        controls_layout.addWidget(self.test_text)

        # Pulsanti
        self.test_btn = ModernButton(t("test_button"), "blue")
        self.test_btn.clicked.connect(self.test_voice)
        controls_layout.addWidget(self.test_btn)

        self.play_btn = ModernButton(t("play_button"), "green")
        self.play_btn.clicked.connect(self.play_test_audio)
        self.play_btn.setEnabled(False)
        controls_layout.addWidget(self.play_btn)

        controls_layout.addStretch()
        test_h_layout.addLayout(controls_layout)

        # Risultato a destra (più largo)
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setPlaceholderText(t("result_placeholder"))
        self.result_text.setStyleSheet("background: #f5f5f5; border: 1px solid #ddd; border-radius: 3px; font-size: 10px;")
        test_h_layout.addWidget(self.result_text, 1)

        right_column.addLayout(test_h_layout, 1)

        columns_layout.addLayout(right_column, 1)

        status_main_layout.addLayout(columns_layout, 1)

        layout.addWidget(status_group)

        # === CONFIGURAZIONE ===
        config_group = QGroupBox(t("tts_config_title"))
        self._config_group = config_group
        config_main = QVBoxLayout(config_group)
        config_main.setSpacing(6)
        config_main.setContentsMargins(10, 10, 10, 10)

        # Istruzioni
        self._config_instructions = QLabel(t("tts_config_go_to"))
        self._config_instructions.setStyleSheet("font-size: 10px; padding: 3px;")
        config_main.addWidget(self._config_instructions)

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
            label.setStyleSheet("font-size: 10px;")
            row.addWidget(label)
            field = QLineEdit(value)
            field.setReadOnly(True)
            field.setStyleSheet("font-family: 'DejaVu Sans Mono'; font-size: 10px; padding: 2px; background: #f5f5f5;")
            row.addWidget(field, 1)
            copy_btn = QPushButton("📋")
            copy_btn.setMaximumWidth(24)
            copy_btn.setMaximumHeight(22)
            copy_btn.clicked.connect(lambda: QApplication.clipboard().setText(value))
            row.addWidget(copy_btn)
            parent_layout.addLayout(row)
            return field

        create_param_row(t("tts_param_engine"), "OpenAI", left_col)
        create_param_row(t("tts_param_url"), f"{URL_OPENEDAI_SPEECH_DOCKER}/v1", left_col)
        create_param_row(t("tts_param_key"), "sk-local", left_col)
        create_param_row(t("tts_param_voice"), "alloy", left_col)

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

        docker_title = QLabel(t("tts_docker_title"))
        docker_title.setStyleSheet("font-size: 10px;")
        right_col.addWidget(docker_title)

        # Docker URL
        docker_row = QHBoxLayout()
        docker_row.setSpacing(4)
        docker_field = QLineEdit(f"{URL_OPENEDAI_SPEECH_DOCKER}/v1")
        docker_field.setReadOnly(True)
        docker_field.setStyleSheet("font-family: 'DejaVu Sans Mono'; font-size: 10px; padding: 2px; background: #fef5e7;")
        docker_row.addWidget(docker_field, 1)
        docker_copy = QPushButton("📋")
        docker_copy.setMaximumWidth(24)
        docker_copy.setMaximumHeight(22)
        docker_copy.clicked.connect(lambda: QApplication.clipboard().setText(f"{URL_OPENEDAI_SPEECH_DOCKER}/v1"))
        docker_row.addWidget(docker_copy)
        right_col.addLayout(docker_row)

        # docker-compose.yml
        self.config_text = QTextEdit()
        self.config_text.setReadOnly(True)
        self.config_text.setMaximumHeight(55)
        self.config_text.setFont(QFont("DejaVu Sans Mono", 10))
        self.config_text.setPlainText(
            "AUDIO_TTS_ENGINE=openai\n"
            f"AUDIO_TTS_OPENAI_API_BASE_URL={URL_OPENEDAI_SPEECH_DOCKER}/v1\n"
            "AUDIO_TTS_OPENAI_API_KEY=sk-local\n"
            "AUDIO_TTS_VOICE=alloy"
        )
        right_col.addWidget(self.config_text)

        # Pulsanti
        btn_row = QHBoxLayout()
        btn_row.setSpacing(5)
        copy_btn = ModernButton(t("copy_config"), "blue")
        self._btn_copy_config = copy_btn
        copy_btn.clicked.connect(self.copy_config)
        btn_row.addWidget(copy_btn)
        apply_btn = ModernButton(t("apply_config"), "orange")
        self._btn_apply_config = apply_btn
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

                lang = self._get_lang()
                tt = lambda key, **kw: get_text(key, lang, **kw)
                if ready:
                    # Sistema pronto - tutto OK
                    self.status_indicator.setStyleSheet("color: #27ae60;")
                    self.status_label.setText(tt("tts_ready", count=len(models)))
                    self.test_btn.setEnabled(True)
                    self.play_btn.setEnabled(False)  # Reset play button
                    self.result_text.setPlainText(tt("tts_ready_detail", voices=', '.join(models)))
                elif not models:
                    # Nessuna voce installata
                    self.status_indicator.setStyleSheet("color: #e74c3c;")
                    self.status_label.setText(tt("tts_missing"))
                    self.test_btn.setEnabled(False)
                    self.result_text.setPlainText(tt("tts_no_voices_warning"))
                elif not piper_available:
                    # Piper non disponibile
                    self.status_indicator.setStyleSheet("color: #f39c12;")
                    self.status_label.setText(tt("tts_piper_missing"))
                    self.test_btn.setEnabled(False)
                    self.result_text.setPlainText(tt("tts_piper_not_installed"))
                else:
                    # Stato parziale
                    self.status_indicator.setStyleSheet("color: #f39c12;")
                    self.status_label.setText(tt("tts_partial", count=len(models)))
                    self.test_btn.setEnabled(bool(models))

                self.start_service_btn.setEnabled(False)

                # Aggiorna stato voci
                if "paola" in models:
                    self.paola_status.setStyleSheet("color: #27ae60;")
                    self.paola_status.setToolTip(tt("voice_installed"))
                    self.install_paola_btn.setText(tt("voice_ok"))
                    self.install_paola_btn.setEnabled(False)
                else:
                    self.paola_status.setStyleSheet("color: #e74c3c;")
                    self.paola_status.setToolTip(tt("voice_not_installed"))
                    self.install_paola_btn.setText(tt("download_voice"))
                    self.install_paola_btn.setEnabled(True)

                if "riccardo" in models:
                    self.riccardo_status.setStyleSheet("color: #27ae60;")
                    self.riccardo_status.setToolTip(tt("voice_installed"))
                    self.install_riccardo_btn.setText(tt("voice_ok"))
                    self.install_riccardo_btn.setEnabled(False)
                else:
                    self.riccardo_status.setStyleSheet("color: #e74c3c;")
                    self.riccardo_status.setToolTip(tt("voice_not_installed"))
                    self.install_riccardo_btn.setText(tt("download_voice"))
                    self.install_riccardo_btn.setEnabled(True)
            else:
                self._set_service_offline()
        except Exception:
            self._set_service_offline()

    def _set_service_offline(self):
        self.status_indicator.setStyleSheet("color: #e74c3c;")
        self.status_label.setText(get_text("tts_offline", self._get_lang()))
        self.start_service_btn.setEnabled(True)
        self.test_btn.setEnabled(False)
        # Reset stato voci
        self.paola_status.setStyleSheet("color: #bdc3c7;")
        self.riccardo_status.setStyleSheet("color: #bdc3c7;")

    def run_download_script(self):
        """Esegue lo script per scaricare tutte le voci."""
        lang = self._get_lang()
        t = lambda key, **kw: get_text(key, lang, **kw)
        script_path = SCRIPT_DIR / "tts_service" / "download_voices.py"
        if not script_path.exists():
            QMessageBox.warning(
                self, t("script_not_found"),
                t("file_not_found", path=str(script_path))
            )
            return

        reply = QMessageBox.question(
            self, t("download_voices_title"),
            t("download_voices_confirm"),
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.result_text.setPlainText(t("voices_downloading"))
            QApplication.processEvents()

            if IS_WINDOWS:
                subprocess.Popen(
                    ['cmd', '/c', 'start', 'Download Voci', PYTHON_EXE, str(script_path)],
                    cwd=str(SCRIPT_DIR)
                )
            else:
                subprocess.Popen(
                    ['x-terminal-emulator', '-e', PYTHON_EXE, str(script_path)],
                    cwd=str(SCRIPT_DIR)
                )

            # Refresh dopo un po'
            QTimer.singleShot(10000, self.check_service_status)

    def toggle_tts_service(self):
        """Toggle TTS on/off per liberare memoria."""
        lang = self._get_lang()
        if self.tts_toggle_btn.isChecked():
            self.tts_toggle_btn.setText(get_text("tts_on", lang))
            self.start_tts_service()
        else:
            self.tts_toggle_btn.setText(get_text("tts_off", lang))
            self.stop_tts_service()

    def stop_tts_service(self):
        """Ferma il servizio TTS locale (porta 5556) per liberare memoria."""
        try:
            if IS_WINDOWS:
                # Termina solo il processo sulla porta TTS, non tutti i Python
                subprocess.run(
                    ["powershell", "-Command",
                     f"Get-NetTCPConnection -LocalPort {PORT_TTS} -ErrorAction SilentlyContinue | "
                     f"ForEach-Object {{ Stop-Process -Id $_.OwningProcess -Force }}"],
                    capture_output=True, timeout=5
                )
            else:
                # Trova e termina il processo sulla porta TTS
                result = subprocess.run(
                    ['lsof', '-t', f'-i:{PORT_TTS}'],
                    capture_output=True, text=True, timeout=5
                )
                if result.stdout.strip():
                    for pid in result.stdout.strip().split('\n'):
                        subprocess.run(['kill', pid.strip()], capture_output=True, timeout=3)
            self.status_label.setText(get_text("tts_stopped", self._get_lang()))
            self.status_indicator.setStyleSheet("color: #95a5a6;")
            QTimer.singleShot(2000, self.check_service_status)
        except Exception as e:
            self.status_label.setText(get_text("tts_error_stop", self._get_lang(), error=str(e)))

    def start_tts_service(self):
        """Avvia servizio TTS locale."""
        if IS_WINDOWS:
            subprocess.Popen(
                ['cmd', '/c', 'start', 'TTS Local', PYTHON_EXE, str(TTS_SCRIPT)],
                cwd=str(SCRIPT_DIR)
            )
        else:
            subprocess.Popen(
                [PYTHON_EXE, str(TTS_SCRIPT)],
                cwd=str(SCRIPT_DIR),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        self.status_label.setText(get_text("tts_starting", self._get_lang()))
        QTimer.singleShot(3000, self.check_service_status)

    def install_voice(self, voice_id):
        """Installa una voce italiana."""
        try:
            import requests
            self.result_text.setPlainText(get_text("voice_downloading", self._get_lang(), voice=voice_id))
            QApplication.processEvents()

            resp = requests.post(f"{self.tts_service_url}/install/{voice_id}", timeout=300)
            if resp.status_code == 200:
                result = resp.json()
                if result.get("success"):
                    self.result_text.setPlainText(get_text("voice_installed_msg", self._get_lang(), voice=voice_id))
                    self.check_service_status()
                else:
                    self.result_text.setPlainText(get_text("tts_error_generic", self._get_lang(), error=str(result)))
            else:
                self.result_text.setPlainText(get_text("tts_error_http", self._get_lang(), code=resp.status_code))
        except Exception as e:
            self.result_text.setPlainText(get_text("tts_error_generic", self._get_lang(), error=str(e)))

    def test_voice(self):
        """Testa la voce selezionata."""
        try:
            import requests
            voice = self.voice_combo.currentText().split(" ")[0]  # "paola (Femminile)" -> "paola"
            text = self.test_text.text().strip()

            if not text:
                self.result_text.setPlainText(get_text("tts_insert_text", self._get_lang()))
                return

            self.result_text.setPlainText(get_text("tts_synthesizing", self._get_lang(), voice=voice))
            self.test_btn.setEnabled(False)
            QApplication.processEvents()

            data = {"voice": voice, "text": text}
            resp = requests.post(f"{self.tts_service_url}/test", data=data, timeout=30)

            self.test_btn.setEnabled(True)

            lang = self._get_lang()
            tt = lambda key, **kw: get_text(key, lang, **kw)
            if resp.status_code == 200:
                result = resp.json()
                if result.get("success"):
                    offline_text = tt("yes_offline") if result.get('offline') else tt("no_offline")
                    self.result_text.setPlainText(
                        tt("tts_test_success",
                           voice=result.get('voice'),
                           size=result.get('audio_size_kb'),
                           time=result.get('synthesis_time_ms'),
                           offline=offline_text)
                    )
                    self.play_btn.setEnabled(True)
                else:
                    self.result_text.setPlainText(tt("tts_test_error", error=result.get('error')))
                    self.play_btn.setEnabled(False)
            else:
                self.result_text.setPlainText(tt("tts_error_http", code=resp.status_code))
                self.play_btn.setEnabled(False)
        except Exception as e:
            self.test_btn.setEnabled(True)
            lang = self._get_lang()
            tt = lambda key, **kw: get_text(key, lang, **kw)
            self.result_text.setPlainText(f"{tt('tts_test_error', error=str(e))}\n\n{tt('tts_test_ensure_active')}")
            self.play_btn.setEnabled(False)

    def play_test_audio(self):
        """Riproduce l'audio di test tramite Qt (cross-platform)."""
        try:
            import requests
            import tempfile

            # Scarica l'audio in un file temporaneo
            audio_url = f"{self.tts_service_url}/test-audio"

            lang = self._get_lang()
            tt = lambda key, **kw: get_text(key, lang, **kw)
            self.play_btn.setEnabled(False)
            self.result_text.setPlainText(
                self.result_text.toPlainText().split("\n\n▶")[0] + f"\n\n{tt('tts_audio_downloading')}"
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
                        self.result_text.toPlainText().split("\n\n⏳")[0] + f"\n\n{tt('tts_audio_playing')}"
                    )
                else:
                    # Fallback: apri con app di sistema
                    self._play_with_system(str(self.audio_file))
                    self.play_btn.setEnabled(True)
            else:
                self.result_text.setPlainText(tt("tts_audio_download_error", code=resp.status_code))
                self.play_btn.setEnabled(True)
        except Exception as e:
            self.result_text.setPlainText(get_text("tts_playback_error", self._get_lang(), error=str(e)))
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
            lang = self._get_lang()
            self.result_text.setPlainText(
                self.result_text.toPlainText().split("\n\n⏳")[0] + f"\n\n{get_text('tts_audio_system_player', lang)}"
            )
        except Exception as e:
            self.result_text.setPlainText(get_text("tts_player_open_error", self._get_lang(), error=str(e)))

    def _on_player_state_changed(self, state):
        """Callback quando cambia lo stato del player."""
        if state == QMediaPlayer.StoppedState:
            self.play_btn.setEnabled(True)
            current = self.result_text.toPlainText()
            playing_text = get_text("tts_audio_playing", self._get_lang())
            if playing_text in current:
                self.result_text.setPlainText(
                    current.replace(playing_text, get_text("tts_playback_complete", self._get_lang()))
                )
        elif state == QMediaPlayer.PlayingState:
            self.play_btn.setEnabled(False)

    def _on_player_error(self, error):
        """Callback per errori del player."""
        if error != QMediaPlayer.NoError:
            lang = self._get_lang()
            error_msg = self.player.errorString() if self.player else get_text("tts_unknown_error", lang)
            self.result_text.setPlainText(get_text("tts_player_error", lang, error=error_msg))
            self.play_btn.setEnabled(True)
            # Fallback al player di sistema
            if self.audio_file and self.audio_file.exists():
                self._play_with_system(str(self.audio_file))

    def copy_config(self):
        """Copia configurazione."""
        lang = self._get_lang()
        QApplication.clipboard().setText(self.config_text.toPlainText())
        QMessageBox.information(self, get_text("config_copied", lang), get_text("config_copied_msg", lang))

    def apply_config(self):
        """Applica configurazione al docker-compose.yml."""
        lang = self._get_lang()
        t = lambda key, **kw: get_text(key, lang, **kw)
        compose_file = SCRIPT_DIR / "docker-compose.yml"
        if not compose_file.exists():
            QMessageBox.warning(self, t("error"), t("tts_docker_not_found"))
            return

        reply = QMessageBox.question(
            self, t("confirm"),
            t("tts_apply_confirm"),
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            # Backup
            backup_file = SCRIPT_DIR / "docker-compose.yml.backup"
            shutil.copy(compose_file, backup_file)

            # Leggi e modifica
            content = compose_file.read_text()

            # Sostituisci configurazione TTS - punta a OpenedAI Speech (:8000)
            replacements = [
                ("AUDIO_TTS_OPENAI_API_BASE_URL=http://openedai-speech:8000/v1",
                 f"AUDIO_TTS_OPENAI_API_BASE_URL={URL_OPENEDAI_SPEECH_DOCKER}/v1"),
                ("AUDIO_TTS_OPENAI_API_KEY=sk-111111111", "AUDIO_TTS_OPENAI_API_KEY=sk-local"),
            ]

            for old, new in replacements:
                content = content.replace(old, new)

            compose_file.write_text(content)

            QMessageBox.information(
                self, t("done"),
                t("tts_apply_success")
            )

    def retranslate_ui(self, lang):
        t = lambda key, **kw: get_text(key, lang, **kw)
        self._status_group.setTitle(t("tts_status"))
        self._config_group.setTitle(t("tts_config_title"))
        self._config_instructions.setText(t("tts_config_go_to"))
        self.start_service_btn.setText(t("start_service"))
        self.refresh_btn.setText(t("refresh"))
        self._btn_download_all.setText(t("download_all"))
        self._voices_label.setText(t("available_voices"))
        self._test_label.setText(f"<b>{t('voice_test')}</b>")
        self._voice_selector_label.setText(t("voice_label"))
        self.test_text.setPlaceholderText(t("test_text_placeholder"))
        self.result_text.setPlaceholderText(t("result_placeholder"))
        self.test_btn.setText(t("test_button"))
        self.play_btn.setText(t("play_button"))
        self._btn_copy_config.setText(t("copy_config"))
        self._btn_apply_config.setText(t("apply_config"))
        self.tts_toggle_btn.setText(t("tts_on") if self.tts_toggle_btn.isChecked() else t("tts_off"))
        # Aggiorna stato con nuova lingua
        self.check_service_status()
