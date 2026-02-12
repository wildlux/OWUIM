"""
Logs Widget - Visualizzazione log dei container Docker.
"""

import subprocess
import platform as pf
import logging

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QApplication
from PyQt5.QtGui import QFont

from config import SCRIPT_DIR, DOCKER_COMPOSE
from ui.components import ModernButton

try:
    from translations import get_text
except ImportError:
    def get_text(key, lang="it", **kwargs): return key

import sys
sys.path.insert(0, str(SCRIPT_DIR / "scripts"))
try:
    from system_profiler import get_system_profile
    HAS_PROFILER = True
except ImportError:
    HAS_PROFILER = False

logger = logging.getLogger(__name__)


class LogsWidget(QWidget):
    """Widget per visualizzare i log."""

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

        title = QLabel(get_text("logs_title", self._get_lang()))
        title.setFont(QFont("Arial", 20, QFont.Bold))
        title.setStyleSheet("color: #2c3e50;")
        layout.addWidget(title)
        self._title = title

        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setFont(QFont("DejaVu Sans Mono", 10))
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

        btn_layout = QHBoxLayout()

        lang = self._get_lang()
        btn_refresh = ModernButton(get_text("refresh_logs", lang), "blue")
        btn_clear = ModernButton(get_text("clear_logs", lang), "gray")
        btn_follow = ModernButton(get_text("follow_logs", lang), "green")
        btn_copy_support = ModernButton(get_text("copy_for_support", lang), "purple", compact=True)

        self._btn_refresh = btn_refresh
        self._btn_clear = btn_clear
        self._btn_follow = btn_follow
        self._btn_copy = btn_copy_support

        btn_refresh.clicked.connect(self.refresh_logs)
        btn_clear.clicked.connect(self.clear_logs)
        btn_follow.clicked.connect(self.follow_logs)
        btn_copy_support.clicked.connect(self.copy_for_support)

        btn_layout.addWidget(btn_refresh)
        btn_layout.addWidget(btn_clear)
        btn_layout.addWidget(btn_follow)
        btn_layout.addWidget(btn_copy_support)
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
            self.log_area.setText(result.stdout or result.stderr or get_text("no_logs", self._get_lang()))
        except Exception as e:
            logger.error("Errore refresh log: %s", e)
            self.log_area.setText(f"Errore: {str(e)}")

    def follow_logs(self):
        self.main_window.run_command(
            f"{DOCKER_COMPOSE} logs -f --tail=50",
            "Caricamento log in tempo reale..."
        )

    def copy_for_support(self):
        """Copia log + info sistema formattato per issue GitHub."""
        log_text = self.log_area.toPlainText()
        last_lines = "\n".join(log_text.split("\n")[-50:]) if log_text else "(nessun log)"

        system_info = (
            f"**OS:** {pf.system()} {pf.release()}\n"
            f"**Python:** {pf.python_version()}\n"
        )
        if HAS_PROFILER:
            try:
                profile = get_system_profile()
                system_info += (
                    f"**RAM:** {profile.ram_available_gb:.1f}/{profile.ram_total_gb:.1f} GB\n"
                    f"**GPU:** {profile.gpu_name if profile.has_gpu else 'N/A'}\n"
                    f"**Tier:** {profile.tier.value}\n"
                )
            except Exception:
                pass

        clipboard_text = (
            f"## Info Sistema\n{system_info}\n"
            f"## Log (ultime 50 righe)\n```\n{last_lines}\n```\n"
        )

        clipboard = QApplication.clipboard()
        clipboard.setText(clipboard_text)
        self.main_window.statusBar().showMessage(get_text("log_copied", self._get_lang()), 3000)

    def retranslate_ui(self, lang):
        t = lambda key, **kw: get_text(key, lang, **kw)
        self._title.setText(t("logs_title"))
        self._btn_refresh.setText(t("refresh_logs"))
        self._btn_clear.setText(t("clear_logs"))
        self._btn_follow.setText(t("follow_logs"))
        self._btn_copy.setText(t("copy_for_support"))
