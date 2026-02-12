"""
Archivio Widget - Gestione file locali per Open WebUI.
"""
import os
from pathlib import Path

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGroupBox,
    QGridLayout, QTreeView, QListWidget, QListWidgetItem,
    QLineEdit, QTextEdit, QFrame, QPushButton, QFileDialog,
    QMessageBox, QApplication, QAbstractItemView, QInputDialog
)
from PyQt5.QtCore import Qt, QSettings, QDir, QFileInfo, QUrl
from PyQt5.QtGui import QFont, QDesktopServices
from PyQt5.QtWidgets import QFileSystemModel

try:
    from translations import get_text
except ImportError:
    def get_text(key, lang="it", **kwargs): return key

from config import SCRIPT_DIR


class ArchivioWidget(QWidget):
    """Widget Archivio - Gestione file locali per Open WebUI"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        self.settings = QSettings("OpenWebUI", "Manager")
        self.current_path = None
        self.last_result = None
        self.setup_ui()
        self.load_settings()

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

        # === ESPLORA FILE ===
        browser_group = QGroupBox(t("archive_browse"))
        self._browse_group = browser_group
        browser_layout = QVBoxLayout(browser_group)
        browser_layout.setContentsMargins(10, 12, 10, 10)
        browser_layout.setSpacing(8)

        # Toolbar navigazione con percorso e preferiti
        nav_row = QHBoxLayout()
        nav_row.setSpacing(5)

        self.back_btn = QPushButton("◀")
        self.back_btn.setMaximumWidth(32)
        self.back_btn.setMinimumHeight(28)
        self.back_btn.setToolTip(t("back_tooltip"))
        self.back_btn.clicked.connect(self.go_back)
        nav_row.addWidget(self.back_btn)

        self.up_btn = QPushButton("▲")
        self.up_btn.setMaximumWidth(32)
        self.up_btn.setMinimumHeight(28)
        self.up_btn.setToolTip(t("up_tooltip"))
        self.up_btn.clicked.connect(self.go_up)
        nav_row.addWidget(self.up_btn)

        self.home_btn = QPushButton("⌂")
        self.home_btn.setMaximumWidth(32)
        self.home_btn.setMinimumHeight(28)
        self.home_btn.setToolTip(t("home_tooltip"))
        self.home_btn.clicked.connect(self.go_home)
        nav_row.addWidget(self.home_btn)

        self.refresh_btn = QPushButton("↻")
        self.refresh_btn.setMaximumWidth(32)
        self.refresh_btn.setMinimumHeight(28)
        self.refresh_btn.setToolTip(t("refresh_tooltip"))
        self.refresh_btn.clicked.connect(self.refresh_view)
        nav_row.addWidget(self.refresh_btn)

        # Percorso corrente
        self.path_label = QLineEdit()
        self.path_label.setReadOnly(True)
        self.path_label.setPlaceholderText(t("path_placeholder"))
        self.path_label.setStyleSheet("""
            QLineEdit {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 3px;
                padding: 4px 8px;
                font-family: 'DejaVu Sans Mono';
                font-size: 10px;
            }
        """)
        nav_row.addWidget(self.path_label, 1)

        # Pulsante preferiti (imposta cartella home)
        self.star_btn = QPushButton("⭐")
        self.star_btn.setMaximumWidth(32)
        self.star_btn.setMinimumHeight(28)
        self.star_btn.setToolTip(t("favorite_tooltip"))
        self.star_btn.clicked.connect(self.set_as_favorite)
        nav_row.addWidget(self.star_btn)

        # Pulsante sfoglia
        self.select_folder_btn = QPushButton("📁")
        self.select_folder_btn.setMaximumWidth(32)
        self.select_folder_btn.setMinimumHeight(28)
        self.select_folder_btn.setToolTip(t("browse_tooltip"))
        self.select_folder_btn.clicked.connect(self.select_private_folder)
        nav_row.addWidget(self.select_folder_btn)

        browser_layout.addLayout(nav_row)

        # Layout a due colonne: TreeView | Azioni + Risultato
        columns_layout = QHBoxLayout()
        columns_layout.setSpacing(10)

        # === COLONNA SINISTRA: File Manager ===
        self.file_model = QFileSystemModel()
        self.file_model.setRootPath("")
        self.file_model.setFilter(QDir.AllEntries | QDir.NoDotAndDotDot)

        self.tree_view = QTreeView()
        self.tree_view.setModel(self.file_model)
        self.tree_view.setAlternatingRowColors(True)
        self.tree_view.setSortingEnabled(True)
        self.tree_view.setSelectionMode(QAbstractItemView.SingleSelection)

        # Configura colonne
        self.tree_view.setColumnWidth(0, 200)
        self.tree_view.setColumnHidden(2, True)  # Tipo

        # Stile compatto
        self.tree_view.setStyleSheet("""
            QTreeView {
                border: 1px solid #bdc3c7;
                border-radius: 3px;
                background-color: white;
                font-size: 11px;
            }
            QTreeView::item {
                padding: 2px;
            }
            QTreeView::item:hover {
                background-color: #e8f4fc;
            }
            QTreeView::item:selected {
                background-color: #3498db;
                color: white;
            }
        """)

        self.tree_view.doubleClicked.connect(self.on_item_double_clicked)
        self.tree_view.clicked.connect(self.on_item_clicked)

        columns_layout.addWidget(self.tree_view, 1)

        # === COLONNA DESTRA: Info + Pulsanti + Risultato ===
        right_column = QVBoxLayout()
        right_column.setSpacing(8)

        # Info file selezionato
        self.file_info_label = QLabel(t("select_file"))
        self.file_info_label.setStyleSheet("""
            QLabel {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 3px;
                padding: 8px;
                font-size: 11px;
            }
        """)
        self.file_info_label.setMinimumHeight(40)
        right_column.addWidget(self.file_info_label)

        # Pulsanti azione in griglia 2x2
        btn_grid = QGridLayout()
        btn_grid.setSpacing(10)

        self.export_base64_btn = QPushButton(t("export_text_button"))
        self.export_base64_btn.setMinimumHeight(36)
        self.export_base64_btn.setStyleSheet("font-size: 11px; padding: 6px;")
        self.export_base64_btn.clicked.connect(self.export_to_base64)
        self.export_base64_btn.setEnabled(False)
        self.export_base64_btn.setToolTip(t("select_info"))
        btn_grid.addWidget(self.export_base64_btn, 0, 0)

        self.open_file_btn = QPushButton(t("open_button"))
        self.open_file_btn.setMinimumHeight(36)
        self.open_file_btn.setStyleSheet("font-size: 11px; padding: 6px;")
        self.open_file_btn.clicked.connect(self.open_selected_file)
        self.open_file_btn.setEnabled(False)
        self.open_file_btn.setToolTip(t("select_info"))
        btn_grid.addWidget(self.open_file_btn, 0, 1)

        self.copy_path_btn = QPushButton(t("path_button"))
        self.copy_path_btn.setMinimumHeight(36)
        self.copy_path_btn.setStyleSheet("font-size: 11px; padding: 6px;")
        self.copy_path_btn.clicked.connect(self.copy_file_path)
        self.copy_path_btn.setEnabled(False)
        self.copy_path_btn.setToolTip(t("select_info"))
        btn_grid.addWidget(self.copy_path_btn, 1, 0)

        self.copy_result_btn = QPushButton(t("copy_result"))
        self.copy_result_btn.setMinimumHeight(36)
        self.copy_result_btn.setStyleSheet("font-size: 11px; padding: 6px; background-color: #9b59b6; color: white;")
        self.copy_result_btn.clicked.connect(self.copy_result)
        self.copy_result_btn.setEnabled(False)
        self.copy_result_btn.setToolTip(t("export_first"))
        btn_grid.addWidget(self.copy_result_btn, 1, 1)

        right_column.addLayout(btn_grid)

        # === VOLUMI MONTATI ===
        self._volumes_label = QLabel(f"<b>{t('linked_folders')}</b>")
        self._volumes_label.setStyleSheet("font-size: 10px; color: #555; margin-top: 4px;")
        right_column.addWidget(self._volumes_label)

        self.volumes_list = QListWidget()
        self.volumes_list.setMaximumHeight(90)
        self.volumes_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #ddd;
                border-radius: 3px;
                font-size: 10px;
                background: #fafafa;
            }
            QListWidget::item { padding: 3px 6px; }
            QListWidget::item:selected { background-color: #3498db; color: white; }
        """)
        right_column.addWidget(self.volumes_list)

        vol_btn_row = QHBoxLayout()
        vol_btn_row.setSpacing(4)

        self.remove_volume_btn = QPushButton(t("unlink_button"))
        self.remove_volume_btn.setMinimumHeight(28)
        self.remove_volume_btn.setStyleSheet("font-size: 10px; padding: 4px 8px; background-color: #e74c3c; color: white; border-radius: 3px;")
        self.remove_volume_btn.setToolTip(t("unlink_tooltip"))
        self.remove_volume_btn.clicked.connect(self.remove_volume_from_docker)
        vol_btn_row.addWidget(self.remove_volume_btn)

        self.restore_volume_btn = QPushButton(t("restore_button"))
        self.restore_volume_btn.setMinimumHeight(28)
        self.restore_volume_btn.setStyleSheet("font-size: 10px; padding: 4px 8px; background-color: #f39c12; color: white; border-radius: 3px;")
        self.restore_volume_btn.setToolTip(t("restore_tooltip"))
        self.restore_volume_btn.clicked.connect(self.restore_volume)
        vol_btn_row.addWidget(self.restore_volume_btn)

        self.refresh_volumes_btn = QPushButton("↻")
        self.refresh_volumes_btn.setFixedWidth(28)
        self.refresh_volumes_btn.setMinimumHeight(28)
        self.refresh_volumes_btn.setToolTip(t("refresh_volumes_tooltip"))
        self.refresh_volumes_btn.clicked.connect(self.refresh_volumes_list)
        vol_btn_row.addWidget(self.refresh_volumes_btn)

        right_column.addLayout(vol_btn_row)

        # Risultato esportazione
        self._result_label = QLabel(t("export_result"))
        self._result_label.setStyleSheet("font-size: 10px; font-weight: bold; color: #555;")
        right_column.addWidget(self._result_label)

        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setPlaceholderText(t("result_placeholder_archive"))
        self.result_text.setFont(QFont("DejaVu Sans Mono", 10))
        self.result_text.setStyleSheet("border: 1px solid #ddd; border-radius: 3px;")
        right_column.addWidget(self.result_text, 1)

        columns_layout.addLayout(right_column, 1)

        browser_layout.addLayout(columns_layout, 1)

        layout.addWidget(browser_group, 1)  # Stretch per occupare spazio

        # === COME FUNZIONA (layout a due colonne) ===
        config_group = QGroupBox(t("how_it_works"))
        self._howto_group = config_group
        config_layout = QHBoxLayout(config_group)
        config_layout.setContentsMargins(10, 15, 10, 10)
        config_layout.setSpacing(15)

        # === COLONNA SINISTRA: Spiegazione ===
        left_col = QVBoxLayout()
        left_col.setSpacing(8)

        self._intro_box = QLabel(t("archive_purpose"))
        self._intro_box.setWordWrap(True)
        self._intro_box.setStyleSheet("font-size: 11px;")
        left_col.addWidget(self._intro_box)

        # Nota chat in basso a sinistra
        self._note_box = QLabel(t("archive_chat_note"))
        self._note_box.setWordWrap(True)
        self._note_box.setStyleSheet("font-size: 10px;")
        left_col.addWidget(self._note_box)

        left_col.addStretch()
        config_layout.addLayout(left_col, 1)

        # === COLONNA DESTRA: 3 Passaggi ===
        right_col = QVBoxLayout()
        right_col.setSpacing(10)

        self._steps_label = QLabel(t("archive_steps_title"))
        self._steps_label.setStyleSheet("color: #2c3e50;")
        right_col.addWidget(self._steps_label)

        self._step1 = QLabel(t("archive_step1_html"))
        self._step1.setWordWrap(True)
        self._step1.setStyleSheet("font-size: 11px;")
        right_col.addWidget(self._step1)

        self._step2 = QLabel(t("archive_step2_html"))
        self._step2.setWordWrap(True)
        self._step2.setStyleSheet("font-size: 11px;")
        right_col.addWidget(self._step2)

        # Volume path con pulsante copia
        volume_row = QHBoxLayout()
        volume_row.setSpacing(5)

        self.volume_field = QLineEdit("- /percorso/cartella:/app/backend/data/uploads")
        self.volume_field.setReadOnly(True)
        self.volume_field.setStyleSheet("font-family: 'DejaVu Sans Mono'; font-size: 10px; padding: 6px; background: #fff3cd; border: 1px solid #ffc107;")
        volume_row.addWidget(self.volume_field, 1)

        copy_volume_btn = QPushButton("📋")
        copy_volume_btn.setMaximumWidth(35)
        copy_volume_btn.setToolTip(t("copy_volume_tooltip"))
        copy_volume_btn.clicked.connect(self.copy_volume_config)
        volume_row.addWidget(copy_volume_btn)

        right_col.addLayout(volume_row)

        self._step3 = QLabel(t("archive_step3_html"))
        self._step3.setWordWrap(True)
        self._step3.setStyleSheet("font-size: 11px;")
        right_col.addWidget(self._step3)

        right_col.addStretch()
        config_layout.addLayout(right_col, 1)

        layout.addWidget(config_group)

    def set_as_favorite(self):
        """Imposta la cartella corrente come preferita e aggiunge come volume Docker."""
        lang = self._get_lang()
        t = lambda key, **kw: get_text(key, lang, **kw)
        if self.current_path:
            self.settings.setValue("private_folder", self.current_path)
            self.star_btn.setStyleSheet("background-color: #f1c40f;")

            # Aggiungi come volume Docker in docker-compose.yml
            added = self._add_docker_volume(self.current_path)

            if self.main_window:
                if added:
                    self.main_window.statusBar().showMessage(
                        t("folder_added_archive", path=self.current_path), 5000)
                    QMessageBox.information(
                        self, t("volume_added_title"),
                        t("volume_added_msg", path=self.current_path, name=Path(self.current_path).name)
                    )
                else:
                    self.main_window.statusBar().showMessage(
                        t("favorite_set", path=self.current_path), 3000)
        else:
            if self.main_window:
                self.main_window.statusBar().showMessage(t("select_folder_first"), 3000)

    def _add_docker_volume(self, folder_path):
        """Aggiunge una cartella come volume nel docker-compose.yml."""
        compose_file = SCRIPT_DIR / "docker-compose.yml"
        if not compose_file.exists():
            return False

        try:
            content = compose_file.read_text()
            folder_name = Path(folder_path).name
            volume_line = f"      - {folder_path}:/app/backend/data/uploads/{folder_name}"

            # Controlla se il volume esiste gia'
            if folder_path in content:
                return False

            # Inserisci dopo "- open_webui_data:/app/backend/data" nella sezione volumes di open-webui
            marker = "      - open_webui_data:/app/backend/data"
            if marker in content:
                content = content.replace(
                    marker,
                    f"{marker}\n{volume_line}"
                )
                compose_file.write_text(content)
                return True
        except Exception as e:
            print(f"[Archivio] Errore aggiunta volume: {e}")
        return False

    def _remove_docker_volume(self, folder_path):
        """Rimuove un volume dal docker-compose.yml."""
        compose_file = SCRIPT_DIR / "docker-compose.yml"
        if not compose_file.exists():
            return False

        try:
            content = compose_file.read_text()
            folder_name = Path(folder_path).name
            volume_line = f"      - {folder_path}:/app/backend/data/uploads/{folder_name}\n"

            if volume_line in content:
                content = content.replace(volume_line, "")
                compose_file.write_text(content)
                return True
        except Exception as e:
            print(f"[Archivio] Errore rimozione volume: {e}")
        return False

    def _get_custom_volumes(self):
        """Legge i volumi personalizzati dal docker-compose.yml."""
        compose_file = SCRIPT_DIR / "docker-compose.yml"
        if not compose_file.exists():
            return []
        try:
            content = compose_file.read_text()
            volumes = []
            for line in content.splitlines():
                stripped = line.strip()
                # Cerca righe tipo "- /percorso:/app/backend/data/uploads/nome"
                if stripped.startswith("- ") and ":/app/backend/data/uploads/" in stripped:
                    local_path = stripped[2:].split(":")[0].strip()
                    volumes.append(local_path)
            return volumes
        except (OSError, UnicodeDecodeError):
            return []

    def refresh_volumes_list(self):
        """Aggiorna la lista dei volumi montati nella UI."""
        self.volumes_list.clear()
        volumes = self._get_custom_volumes()
        if volumes:
            for vol in volumes:
                folder_name = Path(vol).name
                exists = Path(vol).exists()
                icon = "📁" if exists else "⚠️"
                item = QListWidgetItem(f"{icon} {folder_name}  ({vol})")
                item.setData(Qt.UserRole, vol)
                if not exists:
                    item.setToolTip("Cartella non trovata sul disco")
                    item.setForeground(Qt.gray)
                self.volumes_list.addItem(item)
        else:
            item = QListWidgetItem(get_text("no_linked_folder", self._get_lang()))
            item.setFlags(Qt.NoItemFlags)
            item.setForeground(Qt.gray)
            self.volumes_list.addItem(item)

    def remove_volume_from_docker(self):
        """Scollega la cartella selezionata dalla lista volumi."""
        lang = self._get_lang()
        t = lambda key, **kw: get_text(key, lang, **kw)
        current_item = self.volumes_list.currentItem()
        if not current_item:
            QMessageBox.information(self, t("info"), t("select_info"))
            return

        vol_path = current_item.data(Qt.UserRole)
        if not vol_path:
            return

        folder_name = Path(vol_path).name
        reply = QMessageBox.question(
            self, t("confirm_unlink_title"),
            t("confirm_unlink_msg", name=folder_name, path=vol_path),
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            removed = self._remove_docker_volume(vol_path)
            if removed:
                # Salva nella cronologia per ripristino
                self._save_to_history(vol_path)
                self.refresh_volumes_list()
                QMessageBox.information(
                    self, t("folder_unlinked_title"),
                    t("folder_unlinked_msg", name=folder_name)
                )
            else:
                QMessageBox.information(self, t("info"), t("no_volume_found"))

    def _save_to_history(self, folder_path):
        """Salva un percorso nella cronologia per ripristino."""
        history = self.settings.value("removed_volumes_history", [], type=list)
        if folder_path not in history:
            history.append(folder_path)
            # Mantieni max 20 voci
            if len(history) > 20:
                history = history[-20:]
            self.settings.setValue("removed_volumes_history", history)

    def _get_history(self):
        """Restituisce la cronologia dei volumi rimossi (esclude quelli gia' attivi)."""
        history = self.settings.value("removed_volumes_history", [], type=list)
        active = self._get_custom_volumes()
        return [h for h in history if h not in active]

    def restore_volume(self):
        """Mostra i volumi rimossi in precedenza e permette di ripristinarne uno."""
        lang = self._get_lang()
        t = lambda key, **kw: get_text(key, lang, **kw)
        available = self._get_history()

        if not available:
            QMessageBox.information(
                self, t("no_restore_title"),
                t("no_restore_msg")
            )
            return

        # Mostra lista scelta
        items = [f"{Path(p).name}  ({p})" for p in available]
        from PyQt5.QtWidgets import QInputDialog
        choice, ok = QInputDialog.getItem(
            self, t("restore_folder_title"),
            t("restore_folder_prompt"),
            items, 0, False
        )
        if ok and choice:
            idx = items.index(choice)
            folder_path = available[idx]

            if not Path(folder_path).exists():
                reply = QMessageBox.question(
                    self, t("folder_not_found_title"),
                    t("folder_not_found_msg", path=folder_path),
                    QMessageBox.Yes | QMessageBox.No
                )
                if reply == QMessageBox.Yes:
                    history = self.settings.value("removed_volumes_history", [], type=list)
                    history = [h for h in history if h != folder_path]
                    self.settings.setValue("removed_volumes_history", history)
                return

            added = self._add_docker_volume(folder_path)
            if added:
                # Rimuovi dalla cronologia
                history = self.settings.value("removed_volumes_history", [], type=list)
                history = [h for h in history if h != folder_path]
                self.settings.setValue("removed_volumes_history", history)

                self.refresh_volumes_list()
                folder_name = Path(folder_path).name
                QMessageBox.information(
                    self, t("folder_restored_title"),
                    t("folder_restored_msg", name=folder_name)
                )
            else:
                QMessageBox.information(self, t("info"), t("folder_already_linked"))

    def copy_volume_config(self):
        """Copia la configurazione del volume Docker con il percorso attuale"""
        lang = self._get_lang()
        if self.current_path:
            volume_config = f"- {self.current_path}:/app/backend/data/uploads"
            QApplication.clipboard().setText(volume_config)
            self.volume_field.setText(volume_config)
            if self.main_window:
                self.main_window.statusBar().showMessage(get_text("volume_copied", lang), 3000)
        else:
            if self.main_window:
                self.main_window.statusBar().showMessage(get_text("select_folder_first", lang), 3000)

    def load_settings(self):
        """Carica le impostazioni salvate"""
        private_folder = self.settings.value("private_folder", "")
        if private_folder and Path(private_folder).exists():
            self.set_private_folder(private_folder)
        else:
            # Default: cartella home
            home = str(Path.home())
            self.set_private_folder(home)
        # Carica lista volumi montati
        self.refresh_volumes_list()

    def save_settings(self):
        """Salva le impostazioni"""
        if self.current_path:
            self.settings.setValue("private_folder", self.current_path)

    def select_private_folder(self):
        """Apre dialog per selezionare la cartella privata"""
        folder = QFileDialog.getExistingDirectory(
            self,
            get_text("select_private_folder", self._get_lang()),
            self.current_path or str(Path.home())
        )
        if folder:
            self.set_private_folder(folder)
            self.save_settings()

    def set_private_folder(self, folder_path):
        """Imposta la cartella privata"""
        self.current_path = folder_path
        self.path_label.setText(folder_path)

        # Aggiorna il tree view
        index = self.file_model.setRootPath(folder_path)
        self.tree_view.setRootIndex(index)

        # Aggiorna il campo volume Docker
        if hasattr(self, 'volume_field'):
            self.volume_field.setText(f"- {folder_path}:/app/backend/data/uploads")

        # Evidenzia stellina se è la cartella preferita
        favorite = self.settings.value("private_folder", "")
        if hasattr(self, 'star_btn'):
            if folder_path == favorite:
                self.star_btn.setStyleSheet("background-color: #f1c40f;")
            else:
                self.star_btn.setStyleSheet("")

    def go_back(self):
        """Torna alla cartella precedente"""
        # Usa la history del modello
        self.go_up()

    def go_up(self):
        """Vai alla cartella superiore"""
        if self.current_path:
            parent = str(Path(self.current_path).parent)
            if Path(parent).exists():
                self.set_private_folder(parent)

    def go_home(self):
        """Torna alla cartella privata principale"""
        private_folder = self.settings.value("private_folder", str(Path.home()))
        if Path(private_folder).exists():
            self.set_private_folder(private_folder)

    def refresh_view(self):
        """Aggiorna la vista"""
        if self.current_path:
            self.set_private_folder(self.current_path)

    def on_item_clicked(self, index):
        """Gestisce il click su un elemento"""
        file_path = self.file_model.filePath(index)
        file_info = QFileInfo(file_path)

        if file_info.isFile():
            size_kb = file_info.size() / 1024
            size_str = f"{size_kb:.1f}KB" if size_kb < 1024 else f"{size_kb/1024:.1f}MB"

            self.file_info_label.setText(
                f"📄 {file_info.fileName()} ({size_str})"
            )

            self.export_base64_btn.setEnabled(True)
            self.open_file_btn.setEnabled(True)
            self.copy_path_btn.setEnabled(True)
        else:
            self.file_info_label.setText(f"📁 {file_info.fileName()}")
            self.export_base64_btn.setEnabled(False)
            self.open_file_btn.setEnabled(True)
            self.copy_path_btn.setEnabled(True)

    def on_item_double_clicked(self, index):
        """Gestisce il doppio click su un elemento"""
        file_path = self.file_model.filePath(index)
        file_info = QFileInfo(file_path)

        if file_info.isDir():
            self.set_private_folder(file_path)
        else:
            self.open_selected_file()

    def get_selected_file_path(self):
        """Ottiene il percorso del file selezionato"""
        indexes = self.tree_view.selectedIndexes()
        if indexes:
            return self.file_model.filePath(indexes[0])
        return None

    def export_to_base64(self):
        """Esporta il file selezionato in Base64"""
        file_path = self.get_selected_file_path()
        if not file_path:
            return

        try:
            import base64
            import mimetypes

            file_info = QFileInfo(file_path)
            file_size = file_info.size()

            # Limite 10 MB
            if file_size > 10 * 1024 * 1024:
                QMessageBox.warning(
                    self, get_text("file_too_large", self._get_lang()),
                    get_text("file_too_large_msg", self._get_lang())
                )
                return

            # Leggi e converti
            with open(file_path, 'rb') as f:
                data = f.read()

            base64_data = base64.b64encode(data).decode('utf-8')

            # Determina MIME type
            mime_type, _ = mimetypes.guess_type(file_path)
            if not mime_type:
                mime_type = "application/octet-stream"

            # Crea data URI
            data_uri = f"data:{mime_type};base64,{base64_data}"

            self.last_result = data_uri
            self.copy_result_btn.setEnabled(True)

            # Mostra risultato
            base64_len = len(base64_data)
            compatible = "SI" if base64_len < 40000 else "NO (troppo grande per chat)"

            self.result_text.setPlainText(
                f"✓ Esportato: {file_info.fileName()}\n"
                f"Tipo: {mime_type}\n"
                f"Lunghezza Base64: {base64_len:,} caratteri\n"
                f"Compatibile chat: {compatible}"
            )

        except Exception as e:
            self.result_text.setPlainText(f"✗ Errore: {str(e)}")
            self.copy_result_btn.setEnabled(False)

    def open_selected_file(self):
        """Apre il file/cartella selezionato con l'applicazione predefinita"""
        file_path = self.get_selected_file_path()
        if file_path:
            QDesktopServices.openUrl(QUrl.fromLocalFile(file_path))

    def copy_file_path(self):
        """Copia il percorso del file negli appunti"""
        file_path = self.get_selected_file_path()
        if file_path:
            QApplication.clipboard().setText(file_path)
            self.result_text.setPlainText(get_text("path_copied", self._get_lang(), path=file_path))

    def copy_result(self):
        """Copia il risultato Base64 negli appunti"""
        if self.last_result:
            QApplication.clipboard().setText(self.last_result)
            current = self.result_text.toPlainText()
            self.result_text.setPlainText(current + "\n\n" + get_text("copied_to_clipboard", self._get_lang()))

    def retranslate_ui(self, lang):
        t = lambda key, **kw: get_text(key, lang, **kw)
        self._browse_group.setTitle(t("archive_browse"))
        self._howto_group.setTitle(t("how_it_works"))
        self.export_base64_btn.setText(t("export_text_button"))
        self.open_file_btn.setText(t("open_button"))
        self.copy_path_btn.setText(t("path_button"))
        self.copy_result_btn.setText(t("copy_result"))
        self.back_btn.setToolTip(t("back_tooltip"))
        self.up_btn.setToolTip(t("up_tooltip"))
        self.home_btn.setToolTip(t("home_tooltip"))
        self.refresh_btn.setToolTip(t("refresh_tooltip"))
        self.star_btn.setToolTip(t("favorite_tooltip"))
        self.select_folder_btn.setToolTip(t("browse_tooltip"))
        self.path_label.setPlaceholderText(t("path_placeholder"))
        self.file_info_label.setText(t("select_file"))
        self._volumes_label.setText(f"<b>{t('linked_folders')}</b>")
        self.remove_volume_btn.setText(t("unlink_button"))
        self.remove_volume_btn.setToolTip(t("unlink_tooltip"))
        self.restore_volume_btn.setText(t("restore_button"))
        self.restore_volume_btn.setToolTip(t("restore_tooltip"))
        self.refresh_volumes_btn.setToolTip(t("refresh_volumes_tooltip"))
        self._result_label.setText(t("export_result"))
        self.result_text.setPlaceholderText(t("result_placeholder_archive"))
        self._intro_box.setText(t("archive_purpose"))
        self._note_box.setText(t("archive_chat_note"))
        self._steps_label.setText(t("archive_steps_title"))
        self._step1.setText(t("archive_step1_html"))
        self._step2.setText(t("archive_step2_html"))
        self._step3.setText(t("archive_step3_html"))
