"""
Info Widget - Informazioni sul progetto.
"""
import webbrowser

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGroupBox, QPushButton
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

try:
    from translations import get_text
except ImportError:
    def get_text(key, lang="it", **kwargs): return key


class InfoWidget(QWidget):
    """Widget con informazioni sul progetto"""
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
        layout.setContentsMargins(30, 30, 30, 30)

        # Titolo
        title = QLabel("Open WebUI Manager")
        title.setFont(QFont("Arial", 20, QFont.Bold))
        title.setStyleSheet("color: #2c3e50;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Cosa fa
        desc_group = QGroupBox(get_text("about_program"))
        self._desc_group = desc_group
        desc_group.setFont(QFont("Arial", 12, QFont.Bold))
        desc_layout = QVBoxLayout(desc_group)
        desc_layout.setContentsMargins(15, 20, 15, 15)

        self._desc_info = QLabel(get_text("info_desc_html"))
        self._desc_info.setWordWrap(True)
        self._desc_info.setStyleSheet("font-size: 11px; line-height: 1.5;")
        desc_layout.addWidget(self._desc_info)
        layout.addWidget(desc_group)

        # Ringraziamenti (compatto, max 5 righe)
        thanks_group = QGroupBox(get_text("thanks"))
        self._thanks_group = thanks_group
        thanks_group.setFont(QFont("Arial", 12, QFont.Bold))
        thanks_layout = QVBoxLayout(thanks_group)
        thanks_layout.setContentsMargins(15, 20, 15, 15)

        self._thanks_info = QLabel(get_text("info_thanks_html"))
        self._thanks_info.setWordWrap(True)
        self._thanks_info.setAlignment(Qt.AlignCenter)
        self._thanks_info.setOpenExternalLinks(True)
        thanks_layout.addWidget(self._thanks_info)
        layout.addWidget(thanks_group)

        # === Scorciatoie Tastiera + Supporto (layout a due colonne) ===
        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(15)

        # Scorciatoie tastiera
        shortcuts_group = QGroupBox(get_text("shortcuts_title"))
        self._shortcuts_group = shortcuts_group
        shortcuts_group.setFont(QFont("Arial", 12, QFont.Bold))
        shortcuts_layout = QVBoxLayout(shortcuts_group)
        shortcuts_layout.setContentsMargins(15, 18, 15, 12)

        self._shortcuts_info = QLabel(get_text("info_shortcuts_html"))
        self._shortcuts_info.setWordWrap(True)
        shortcuts_layout.addWidget(self._shortcuts_info)
        bottom_row.addWidget(shortcuts_group, 1)

        # Supporto e segnalazioni
        support_group = QGroupBox(get_text("support_title", self._get_lang()))
        self._support_group = support_group
        support_group.setFont(QFont("Arial", 12, QFont.Bold))
        support_layout = QVBoxLayout(support_group)
        support_layout.setContentsMargins(15, 18, 15, 12)

        report_btn = QPushButton(get_text("report_issue", self._get_lang()))
        self._report_btn = report_btn
        report_btn.setStyleSheet(
            "font-size: 11px; padding: 8px 16px; background-color: #e74c3c; "
            "color: white; border-radius: 4px; font-weight: bold;")
        report_btn.setToolTip("Apri GitHub Issues per segnalare un bug o proporre un miglioramento")
        report_btn.clicked.connect(lambda: __import__('webbrowser').open("https://github.com/wildlux/OWUIM/issues"))
        support_layout.addWidget(report_btn)

        self._support_label = QLabel(
            f"<span style='font-size: 10px; color: #7f8c8d;'>"
            f"{get_text('support_desc', self._get_lang())}</span>")
        self._support_label.setWordWrap(True)
        support_layout.addWidget(self._support_label)

        bottom_row.addWidget(support_group, 1)

        layout.addLayout(bottom_row)
        layout.addStretch()

    def retranslate_ui(self, lang):
        t = lambda key, **kw: get_text(key, lang, **kw)
        self._desc_group.setTitle(t("about_program"))
        self._thanks_group.setTitle(t("thanks"))
        self._shortcuts_group.setTitle(t("shortcuts_title"))
        self._support_group.setTitle(t("support_title"))
        self._report_btn.setText(t("report_issue"))
        self._desc_info.setText(t("info_desc_html"))
        self._thanks_info.setText(t("info_thanks_html"))
        self._shortcuts_info.setText(t("info_shortcuts_html"))
        self._support_label.setText(
            f"<span style='font-size: 10px; color: #7f8c8d;'>"
            f"{t('support_desc')}</span>")
