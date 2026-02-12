"""
Componenti UI riutilizzabili.

Principi applicati:
- SRP: Ogni componente ha una responsabilita'
- OCP: Estendibili tramite parametri, non modifica
"""

from PyQt5.QtWidgets import QPushButton, QFrame, QHBoxLayout, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

try:
    from translations import get_text
except ImportError:
    def get_text(key, lang="it", **kwargs): return key


class ModernButton(QPushButton):
    """Pulsante con stile moderno e colori predefiniti."""

    COLORS = {
        "blue": ("#3498db", "#2980b9"),
        "green": ("#27ae60", "#1e8449"),
        "red": ("#e74c3c", "#c0392b"),
        "orange": ("#f39c12", "#d68910"),
        "purple": ("#9b59b6", "#8e44ad"),
        "gray": ("#6c7a89", "#566573"),
    }

    def __init__(self, text, color="blue", parent=None, compact=False):
        super().__init__(text, parent)
        self.setCursor(Qt.PointingHandCursor)

        bg, hover = self.COLORS.get(color, self.COLORS["blue"])

        if compact:
            self.setMinimumHeight(28)
            padding = "4px 10px"
            font_size = "11px"
        else:
            self.setMinimumHeight(40)
            padding = "10px 20px"
            font_size = "14px"

        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg};
                color: white;
                border: none;
                border-radius: 6px;
                padding: {padding};
                font-size: {font_size};
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
                color: #7f8c8d;
            }}
        """)


class StatusIndicator(QFrame):
    """Indicatore di stato con pallino colorato."""

    def __init__(self, name, parent=None):
        super().__init__(parent)
        self._lang = "it"
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)

        self.indicator = QLabel("\u25cf")
        self.indicator.setFont(QFont("Arial", 16))
        self.label = QLabel(name)
        self.label.setFont(QFont("Arial", 12))
        self.status_label = QLabel(get_text("verifying", self._lang))
        self.status_label.setFont(QFont("Arial", 11))
        self.status_label.setStyleSheet("color: #7f8c8d;")

        layout.addWidget(self.indicator)
        layout.addWidget(self.label)
        layout.addStretch()
        layout.addWidget(self.status_label)

        self._current_status = None
        self.set_status(None)

    def set_status(self, active):
        self._current_status = active
        if active is None:
            self.indicator.setStyleSheet("color: #f39c12;")
            self.status_label.setText(get_text("verifying", self._lang))
        elif active:
            self.indicator.setStyleSheet("color: #27ae60;")
            self.status_label.setText(get_text("active", self._lang))
        else:
            self.indicator.setStyleSheet("color: #e74c3c;")
            self.status_label.setText(get_text("inactive", self._lang))

    def set_lang(self, lang):
        self._lang = lang
        self.set_status(self._current_status)
