import sys
import json
import os
import webbrowser

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLineEdit, QLabel, QFileDialog, QListWidget, QListWidgetItem,
    QMessageBox, QComboBox, QSystemTrayIcon, QMenu, QCheckBox,
    QInputDialog
)
from PyQt6.QtGui import QIcon, QAction, QKeySequence
from PyQt6.QtCore import Qt, QUrl, QMimeData

FAVORITES_FILE = 'favorites.json'
SETTINGS_FILE = 'settings.json'

def load_settings():
    if not os.path.exists(SETTINGS_FILE):
        return {"start_on_boot": False, "start_in_tray": False}
    try:
        with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
            settings = json.load(f)
            settings.setdefault("start_on_boot", False)
            settings.setdefault("start_in_tray", False)
            return settings
    except json.JSONDecodeError:
        print(f"Warning: Could not decode {SETTINGS_FILE}. Returning default settings.")
        return {"start_on_boot": False, "start_in_tray": False}
    except Exception as e:
        print(f"Error loading settings: {e}. Returning default settings.")
        return {"start_on_boot": False, "start_in_tray": False}

def save_settings(settings):
    try:
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving settings: {e}")

class FavoritesApp(QWidget):
    def __init__(self):
        super().__init__()
        self.settings = load_settings()
        self.favorites = self.load_favorites()
        self.current_edit_index = -1

        self.setWindowTitle("Favorites")
        self.setWindowIcon(QIcon("C:/Users/User/Desktop/icon.ico"))
        self.resize(600, 500)

        self.init_ui()

        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon("C:/Users/User/Desktop/icon.ico"))
        self.tray_icon.setToolTip("Favorites - Running in background")
        self.tray_icon.activated.connect(self.on_tray_icon_activated)

        self.update_tray_menu()
        self.tray_icon.show()

        if self.settings.get("start_in_tray", False):
            self.hide()
            self.tray_icon.showMessage(
                "Favorites",
                "Application started minimized to system tray.",
                QSystemTrayIcon.MessageIcon.Information,
                3000
            )
        else:
            self.showNormal()

        self.setAcceptDrops(True)

    def init_ui(self):
        main_layout = QVBoxLayout()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search favorites by name, type, or tags...")
        self.search_input.textChanged.connect(self.filter_favorites)
        main_layout.addWidget(self.search_input)

        input_layout = QHBoxLayout()

        self.label_input = QLineEdit()
        self.label_input.setPlaceholderText("Name (e.g., Google, Documents, etc.)")
        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText("Path or URL")

        browse_button = QPushButton("Browse")
        browse_button.clicked.connect(self.browse_path_or_url)

        self.type_box = QComboBox()
        self.type_box.addItems(["File", "Folder", "URL", "App"])

        input_layout.addWidget(self.label_input)
        input_layout.addWidget(self.path_input)
        input_layout.addWidget(self.type_box)
        input_layout.addWidget(browse_button)
        main_layout.addLayout(input_layout)

        self.tag_input = QLineEdit()
        self.tag_input.setPlaceholderText("Tags (comma-separated, e.g., work, personal, important)")
        main_layout.addWidget(self.tag_input)

        buttons_layout = QHBoxLayout()

        self.add_update_button = QPushButton("Add")
        self.add_update_button.clicked.connect(self.add_or_update_favorite)

        self.edit_button = QPushButton("Edit")
        self.edit_button.clicked.connect(self.edit_selected_favorite)
        self.edit_button.setEnabled(False)

        self.delete_button = QPushButton("Delete Selected")
        self.delete_button.clicked.connect(self.confirm_delete_selected)
        self.delete_button.setEnabled(False)

        self.cancel_edit_button = QPushButton("Cancel Edit")
        self.cancel_edit_button.clicked.connect(self.cancel_edit)
        self.cancel_edit_button.setVisible(False)

        buttons_layout.addWidget(self.add_update_button)
        buttons_layout.addWidget(self.edit_button)
        buttons_layout.addWidget(self.delete_button)
        buttons_layout.addWidget(self.cancel_edit_button)
        main_layout.addLayout(buttons_layout)

        main_layout.addWidget(QLabel("📌 Favorites"))
        self.list_widget = QListWidget()
        self.update_list()
        self.list_widget.itemDoubleClicked.connect(self.open_favorite_from_list)
        self.list_widget.currentRowChanged.connect(self.update_button_states)
        self.list_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.list_widget.customContextMenuRequested.connect(self.show_list_context_menu)
        main_layout.addWidget(self.list_widget)

        self.status_label = QLabel("Ready.")
        self.status_label.setStyleSheet("color: #bbbbbb; padding: 5px; font-size: 12px;")
        main_layout.addWidget(self.status_label)

        bottom_layout = QHBoxLayout()

        self.autorun_checkbox = QCheckBox()
        self.autorun_checkbox.setChecked(self.settings.get("start_on_boot", False))
        self.autorun_checkbox.stateChanged.connect(self.toggle_autorun)

        autorun_label = QLabel("Start app on system startup")
        autorun_label.setStyleSheet("font-weight: bold; color: #dddddd;")

        bottom_layout.addWidget(self.autorun_checkbox)
        bottom_layout.addWidget(autorun_label)
        
        self.start_in_tray_checkbox = QCheckBox()
        self.start_in_tray_checkbox.setChecked(self.settings.get("start_in_tray", False))
        self.start_in_tray_checkbox.stateChanged.connect(self.toggle_start_in_tray)

        start_in_tray_label = QLabel("Start minimized to system tray")
        start_in_tray_label.setStyleSheet("font-weight: bold; color: #dddddd;")

        bottom_layout.addWidget(self.start_in_tray_checkbox)
        bottom_layout.addWidget(start_in_tray_label)

        bottom_layout.addStretch()

        exit_button = QPushButton("Exit")
        exit_button.setStyleSheet("background-color: #b33a3a; color: white; font-weight: bold; padding: 6px 12px;")
        exit_button.clicked.connect(QApplication.quit)

        bottom_layout.addWidget(exit_button)
        main_layout.addSpacing(10)
        main_layout.addLayout(bottom_layout)

        self.setLayout(main_layout)
        self.update_button_states()

        QAction("Add", self, shortcut=QKeySequence("Ctrl+A"), triggered=self.add_or_update_favorite)
        QAction("Edit", self, shortcut=QKeySequence("Ctrl+E"), triggered=self.edit_selected_favorite)
        QAction("Delete", self, shortcut=QKeySequence(Qt.Key.Key_Delete), triggered=self.confirm_delete_selected)
        QAction("Cancel Edit", self, shortcut=QKeySequence(Qt.Key.Key_Escape), triggered=self.cancel_edit)


    def show_status_message(self, message, is_error=False):
        if is_error:
            self.status_label.setStyleSheet("color: #FF6347; padding: 5px; font-size: 12px;")
        else:
            self.status_label.setStyleSheet("color: #bbbbbb; padding: 5px; font-size: 12px;")
        self.status_label.setText(message)

    def load_favorites(self):
        if not os.path.exists(FAVORITES_FILE):
            return []
        try:
            with open(FAVORITES_FILE, 'r', encoding='utf-8') as f:
                favorites_data = json.load(f)
                for item in favorites_data:
                    item.setdefault('tags', [])
                return favorites_data
        except json.JSONDecodeError:
            print(f"Warning: Could not decode {FAVORITES_FILE}. Returning empty favorites list.")
            self.show_status_message(f"Warning: Could not load favorites file.", is_error=True)
            return []
        except Exception as e:
            print(f"Error loading favorites: {e}. Returning empty favorites list.")
            self.show_status_message(f"Error loading favorites: {e}", is_error=True)
            return []

    def save_favorites(self):
        try:
            with open(FAVORITES_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.favorites, f, indent=4, ensure_ascii=False)
            self.show_status_message("Favorites saved successfully.")
        except Exception as e:
            print(f"Error saving favorites: {e}")
            self.show_status_message(f"Error saving favorites: {e}", is_error=True)

    def add_or_update_favorite(self):
        label = self.label_input.text().strip()
        path = self.path_input.text().strip()
        f_type = self.type_box.currentText()
        tags_raw = self.tag_input.text().strip()
        tags = [tag.strip() for tag in tags_raw.split(',') if tag.strip()]

        if not label or not path:
            self.show_status_message("Warning: Please fill in 'Name' and 'Path or URL' fields.", is_error=True)
            return

        if self.current_edit_index == -1:
            self.favorites.append({"label": label, "path": path, "type": f_type, "tags": tags})
            self.show_status_message(f"Favorite '{label}' added.")
        else:
            self.favorites[self.current_edit_index] = {"label": label, "path": path, "type": f_type, "tags": tags}
            self.show_status_message(f"Favorite '{label}' updated.")
            self.cancel_edit()

        self.save_favorites()
        self.filter_favorites(self.search_input.text())
        self.update_tray_menu()
        self.label_input.clear()
        self.path_input.clear()
        self.tag_input.clear()
        self.update_button_states()

    def edit_selected_favorite(self):
        selected_row = self.list_widget.currentRow()
        if selected_row >= 0:
            self.current_edit_index = selected_row
            fav_item = self.favorites[selected_row]
            self.label_input.setText(fav_item['label'])
            self.path_input.setText(fav_item['path'])
            self.type_box.setCurrentText(fav_item['type'])
            self.tag_input.setText(", ".join(fav_item.get('tags', [])))

            self.add_update_button.setText("Update")
            self.cancel_edit_button.setVisible(True)
            self.edit_button.setEnabled(False)
            self.delete_button.setEnabled(False)
            self.list_widget.setEnabled(False)

            self.show_status_message(f"Editing: '{fav_item['label']}'")
        else:
            self.show_status_message("Please select an item to edit.", is_error=True)

    def cancel_edit(self):
        self.current_edit_index = -1
        self.label_input.clear()
        self.path_input.clear()
        self.tag_input.clear()
        self.type_box.setCurrentText("File")

        self.add_update_button.setText("Add")
        self.cancel_edit_button.setVisible(False)
        self.list_widget.setEnabled(True)
        self.show_status_message("Edit cancelled.")
        self.update_button_states()

    def update_list(self):
        self.list_widget.clear()
        for item_data in self.favorites:
            tags_str = f" [{', '.join(item_data['tags'])}]" if item_data.get('tags') else ""
            list_item = QListWidgetItem(f"{item_data['label']} ({item_data['type']}){tags_str}")
            self.list_widget.addItem(list_item)
        self.update_button_states()

    def confirm_delete_selected(self):
        selected_row = self.list_widget.currentRow()
        if selected_row >= 0:
            if hasattr(self.list_widget, 'filtered_indices') and self.list_widget.filtered_indices:
                original_index = self.list_widget.filtered_indices[selected_row]
                item_to_delete_label = self.favorites[original_index]['label']
            else:
                item_to_delete_label = self.favorites[selected_row]['label']

            reply = QMessageBox.question(self, 'Confirm Deletion',
                                         f"Are you sure you want to delete '{item_to_delete_label}'?",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                         QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self.delete_selected_favorite(selected_row)
                self.show_status_message(f"Favorite '{item_to_delete_label}' deleted.")
            else:
                self.show_status_message("Deletion cancelled.")
        else:
            self.show_status_message("Please select an item to delete.", is_error=True)

    def delete_selected_favorite(self, list_row_index=None):
        if list_row_index is None:
            selected_row = self.list_widget.currentRow()
        else:
            selected_row = list_row_index

        if selected_row >= 0:
            if hasattr(self.list_widget, 'filtered_indices') and self.list_widget.filtered_indices:
                original_index = self.list_widget.filtered_indices[selected_row]
            else:
                original_index = selected_row

            if 0 <= original_index < len(self.favorites):
                del self.favorites[original_index]
                self.save_favorites()
                self.filter_favorites(self.search_input.text())
                self.update_tray_menu()
                self.update_button_states()
            else:
                self.show_status_message("Error: Item to delete not found in original list.", is_error=True)
        else:
            self.show_status_message("No item selected for deletion.", is_error=True)


    def filter_favorites(self, text):
        search_text = text.lower()
        self.list_widget.clear()
        filtered_favorites_indices = []
        for i, item_data in enumerate(self.favorites):
            tags_lower = " ".join([t.lower() for t in item_data.get('tags', [])])
            display_text_for_search = f"{item_data['label'].lower()} {item_data['type'].lower()} {tags_lower}"

            if search_text in display_text_for_search:
                tags_str = f" [{', '.join(item_data['tags'])}]" if item_data.get('tags') else ""
                list_item = QListWidgetItem(f"{item_data['label']} ({item_data['type']}){tags_str}")
                self.list_widget.addItem(list_item)
                filtered_favorites_indices.append(i)
        self.list_widget.filtered_indices = filtered_favorites_indices
        self.update_button_states()

    def open_favorite_from_list(self, list_item_or_index=None):
        if isinstance(list_item_or_index, QListWidgetItem):
            current_row = self.list_widget.row(list_item_or_index)
        elif isinstance(list_item_or_index, int):
            current_row = list_item_or_index
        else:
            current_row = self.list_widget.currentRow()

        if current_row >= 0:
            if hasattr(self.list_widget, 'filtered_indices') and self.list_widget.filtered_indices:
                if 0 <= current_row < len(self.list_widget.filtered_indices):
                    original_index = self.list_widget.filtered_indices[current_row]
                else:
                    self.show_status_message("Error: Could not determine item to open (filtered).", is_error=True)
                    return
            else:
                original_index = current_row

            if 0 <= original_index < len(self.favorites):
                fav_item = self.favorites[original_index]
                self._execute_favorite(fav_item)
                self.show_status_message(f"Opened: '{fav_item['label']}'")
            else:
                self.show_status_message("Error: Item not found to open (original list).", is_error=True)
        else:
            self.show_status_message("Please select an item to open.", is_error=True)

    def _execute_favorite(self, fav_item):
        path = fav_item['path']
        f_type = fav_item['type']

        if f_type == 'URL':
            webbrowser.open(path)
        elif f_type in ['File', 'Folder', 'App']:
            try:
                os.startfile(path)
            except FileNotFoundError:
                self.show_status_message(f"Error: Target not found: '{path}'", is_error=True)
            except Exception as e:
                self.show_status_message(f"Error occurred while opening '{path}': {e}", is_error=True)

    def browse_path_or_url(self):
        f_type = self.type_box.currentText()

        if f_type == "File":
            path, _ = QFileDialog.getOpenFileName(self, "Select File")
        elif f_type == "Folder":
            path = QFileDialog.getExistingDirectory(self, "Select Folder")
        elif f_type == "App":
            path, _ = QFileDialog.getOpenFileName(self, "Select Application", filter="Executable Files (*.exe);;All Files (*)")
        elif f_type == "URL":
            self.show_status_message("Please enter URLs manually.", is_error=False)
            return

        if path:
            self.path_input.setText(path)
            self.show_status_message(f"Path selected: '{path}'")

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls() or event.mimeData().hasFormat('text/uri-list'):
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        if urls:
            for url in urls:
                if url.isLocalFile():
                    path = url.toLocalFile()
                    if os.path.isdir(path):
                        f_type = "Folder"
                    elif os.path.isfile(path):
                        if path.lower().endswith(('.exe', '.lnk', '.bat', '.cmd')):
                            f_type = "App"
                        else:
                            f_type = "File"
                    else:
                        f_type = "File"

                    label = os.path.basename(path)
                    self.label_input.setText(label)
                    self.path_input.setText(path)
                    self.type_box.setCurrentText(f_type)
                    self.show_status_message(f"Dropped: '{label}' ({f_type}). Ready to add/update.")
                else:
                    path = url.toString()
                    label = url.host() or "Web Link"
                    self.label_input.setText(label)
                    self.path_input.setText(path)
                    self.type_box.setCurrentText("URL")
                    self.show_status_message(f"Dropped URL: '{label}'. Ready to add/update.")
            event.acceptProposedAction()
        else:
            event.ignore()


    def on_tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            if self.isHidden():
                self.showNormal()
                self.activateWindow()

    def closeEvent(self, event):
        event.ignore()
        self.hide()
        self.tray_icon.showMessage(
            "Favorites",
            "Application minimized to system tray.",
            QSystemTrayIcon.MessageIcon.Information,
            3000
        )

    def update_tray_menu(self):
        tray_menu = QMenu()

        for item_data in self.favorites:
            action = QAction(f"{item_data['label']} ({item_data['type']})", self)
            action.triggered.connect(lambda checked, i=item_data: self._execute_favorite(i))
            tray_menu.addAction(action)

        tray_menu.addSeparator()

        restore_action = QAction("🔄 Restore", self)
        restore_action.triggered.connect(self.showNormal)
        tray_menu.addAction(restore_action)

        tray_menu.addSeparator()

        exit_action = QAction("❌ Exit", self)
        exit_action.triggered.connect(QApplication.quit)
        tray_menu.addAction(exit_action)

        self.tray_icon.setContextMenu(tray_menu)

    def toggle_autorun(self, state):
        enabled = (state == Qt.CheckState.Checked)
        self.settings["start_on_boot"] = enabled
        save_settings(self.settings)
        self.set_autorun(enabled)

    def set_autorun(self, enable):
        if sys.platform != 'win32':
            self.show_status_message("This feature is only supported on Windows operating system.", is_error=True)
            return

        startup_folder = os.path.join(os.getenv('APPDATA'), r'Microsoft\Windows\Start Menu\Programs\Startup')
        script_path = os.path.abspath(sys.argv[0])
        shortcut_name = "FavoritesApp.lnk"
        shortcut_path = os.path.join(startup_folder, shortcut_name)

        try:
            import pythoncom
            from win32com.client import Dispatch
        except ImportError:
            self.show_status_message(
                "Error: The 'pywin32' package is required for the autorun feature. Install it using 'pip install pywin32'.",
                is_error=True
            )
            return

        if enable:
            try:
                shell = Dispatch('WScript.Shell')
                shortcut = shell.CreateShortCut(shortcut_path)
                shortcut.Targetpath = sys.executable
                shortcut.Arguments = f'"{script_path}"'
                shortcut.WorkingDirectory = os.path.dirname(script_path)
                shortcut.IconLocation = script_path
                shortcut.save()
                self.show_status_message("Application added to startup folder.")
            except Exception as e:
                self.show_status_message(f"Error adding to startup: {e}", is_error=True)
        else:
            if os.path.exists(shortcut_path):
                try:
                    os.remove(shortcut_path)
                    self.show_status_message("Application removed from startup folder.")
                except Exception as e:
                    self.show_status_message(f"Error removing from startup: {e}", is_error=True)

    def toggle_start_in_tray(self, state):
        enabled = (state == Qt.CheckState.Checked)
        self.settings["start_in_tray"] = enabled
        save_settings(self.settings)
        self.show_status_message(f"Start minimized to tray set to: {enabled}")


    def update_button_states(self):
        has_selection = self.list_widget.currentRow() >= 0
        is_editing = self.current_edit_index != -1

        self.edit_button.setEnabled(has_selection and not is_editing)
        self.delete_button.setEnabled(has_selection and not is_editing)

    def show_list_context_menu(self, position):
        item = self.list_widget.itemAt(position)
        if item:
            context_menu = QMenu(self)

            open_action = QAction("Open", self)
            open_action.triggered.connect(lambda: self.open_favorite_from_list(item))
            context_menu.addAction(open_action)

            edit_action = QAction("Edit", self)
            edit_action.triggered.connect(self.edit_selected_favorite)
            context_menu.addAction(edit_action)

            delete_action = QAction("Delete", self)
            delete_action.triggered.connect(self.confirm_delete_selected)
            context_menu.addAction(delete_action)

            context_menu.exec(self.list_widget.mapToGlobal(position))


if __name__ == '__main__':
    app = QApplication(sys.argv)

    dark_stylesheet = """
    QWidget {
        background-color: #2b2b2b;
        color: #f0f0f0;
        font-family: "Segoe UI", sans-serif;
        font-size: 14px;
    }
    QLineEdit, QComboBox, QListWidget {
        background-color: #3c3f41;
        border: 1px solid #555;
        border-radius: 5px;
        padding: 5px;
        selection-background-color: #4CAF50;
    }
    QPushButton {
        background-color: #5c5c5c;
        border: none;
        border-radius: 5px;
        padding: 6px 12px;
        color: #f0f0f0;
    }
    QPushButton:hover {
        background-color: #6d6d6d;
    }
    QPushButton:pressed {
        background-color: #4d4d4d;
    }
    QListWidget::item {
        padding: 6px;
        margin: 2px;
    }
    QListWidget::item:selected {
        background-color: #505050;
        color: #ffffff;
    }
    QLabel {
        color: #bbbbbb;
        padding: 2px;
    }
    QCheckBox::indicator {
        width: 16px;
        height: 16px;
        border: 1px solid #777;
        border-radius: 3px;
        background-color: #444;
    }
    QCheckBox::indicator:unchecked {
    }
    QCheckBox::indicator:checked {
        background-color: #4CAF50;
        border: 1px solid #4CAF50;
        image: url(data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCI+PHBhdGggZmlsbD0id2hpdGUiIGQ9Ik05IDE2LjIwNkw1LjQxNCAxMi42MkEwLjg1NyAwLjg1NyAwIDAwNC4yNjkgMTMuMjk0TDUuNDIgMTQuNjQ5TCA4LjgxMiAxOC4xODZMMTkuNzI1IDcuOTY0QTAuODY3IDAuODY3IDAgMDAxOS43NzQgNy45MDhBMS4wMzEgMS4wMzEgMCAwMDAyMC45MzUgOC43NUwyMS4wNzUgNy43NjRMMTkuOTUyIDYuODc3QTIuNzUgMi43NSAwIDAwMTkuOTQxIDYuODM2TDE3LjcwMyAzLjg2MkExLjYwMiAwIDAwMTUuNTY1IDMuNjM0TDEwLjI0MiA1LjE5TDkgNS42MzdMOSA2LjA3NUwxNS43NjQgMTQuMTIzTDEzLjA4IDE4LjExOEwxMC4zMDYgMTQuOTc1TDkgMTYuMjA2eiIvPjwvc3ZnPg==);
    }
    """
    app.setStyleSheet(dark_stylesheet)

    window = FavoritesApp()

    sys.exit(app.exec())
