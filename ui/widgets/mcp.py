"""
MCP Widget - Gestione servizio MCP Bridge.
"""
import os
import subprocess
import socket
import threading
import webbrowser
import logging

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGroupBox,
    QLineEdit, QTextEdit, QFrame, QScrollArea,
    QPushButton, QMessageBox, QApplication
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont

try:
    from translations import get_text
except ImportError:
    def get_text(key, lang="it", **kwargs): return key

from config import (
    IS_WINDOWS, SCRIPT_DIR, URL_MCP, URL_TTS, URL_IMAGE, URL_DOCUMENT,
    PORT_TTS, PORT_IMAGE, PORT_DOCUMENT, PORT_MCP, SERVICES,
)
from ui.components import ModernButton

logger = logging.getLogger(__name__)


class MCPWidget(QWidget):
    """Widget per gestire il servizio MCP Bridge."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        self.mcp_service_url = URL_MCP
        self.setup_ui()
        # Check iniziale stato servizi dopo che la UI e' pronta
        QTimer.singleShot(1500, self.check_service_status)

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

        # Ottieni IP locale (usato in più posti)
        try:
            import socket
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            self.local_ip = s.getsockname()[0]
            s.close()
        except OSError:
            self.local_ip = "localhost"

        # ╔════════════════════════════════════════════════════════════╗
        # ║  RIGA 1: Warning (sinistra) | Risorse Sistema (destra)    ║
        # ╚════════════════════════════════════════════════════════════╝
        row1 = QHBoxLayout()
        row1.setSpacing(10)

        # === WARNING BOX (sinistra) - H8.1 compatto ===
        warning_frame = QFrame()
        warning_frame.setStyleSheet("""
            QFrame {
                background-color: #fff3cd;
                border: 1px solid #ffc107;
                border-radius: 6px;
                padding: 8px;
            }
        """)
        warning_fl = QHBoxLayout(warning_frame)
        warning_fl.setContentsMargins(8, 6, 8, 6)
        lang = self._get_lang()
        t = lambda key, **kw: get_text(key, lang, **kw)

        warning_label = QLabel(t("mcp_warning_text"))
        warning_label.setWordWrap(True)
        warning_fl.addWidget(warning_label)
        row1.addWidget(warning_frame, 1)

        # === RISORSE SISTEMA (destra) ===
        resources_group = QGroupBox(t("mcp_resources"))
        self._resources_group = resources_group
        resources_layout = QVBoxLayout(resources_group)
        resources_layout.setSpacing(4)
        resources_layout.setContentsMargins(10, 12, 10, 10)

        # RAM
        ram_row = QHBoxLayout()
        ram_row.addWidget(QLabel("<b>RAM:</b>"))
        self.ram_label = QLabel("--")
        self.ram_label.setStyleSheet("font-family: 'DejaVu Sans Mono'; font-size: 10px;")
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
        self.vram_label.setStyleSheet("font-family: 'DejaVu Sans Mono'; font-size: 10px;")
        vram_row.addWidget(self.vram_label)
        vram_row.addStretch()
        self.vram_status = QLabel("●")
        self.vram_status.setFont(QFont("Arial", 12))
        vram_row.addWidget(self.vram_status)
        resources_layout.addLayout(vram_row)

        # Pulsante aggiorna
        refresh_res_btn = ModernButton(t("detect_resources"), "gray")
        refresh_res_btn.clicked.connect(self.detect_system_resources)
        resources_layout.addWidget(refresh_res_btn)

        row1.addWidget(resources_group, 1)
        layout.addLayout(row1)

        # ╔════════════════════════════════════════════════════════════╗
        # ║  RIGA 2: Stato Servizio (intera larghezza)                ║
        # ╚════════════════════════════════════════════════════════════╝
        status_group = QGroupBox(t("mcp_service_title"))
        self._mcp_group = status_group
        status_main_layout = QHBoxLayout(status_group)
        status_main_layout.setSpacing(10)
        status_main_layout.setContentsMargins(10, 12, 10, 10)

        # Indicatore stato
        self.status_indicator = QLabel("●")
        self.status_indicator.setFont(QFont("Arial", 16))
        self.status_indicator.setStyleSheet("color: #bdc3c7;")
        status_main_layout.addWidget(self.status_indicator)

        self.status_label = QLabel(t("mcp_not_started"))
        self.status_label.setFont(QFont("Arial", 10))
        status_main_layout.addWidget(self.status_label)

        status_main_layout.addStretch()

        # Pulsanti
        self.start_service_btn = ModernButton(t("mcp_start"), "green")
        self.start_service_btn.clicked.connect(self.confirm_and_start_mcp_service)
        status_main_layout.addWidget(self.start_service_btn)

        self.stop_service_btn = ModernButton(t("mcp_stop"), "red")
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
        services_group = QGroupBox(t("connected_services"))
        self._services_group = services_group
        services_layout = QVBoxLayout(services_group)
        services_layout.setSpacing(6)
        services_layout.setContentsMargins(10, 12, 10, 10)

        # Stili pulsanti servizi
        self._svc_btn_style_off = "font-size: 10px; padding: 2px 6px; background: #27ae60; color: white; border-radius: 3px;"
        self._svc_btn_style_on = "font-size: 10px; padding: 2px 6px; background: #e74c3c; color: white; border-radius: 3px;"
        self._svc_btn_style_checking = "font-size: 10px; padding: 2px 6px; background: #f39c12; color: white; border-radius: 3px;"

        # Mappa servizi: (label, porta, url health check)
        self._sub_services = {
            "tts": {"label": "TTS", "icon": "🔊", "port": PORT_TTS, "url": URL_TTS + "/"},
            "image": {"label": "Image", "icon": "🖼️", "port": PORT_IMAGE, "url": URL_IMAGE + "/"},
            "document": {"label": "Document", "icon": "📄", "port": PORT_DOCUMENT, "url": URL_DOCUMENT + "/"},
        }
        self._svc_running = {"tts": False, "image": False, "document": False}

        # TTS Service
        tts_row = QHBoxLayout()
        self.tts_status = QLabel("●")
        self.tts_status.setFixedWidth(14)
        self.tts_status.setStyleSheet("color: #bdc3c7;")
        tts_row.addWidget(self.tts_status)
        self.tts_label = QLabel(f"🔊 <b>TTS</b> :{PORT_TTS}")
        tts_row.addWidget(self.tts_label)
        tts_row.addStretch()
        self.tts_start_btn = QPushButton(t("mcp_checking_btn"))
        self.tts_start_btn.setFixedWidth(80)
        self.tts_start_btn.setStyleSheet(self._svc_btn_style_checking)
        self.tts_start_btn.clicked.connect(lambda: self._toggle_sub_service("tts"))
        tts_row.addWidget(self.tts_start_btn)
        services_layout.addLayout(tts_row)

        # Image Service
        img_row = QHBoxLayout()
        self.img_status = QLabel("●")
        self.img_status.setFixedWidth(14)
        self.img_status.setStyleSheet("color: #bdc3c7;")
        img_row.addWidget(self.img_status)
        self.img_label = QLabel(f"🖼️ <b>Image</b> :{PORT_IMAGE}")
        img_row.addWidget(self.img_label)
        img_row.addStretch()
        self.img_start_btn = QPushButton(t("mcp_checking_btn"))
        self.img_start_btn.setFixedWidth(80)
        self.img_start_btn.setStyleSheet(self._svc_btn_style_checking)
        self.img_start_btn.clicked.connect(lambda: self._toggle_sub_service("image"))
        img_row.addWidget(self.img_start_btn)
        services_layout.addLayout(img_row)

        # Document Service
        doc_row = QHBoxLayout()
        self.doc_status = QLabel("●")
        self.doc_status.setFixedWidth(14)
        self.doc_status.setStyleSheet("color: #bdc3c7;")
        doc_row.addWidget(self.doc_status)
        self.doc_label = QLabel(f"📄 <b>Document</b> :{PORT_DOCUMENT}")
        doc_row.addWidget(self.doc_label)
        doc_row.addStretch()
        self.doc_start_btn = QPushButton(t("mcp_checking_btn"))
        self.doc_start_btn.setFixedWidth(80)
        self.doc_start_btn.setStyleSheet(self._svc_btn_style_checking)
        self.doc_start_btn.clicked.connect(lambda: self._toggle_sub_service("document"))
        doc_row.addWidget(self.doc_start_btn)
        services_layout.addLayout(doc_row)

        # Pulsante avvia tutti i servizi
        start_all_btn = ModernButton(t("start_all_services"), "blue")
        self._btn_start_all = start_all_btn
        start_all_btn.setToolTip(t("mcp_start_all_tooltip"))
        start_all_btn.clicked.connect(self._start_all_sub_services)
        services_layout.addWidget(start_all_btn)

        services_layout.addStretch()
        row3.addWidget(services_group, 1)

        # === COLONNA DESTRA: Tools + LAN ===
        right_col = QVBoxLayout()
        right_col.setSpacing(10)

        # Tools MCP
        tools_group = QGroupBox(t("mcp_tools_title"))
        self._tools_group = tools_group
        tools_layout = QVBoxLayout(tools_group)
        tools_layout.setSpacing(4)
        tools_layout.setContentsMargins(10, 12, 10, 10)

        self.tools_list = QTextEdit()
        self.tools_list.setReadOnly(True)
        self.tools_list.setMaximumHeight(80)
        self.tools_list.setStyleSheet("font-size: 10px; font-family: 'DejaVu Sans Mono';")
        self.tools_list.setPlainText(t("mcp_tools_placeholder"))
        tools_layout.addWidget(self.tools_list)
        right_col.addWidget(tools_group)

        # Accesso LAN
        lan_group = QGroupBox(t("lan_access_mcp"))
        self._lan_group = lan_group
        lan_layout = QVBoxLayout(lan_group)
        lan_layout.setSpacing(4)
        lan_layout.setContentsMargins(10, 12, 10, 10)

        lan_info = QLabel(
            f"<b>Locale:</b> <code>http://localhost:{PORT_MCP}</code><br>"
            f"<b>LAN:</b> <code>http://{self.local_ip}:{PORT_MCP}</code>"
        )
        lan_info.setStyleSheet("font-size: 10px;")
        lan_info.setTextInteractionFlags(Qt.TextSelectableByMouse)
        lan_layout.addWidget(lan_info)

        lan_buttons = QHBoxLayout()
        self._btn_copy_url = ModernButton(t("copy_url"), "blue")
        copy_btn = self._btn_copy_url
        copy_btn.clicked.connect(lambda: self._copy_to_clipboard(f"http://{self.local_ip}:{PORT_MCP}"))
        lan_buttons.addWidget(copy_btn)

        self._btn_docs = ModernButton("📚 Docs", "purple")
        docs_btn = self._btn_docs
        docs_btn.clicked.connect(lambda: webbrowser.open(f"{self.mcp_service_url}/docs"))
        lan_buttons.addWidget(docs_btn)
        lan_layout.addLayout(lan_buttons)

        right_col.addWidget(lan_group)
        row3.addLayout(right_col, 2)

        layout.addLayout(row3)

        # ╔════════════════════════════════════════════════════════════╗
        # ║  RIGA 4: Test Rapidi                                      ║
        # ╚════════════════════════════════════════════════════════════╝
        test_group = QGroupBox(t("quick_tests"))
        self._tests_group = test_group
        test_main_layout = QVBoxLayout(test_group)
        test_main_layout.setSpacing(8)
        test_main_layout.setContentsMargins(10, 12, 10, 10)

        # Riga input testo
        text_row = QHBoxLayout()
        self._test_text_label = QLabel(t("mcp_test_text_label"))
        text_row.addWidget(self._test_text_label)
        self.test_text_input = QLineEdit(t("mcp_test_input_default"))
        self.test_text_input.setPlaceholderText(t("mcp_test_input_placeholder"))
        text_row.addWidget(self.test_text_input, 1)
        test_main_layout.addLayout(text_row)

        # Riga pulsanti test
        test_buttons = QHBoxLayout()
        test_buttons.setSpacing(8)

        test_tts_btn = ModernButton(t("test_tts_btn"), "green")
        self._btn_test_tts = test_tts_btn
        test_tts_btn.clicked.connect(self.run_test_tts)
        test_buttons.addWidget(test_tts_btn)

        test_services_btn = ModernButton(t("check_services_btn"), "blue")
        self._btn_check_services = test_services_btn
        test_services_btn.clicked.connect(self.run_test_services)
        test_buttons.addWidget(test_services_btn)

        self._btn_open_swagger = ModernButton(t("open_swagger"), "purple")
        self._btn_open_swagger.clicked.connect(lambda: webbrowser.open(f"{self.mcp_service_url}/docs"))
        test_buttons.addWidget(self._btn_open_swagger)

        test_buttons.addStretch()
        test_main_layout.addLayout(test_buttons)

        # Area risultato test
        self.test_result = QTextEdit()
        self.test_result.setReadOnly(True)
        self.test_result.setMaximumHeight(60)
        self.test_result.setStyleSheet("font-size: 10px; font-family: 'DejaVu Sans Mono'; background-color: #f8f9fa;")
        self.test_result.setPlaceholderText(t("mcp_test_results_placeholder"))
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
            self.ram_label.setText(get_text("mcp_ram_error", self._get_lang(), error=e))
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
            self.vram_label.setText(get_text("mcp_no_gpu", self._get_lang()))
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
        lang = self._get_lang()
        msg.setWindowTitle(get_text("mcp_confirm_title", lang))
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
        msg.setText(get_text("mcp_confirm_question", lang))
        msg.setInformativeText(f"Livello di rischio: <b style='color: {color};'>{risk_level}</b>")
        msg.setDetailedText(f"Risorse rilevate:\n- RAM libera: {getattr(self, 'avail_ram', 0):.1f} GB\n- VRAM libera: {getattr(self, 'free_vram', 0):.1f} GB\n\n{risk_text}")

        # Pulsanti
        if risk_level == "CRITICO":
            msg.setStandardButtons(QMessageBox.Cancel)
            force_btn = msg.addButton(get_text("mcp_force_start", lang), QMessageBox.AcceptRole)
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
            self.status_label.setText(get_text("mcp_starting", self._get_lang()))
            self.status_indicator.setStyleSheet("color: #f39c12;")

            # Avvia timer per check stato (solo dopo avvio manuale)
            if not hasattr(self, 'check_timer') or not self.check_timer.isActive():
                self.check_timer = QTimer()
                self.check_timer.timeout.connect(self.check_service_status)
                self.check_timer.start(5000)

            QTimer.singleShot(3000, self.check_service_status)
        except Exception as e:
            lang = self._get_lang()
            QMessageBox.warning(self, get_text("mcp_start_error", lang),
                f"{get_text('mcp_start_error_msg', lang, error=e)}\n\n"
                f"{get_text('mcp_start_suggestion', lang, port=PORT_MCP)}")

    def stop_mcp_service(self):
        """Ferma il servizio MCP."""
        try:
            # Trova e termina il processo
            if IS_WINDOWS:
                subprocess.run(["taskkill", "/f", "/im", "python.exe", "/fi", "WINDOWTITLE eq MCP*"],
                              capture_output=True)
            else:
                subprocess.run(["pkill", "-f", "mcp_service.py"], capture_output=True)

            lang = self._get_lang()
            self.status_label.setText(get_text("mcp_stopped", lang))
            self.status_indicator.setStyleSheet("color: #bdc3c7;")
            self.stop_service_btn.setEnabled(False)
            self.start_service_btn.setEnabled(True)

            # Ferma il timer
            if hasattr(self, 'check_timer'):
                self.check_timer.stop()

        except Exception as e:
            lang = self._get_lang()
            QMessageBox.warning(self, get_text("mcp_start_error", lang),
                f"{get_text('mcp_stop_error_msg', lang, error=e)}\n\n"
                f"{get_text('mcp_stop_manual', lang)}")

    def check_service_status(self):
        """Verifica lo stato di tutti i servizi in un thread separato (non blocca la GUI)."""
        if hasattr(self, '_status_checking') and self._status_checking:
            return  # Evita check sovrapposti
        self._status_checking = True

        import threading

        def _do_check():
            import requests as req
            results = {"mcp": False, "mcp_data": None, "tools": [], "services": {}}

            # Check MCP
            try:
                resp = req.get(self.mcp_service_url, timeout=2)
                if resp.status_code == 200:
                    results["mcp"] = True
                    results["mcp_data"] = resp.json()
            except (req.RequestException, ValueError):
                pass

            # Check tools (solo se MCP attivo)
            if results["mcp"]:
                try:
                    resp = req.get(f"{self.mcp_service_url}/tools", timeout=2)
                    if resp.status_code == 200:
                        results["tools"] = resp.json().get("tools", [])
                except (req.RequestException, ValueError):
                    pass

            # Check sotto-servizi direttamente
            for svc_name, svc_info in self._sub_services.items():
                try:
                    resp = req.get(svc_info["url"], timeout=1)
                    results["services"][svc_name] = resp.status_code == 200
                except req.RequestException:
                    results["services"][svc_name] = False

            # Aggiorna la UI dal thread principale via QTimer
            QTimer.singleShot(0, lambda: self._apply_status_results(results))

        threading.Thread(target=_do_check, daemon=True).start()

    def _apply_status_results(self, results):
        """Applica i risultati del check alla UI (chiamato nel thread principale)."""
        self._status_checking = False

        # Aggiorna stato MCP
        lang = self._get_lang()
        if results["mcp"] and results["mcp_data"]:
            data = results["mcp_data"]
            self.status_indicator.setStyleSheet("color: #27ae60;")
            self.status_label.setText(get_text("mcp_active", lang, count=data.get('tools_count', 0)))
            self.start_service_btn.setEnabled(False)
            self.stop_service_btn.setEnabled(True)
        else:
            self.status_indicator.setStyleSheet("color: #bdc3c7;")
            self.status_label.setText(get_text("mcp_not_active", lang))
            self.start_service_btn.setEnabled(True)
            self.stop_service_btn.setEnabled(False)

        # Aggiorna tools
        if results["tools"]:
            text = "\n".join([f"• {tool['name']}: {tool['description']}" for tool in results["tools"]])
            self.tools_list.setPlainText(text)
        elif results["mcp"]:
            self.tools_list.setPlainText(get_text("mcp_no_tools", lang))

        # Aggiorna sotto-servizi
        for svc_name, is_running in results["services"].items():
            self._svc_running[svc_name] = is_running
            self._update_svc_button(svc_name, is_running)

    def _copy_to_clipboard(self, text):
        """Copia testo negli appunti."""
        from PyQt5.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        clipboard.setText(text)
        lang = self._get_lang()
        QMessageBox.information(self, get_text("info", lang), get_text("copied_clipboard", lang, text=text))

    def _get_svc_button(self, service_name):
        """Restituisce il pulsante e l'indicatore per un servizio."""
        mapping = {
            "tts": (self.tts_start_btn, self.tts_status, self.tts_label),
            "image": (self.img_start_btn, self.img_status, self.img_label),
            "document": (self.doc_start_btn, self.doc_status, self.doc_label),
        }
        return mapping.get(service_name, (None, None, None))

    def _check_sub_service_direct(self, service_name):
        """Verifica direttamente se un servizio e' attivo (senza passare da MCP)."""
        svc_info = self._sub_services.get(service_name)
        if not svc_info:
            return False
        try:
            import requests
            resp = requests.get(svc_info["url"], timeout=1)
            return resp.status_code == 200
        except (requests.RequestException, ImportError):
            return False

    def _update_svc_button(self, service_name, is_running):
        """Aggiorna testo e stile del pulsante in base allo stato."""
        btn, indicator, label = self._get_svc_button(service_name)
        if not btn:
            return
        self._svc_running[service_name] = is_running
        svc_info = self._sub_services[service_name]
        lang = self._get_lang()
        if is_running:
            btn.setText(get_text("mcp_stop_svc_btn", lang))
            btn.setStyleSheet(self._svc_btn_style_on)
            indicator.setStyleSheet("color: #27ae60;")
            label.setText(f"{svc_info['icon']} <b>{svc_info['label']}</b> :{svc_info['port']} - <span style='color:#27ae60;'>Attivo</span>")
        else:
            btn.setText(get_text("mcp_start_svc_btn", lang))
            btn.setStyleSheet(self._svc_btn_style_off)
            indicator.setStyleSheet("color: #bdc3c7;")
            label.setText(f"{svc_info['icon']} <b>{svc_info['label']}</b> :{svc_info['port']}")

    def _toggle_sub_service(self, service_name):
        """Avvia o ferma un servizio in base allo stato attuale."""
        is_running = self._check_sub_service_direct(service_name)
        if is_running:
            self._stop_sub_service(service_name)
        else:
            self._start_sub_service(service_name)

    def _start_sub_service(self, service_name):
        """Avvia un singolo servizio (tts, image, document)."""
        # Prima controlla se gia' attivo
        if self._check_sub_service_direct(service_name):
            self._update_svc_button(service_name, True)
            self.status_label.setText(get_text("mcp_already_active", self._get_lang(), service=service_name.upper()))
            return

        service_scripts = {
            "tts": ("tts_service/tts_local.py", PORT_TTS),
            "image": ("image_analysis/image_service.py", PORT_IMAGE),
            "document": ("document_service/document_service.py", PORT_DOCUMENT),
        }
        script, port = service_scripts.get(service_name, (None, None))
        if not script:
            return

        script_path = SCRIPT_DIR / script
        if not script_path.exists():
            lang = self._get_lang()
            QMessageBox.warning(self, get_text("error", lang), get_text("mcp_file_not_found", lang, file=script))
            return

        btn, _, _ = self._get_svc_button(service_name)
        if btn:
            btn.setText(get_text("mcp_starting_btn", self._get_lang()))
            btn.setStyleSheet(self._svc_btn_style_checking)
            btn.setEnabled(False)

        try:
            if IS_WINDOWS:
                subprocess.Popen(
                    ['cmd', '/c', 'start', service_name, 'python', str(script_path)],
                    cwd=SCRIPT_DIR
                )
            else:
                subprocess.Popen(
                    ['python3', str(script_path)],
                    cwd=SCRIPT_DIR,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            self.status_label.setText(get_text("mcp_starting_service", self._get_lang(), service=service_name))
            # Ricontrolla dopo 3 secondi
            QTimer.singleShot(3000, lambda: self._verify_after_start(service_name))
        except Exception as e:
            if btn:
                btn.setEnabled(True)
            self._update_svc_button(service_name, False)
            svc_info = self._sub_services.get(service_name, {})
            port = svc_info.get("port", "?")
            lang = self._get_lang()
            QMessageBox.warning(self, get_text("mcp_start_error", lang),
                f"{get_text('mcp_start_error_msg', lang, error=e)}\n\n"
                f"{get_text('mcp_port_suggestion', lang, port=port)}")

    def _verify_after_start(self, service_name):
        """Verifica se il servizio e' partito dopo l'avvio."""
        btn, _, _ = self._get_svc_button(service_name)
        if btn:
            btn.setEnabled(True)
        is_running = self._check_sub_service_direct(service_name)
        self._update_svc_button(service_name, is_running)
        lang = self._get_lang()
        if is_running:
            self.status_label.setText(get_text("mcp_service_started", lang, service=service_name.upper()))
        else:
            self.status_label.setText(get_text("mcp_service_not_responding", lang, service=service_name.upper()))
        self.check_service_status()

    def _stop_sub_service(self, service_name):
        """Ferma un singolo servizio."""
        svc_info = self._sub_services.get(service_name)
        if not svc_info:
            return
        port = svc_info["port"]
        try:
            if IS_WINDOWS:
                subprocess.run(
                    ["powershell", "-Command",
                     f"Get-NetTCPConnection -LocalPort {port} -ErrorAction SilentlyContinue | "
                     f"ForEach-Object {{ Stop-Process -Id $_.OwningProcess -Force }}"],
                    capture_output=True, timeout=5
                )
            else:
                subprocess.run(
                    ["fuser", "-k", f"{port}/tcp"],
                    capture_output=True, timeout=5
                )
            self.status_label.setText(get_text("mcp_service_stopped", self._get_lang(), service=service_name.upper()))
        except Exception as e:
            self.status_label.setText(get_text("mcp_error_stopping", self._get_lang(), service=service_name, error=e))
        # Ricontrolla dopo 1 secondo
        QTimer.singleShot(1000, lambda: self._update_svc_button(
            service_name, self._check_sub_service_direct(service_name)))

    def _start_all_sub_services(self):
        """Avvia tutti i servizi non ancora attivi."""
        started = 0
        for svc in ["tts", "image", "document"]:
            if not self._check_sub_service_direct(svc):
                self._start_sub_service(svc)
                started += 1
        lang = self._get_lang()
        if started == 0:
            self.status_label.setText(get_text("mcp_all_active", lang))
        else:
            self.status_label.setText(get_text("mcp_starting_n", lang, count=started))
            QTimer.singleShot(5000, self.check_service_status)

    def run_test_tts(self):
        """Esegue test TTS via MCP Bridge."""
        text = self.test_text_input.text().strip()
        if not text:
            text = "Ciao, questo è un test!"
            self.test_text_input.setText(text)

        QApplication.setOverrideCursor(Qt.WaitCursor)
        self.test_result.setPlainText(get_text("mcp_test_running", self._get_lang()))

        try:
            import requests
            resp = requests.post(
                f"{self.mcp_service_url}/test/tts",
                params={"text": text},
                timeout=30
            )
            data = resp.json()

            if data.get("success"):
                lang = self._get_lang()
                result = get_text("mcp_test_tts_ok", lang,
                    voice=data.get('voice', 'N/A'),
                    size=data.get('audio_size', 0),
                    path=data.get('audio_path', 'N/A'))
                self.test_result.setPlainText(result)

                # Prova a riprodurre l'audio
                audio_path = data.get('audio_path')
                if audio_path and os.path.exists(audio_path):
                    if IS_WINDOWS:
                        os.startfile(audio_path)
                    else:
                        subprocess.Popen(["xdg-open", audio_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            else:
                self.test_result.setPlainText(f"❌ {get_text('error', self._get_lang())} TTS:\n{data.get('error', '?')}")

        except requests.exceptions.ConnectionError:
            self.test_result.setPlainText(get_text("mcp_service_unreachable", self._get_lang()))
        except Exception as e:
            self.test_result.setPlainText(f"❌ {get_text('error', self._get_lang())}: {e}")
        finally:
            QApplication.restoreOverrideCursor()

    def run_test_services(self):
        """Verifica stato di tutti i servizi."""
        self.test_result.setPlainText(get_text("mcp_test_checking", self._get_lang()))

        try:
            import requests
            resp = requests.get(f"{self.mcp_service_url}/services", timeout=5)
            data = resp.json()

            lines = [get_text("mcp_services_status", self._get_lang())]
            for name, info in data.items():
                status = "✅" if info.get("available") else "❌"
                port = info.get("port", "?")
                lines.append(f"{status} {name.upper()}: porta {port}")

            self.test_result.setPlainText("\n".join(lines))

        except requests.exceptions.ConnectionError:
            self.test_result.setPlainText(get_text("mcp_service_unreachable", self._get_lang()))
        except Exception as e:
            self.test_result.setPlainText(f"❌ {get_text('error', self._get_lang())}: {e}")

    def open_readme(self):
        """Apre il README del servizio MCP."""
        readme_path = SCRIPT_DIR / "mcp_service" / "README.md"
        if readme_path.exists():
            if IS_WINDOWS:
                os.startfile(str(readme_path))
            else:
                subprocess.run(["xdg-open", str(readme_path)])
        else:
            lang = self._get_lang()
            QMessageBox.warning(self, get_text("error", lang), get_text("mcp_readme_not_found", lang))

    def retranslate_ui(self, lang):
        t = lambda key, **kw: get_text(key, lang, **kw)
        self._resources_group.setTitle(t("mcp_resources"))
        self._mcp_group.setTitle(t("mcp_service_title"))
        self._services_group.setTitle(t("connected_services"))
        self._tools_group.setTitle(t("mcp_tools_title"))
        self._lan_group.setTitle(t("lan_access_mcp"))
        self._tests_group.setTitle(t("quick_tests"))
        self.start_service_btn.setText(t("mcp_start"))
        self.stop_service_btn.setText(t("mcp_stop"))
        self._btn_start_all.setText(t("start_all_services"))
        self._btn_start_all.setToolTip(t("mcp_start_all_tooltip"))
        self._btn_test_tts.setText(t("test_tts_btn"))
        self._btn_check_services.setText(t("check_services_btn"))
        self._btn_open_swagger.setText(t("open_swagger"))
        self._btn_copy_url.setText(t("copy_url"))
        self._test_text_label.setText(t("mcp_test_text_label"))
        self.test_text_input.setPlaceholderText(t("mcp_test_input_placeholder"))
        self.test_result.setPlaceholderText(t("mcp_test_results_placeholder"))
        # Aggiorna stato servizi per riflettere la lingua
        self.check_service_status()
