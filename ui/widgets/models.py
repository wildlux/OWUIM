"""
Models Widget - Gestione modelli Ollama.
"""
import subprocess
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGroupBox,
    QListWidget, QListWidgetItem, QComboBox, QFrame,
    QTableWidget, QTableWidgetItem, QHeaderView, QMenu,
    QPushButton, QMessageBox, QApplication
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QColor
from config import SCRIPT_DIR
from ui.components import ModernButton

try:
    from translations import get_text
except ImportError:
    def get_text(key, lang="it", **kwargs): return key


class ModelsWidget(QWidget):
    """Widget per gestire i modelli"""
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
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        lang = self._get_lang()
        t = lambda key, **kw: get_text(key, lang, **kw)

        # Layout a due colonne
        columns = QHBoxLayout()
        columns.setSpacing(12)

        # === COLONNA SINISTRA: Modelli Installati ===
        left_col = QVBoxLayout()
        left_col.setSpacing(8)

        models_group = QGroupBox(t("installed_models"))
        self._installed_group = models_group
        models_layout = QVBoxLayout(models_group)
        models_layout.setContentsMargins(10, 12, 10, 10)

        self.models_list = QListWidget()
        self.models_list.setFont(QFont("DejaVu Sans Mono", 10))
        self.models_list.setStyleSheet("QListWidget::item { padding: 4px; }")
        # H7.2 - Menu contestuale right-click
        self.models_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.models_list.customContextMenuRequested.connect(self._models_context_menu)
        models_layout.addWidget(self.models_list)

        btn_refresh = ModernButton(t("refresh_models"), "blue")
        self._btn_refresh = btn_refresh
        btn_refresh.clicked.connect(self.refresh_models)
        models_layout.addWidget(btn_refresh)

        left_col.addWidget(models_group)
        columns.addLayout(left_col, 1)

        # === COLONNA DESTRA: Modelli Consigliati + Azioni ===
        right_col = QVBoxLayout()
        right_col.setSpacing(8)

        recommend_group = QGroupBox(t("recommended_models"))
        self._recommended_group = recommend_group
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
                    font-size: 10px; text-align: left; padding: 2px 4px;
                    background: transparent; border: none; color: #2980b9;
                }
                QPushButton:hover { text-decoration: underline; background: #ecf0f1; }
            """)
            model_btn.setCursor(Qt.PointingHandCursor)
            model_btn.setToolTip(t("download_tooltip", model=model))
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
        note_label = QLabel(t("models_note"))
        self._note_label = note_label
        note_label.setStyleSheet("font-size: 10px; color: #7f8c8d;")
        note_label.setWordWrap(True)
        recommend_layout.addWidget(note_label)

        links_label = QLabel(t("models_links"))
        self._links_label = links_label
        links_label.setOpenExternalLinks(True)
        links_label.setStyleSheet("font-size: 10px; color: #7f8c8d;")
        recommend_layout.addWidget(links_label)

        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("background-color: #ddd;")
        recommend_layout.addWidget(sep)

        # === AZIONI (dentro Modelli Consigliati) ===
        actions_label = QLabel(f"<b>{t('manual_actions')}</b>")
        self._manual_label = actions_label
        actions_label.setStyleSheet("font-size: 10px; color: #2980b9;")
        recommend_layout.addWidget(actions_label)

        # Download manuale
        download_row = QHBoxLayout()
        download_row.setSpacing(6)
        self.model_combo = QComboBox()
        self.model_combo.setFont(QFont("Arial", 10))
        self.model_combo.setEditable(True)
        self.model_combo.setPlaceholderText(t("download_placeholder"))
        download_row.addWidget(self.model_combo, 1)
        btn_download = ModernButton(t("download_button"), "green")
        self._btn_download = btn_download
        btn_download.clicked.connect(self.download_model)
        download_row.addWidget(btn_download)
        recommend_layout.addLayout(download_row)

        # Rimuovi (combobox con modelli installati)
        remove_row = QHBoxLayout()
        remove_row.setSpacing(6)
        self.remove_combo = QComboBox()
        self.remove_combo.setFont(QFont("Arial", 10))
        self.remove_combo.setPlaceholderText(t("remove_placeholder"))
        remove_row.addWidget(self.remove_combo, 1)
        btn_remove = ModernButton(t("remove_button"), "red")
        self._btn_remove = btn_remove
        btn_remove.clicked.connect(self.remove_model)
        remove_row.addWidget(btn_remove)
        recommend_layout.addLayout(remove_row)

        right_col.addWidget(recommend_group)
        columns.addLayout(right_col, 1)

        layout.addLayout(columns, 1)

        # Carica modelli all'avvio
        self.refresh_models()

    def _models_context_menu(self, pos):
        """H7.2 - Menu contestuale per lista modelli"""
        item = self.models_list.itemAt(pos)
        if not item:
            return
        model_name = item.text().split()[0] if item.text().split() else ""
        if not model_name:
            return

        lang = self._get_lang()
        t = lambda key, **kw: get_text(key, lang, **kw)

        menu = QMenu(self)
        copy_action = menu.addAction(t("copy_name"))
        menu.addSeparator()
        remove_action = menu.addAction(t("remove_model"))

        action = menu.exec_(self.models_list.mapToGlobal(pos))
        if action == copy_action:
            QApplication.clipboard().setText(model_name)
            self.main_window.statusBar().showMessage(t("copied_msg", text=model_name), 2000)
        elif action == remove_action:
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle(t("confirm_remove_title"))
            msg.setText(t("confirm_remove_detail", model=model_name))
            msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            msg.setDefaultButton(QMessageBox.No)
            msg.button(QMessageBox.Yes).setText(t("remove_action"))
            msg.button(QMessageBox.No).setText(t("cancel"))
            if msg.exec_() == QMessageBox.Yes:
                self.main_window.run_command(
                    f"ollama rm {model_name} 2>/dev/null || docker exec ollama ollama rm {model_name}",
                    t("removing_model", model=model_name)
                )
                QTimer.singleShot(2000, self.refresh_models)

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
        if not model:
            # H3.3 - Validazione: campo vuoto
            self.model_combo.setStyleSheet("border: 2px solid #e74c3c; border-radius: 6px; padding: 8px;")
            self.main_window.statusBar().showMessage(get_text("enter_model_name", self._get_lang()), 3000)
            QTimer.singleShot(2000, lambda: self.model_combo.setStyleSheet(""))
            return
        self.main_window.run_command(
            f"ollama pull {model} 2>/dev/null || docker exec -it ollama ollama pull {model}",
            get_text("downloading_model", self._get_lang(), model=model)
        )

    def quick_download(self, model):
        """Scarica un modello dalla lista consigliati"""
        # H5.3 - Anti doppio click: disabilita il pulsante cliccato
        sender = self.sender()
        if sender and isinstance(sender, QPushButton):
            sender.setEnabled(False)
            sender.setText("...")
        self.main_window.run_command(
            f"ollama pull {model} 2>/dev/null || docker exec -it ollama ollama pull {model}",
            get_text("downloading_model", self._get_lang(), model=model)
        )

    def remove_model(self):
        model = self.remove_combo.currentText().strip()
        if model:
            # Cerca dimensione modello dalla lista installati
            model_size = ""
            for i in range(self.models_list.count()):
                line = self.models_list.item(i).text()
                if line.startswith(model):
                    parts = line.split()
                    # Formato: NAME ID SIZE MODIFIED
                    for j, part in enumerate(parts):
                        if part.endswith("GB") or part.endswith("MB"):
                            model_size = f"\nDimensione: {part}"
                            break
                    break

            lang = self._get_lang()
            t = lambda key, **kw: get_text(key, lang, **kw)

            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle(t("confirm_remove_full_title"))
            msg.setText(t("confirm_remove_detail", model=model) + model_size)
            msg.setInformativeText(t("confirm_remove_full_detail"))
            msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            msg.setDefaultButton(QMessageBox.No)
            msg.button(QMessageBox.Yes).setText(t("remove_action"))
            msg.button(QMessageBox.No).setText(t("cancel"))

            if msg.exec_() == QMessageBox.Yes:
                self.main_window.run_command(
                    f"ollama rm {model} 2>/dev/null || docker exec ollama ollama rm {model}",
                    t("removing_model", model=model)
                )
                QTimer.singleShot(2000, self.refresh_models)

    def retranslate_ui(self, lang):
        t = lambda key, **kw: get_text(key, lang, **kw)
        self._installed_group.setTitle(t("installed_models"))
        self._recommended_group.setTitle(t("recommended_models"))
        self._btn_download.setText(t("download_button"))
        self._btn_remove.setText(t("remove_button"))
        self._btn_refresh.setText(t("refresh_models"))
        self._manual_label.setText(f"<b>{t('manual_actions')}</b>")
        self.model_combo.setPlaceholderText(t("download_placeholder"))
        self.remove_combo.setPlaceholderText(t("remove_placeholder"))
        self._note_label.setText(t("models_note"))
        self._links_label.setText(t("models_links"))
