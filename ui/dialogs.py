"""
Dialog dell'applicazione.
"""

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QProgressBar, QPushButton
from PyQt5.QtCore import Qt, QTimer, QSettings
from PyQt5.QtGui import QFont

from ui.threads import StartupThread

try:
    from translations import get_text
except ImportError:
    def get_text(key, lang="it", **kwargs): return key


class StartupDialog(QDialog):
    """Dialog di avvio con progress bar."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._lang = QSettings("OpenWebUI", "Manager").value("language", "it")
        t = lambda key, **kw: get_text(key, self._lang, **kw)

        self.setWindowTitle(t("window_title"))
        self.setFixedSize(400, 200)
        self.setWindowFlags(Qt.Dialog | Qt.CustomizeWindowHint | Qt.WindowTitleHint)

        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        # Titolo
        title = QLabel(t("startup_title"))
        title.setFont(QFont("Arial", 12, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Status
        self.status_label = QLabel(t("startup_status"))
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

        # Pulsante skip
        self.skip_btn = QPushButton(t("skip_button"))
        self.skip_btn.setVisible(False)
        self.skip_btn.clicked.connect(self.accept)
        layout.addWidget(self.skip_btn)

        layout.addStretch()

        # Thread di avvio
        self.startup_thread = StartupThread(lang=self._lang)
        self.startup_thread.progress_signal.connect(self._update_progress)
        self.startup_thread.finished_signal.connect(self._startup_finished)

        # Mostra pulsante skip dopo 10 secondi
        QTimer.singleShot(10000, lambda: self.skip_btn.setVisible(True))

    def start(self):
        self.startup_thread.start()

    def _update_progress(self, message, percent):
        self.status_label.setText(message)
        self.progress.setValue(percent)

    def _startup_finished(self, success, message):
        if success:
            self.accept()
        else:
            t = lambda key, **kw: get_text(key, self._lang, **kw)
            self.skip_btn.setVisible(True)
            self.skip_btn.setText(t("continue_anyway"))
            self.status_label.setText(f"{t('startup_warning')}: {message}")
            self.status_label.setStyleSheet("color: #e74c3c;")
