import os
import sys
import json
from PyQt5.QtCore import Qt, QAbstractListModel, QSize
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QApplication,
    QDialog,
    QVBoxLayout,
    QPushButton,
    QListView,
    QHBoxLayout,
    QStyledItemDelegate,
    QMessageBox
)

class DownloadDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        super().paint(painter, option, index)

        delete_icon = QIcon('delete_icon.png')
        delete_icon_rect = option.rect.adjusted(option.rect.width() - 20, 0, 0, 0)
        delete_icon.paint(painter, delete_icon_rect)

    def sizeHint(self, option, index):
        size_hint = super().sizeHint(option, index)
        return QSize(size_hint.width() + 20, size_hint.height())

class DownloadDialog(QDialog):
    def __init__(self, url, filename, parent=None, downloads=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint)

        self.url = url
        self.filename = filename
        self.parent = parent
        self.downloads = downloads or []

        self.dirpath = os.path.join(os.path.expanduser("~"), "Downloads")
        self.filepath = os.path.join(self.dirpath, self.filename)

        layout = QVBoxLayout()

        self.label = QLabel(f'Downloading {filename}...')
        layout.addWidget(self.label)

        self.showInFolderButton = QPushButton('Show in Folder')
        self.showInFolderButton.clicked.connect(self.show_in_folder)
        layout.addWidget(self.showInFolderButton)

        self.setLayout(layout)

        self.start_download()

    def start_download(self):
        # Implement your download logic here
        pass

    def delete_download(self):
        try:
            if os.path.exists(self.filepath):
                os.remove(self.filepath)
                print(f"{self.filename} deleted")
                self.downloads.remove((self.url, self.filename, self.dirpath))
                self.save_downloads()
            else:
                print(f"File not found: {self.filename}")
        except OSError as e:
            print(f"Failed to delete {self.filename}: {e}")

        self.close()

    def save_downloads(self):
        try:
            with open("downloads.json", "w") as file:
                json.dump(self.downloads, file)
        except Exception as e:
            print(f"Error saving downloads: {e}")

    def open_file(self):
        try:
            os.startfile(self.filepath)
        except OSError as e:
            print(f"Failed to open the file: {e}")

    def open_folder(self):
        try:
            folder_path = os.path.dirname(self.filepath)
            os.startfile(folder_path)
        except OSError as e:
            print(f"Failed to open the folder: {e}")

    def show_in_folder(self):
        try:
            folder_path = os.path.dirname(self.filepath)
            os.startfile(folder_path)
        except OSError as e:
            print(f"Failed to open the folder: {e}")

    def setup_buttons_layout(self):
        layout = QHBoxLayout()

        openFileButton = QPushButton('Open File')
        openFileButton.clicked.connect(self.open_file)
        layout.addWidget(openFileButton)

        openFolderButton = QPushButton('Open Folder')
        openFolderButton.clicked.connect(self.open_folder)
        layout.addWidget(openFolderButton)

        return layout

class DownloadModel(QAbstractListModel):
    def __init__(self, downloads, parent=None):
        super().__init__(parent)
        self.downloads = downloads

    def rowCount(self, parent=None):
        return len(self.downloads)

    def data(self, index, role=None):
        if role == Qt.DisplayRole:
            return self.downloads[index.row()][1]
        elif role == Qt.UserRole:
            return self.downloads[index.row()][2]  # Additional role for path

    def flags(self, index):
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsUserCheckable | Qt.ItemIsEditable

class DownloadManager(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Download Manager')
        self.setGeometry(100, 100, 800, 400)
        self.center_on_screen()

        self.downloads = self.load_downloads()

        layout = QVBoxLayout()

        self.listView = QListView()
        self.model = DownloadModel(self.downloads)
        self.listView.setModel(self.model)
        self.listView.doubleClicked.connect(self.show_in_folder)  # Connect to new slot
        self.listView.setItemDelegate(DownloadDelegate())
        layout.addWidget(self.listView)

        self.clearAllButton = QPushButton('Clear All')
        self.clearAllButton.clicked.connect(self.clear_all)
        layout.addWidget(self.clearAllButton)

        self.setLayout(layout)

        self.setStyleSheet('''
            QDialog {
                background-color: #1E1E1E;  /* Dark gray background */
                border: 1px solid #303030;  /* Darker border */
                color: #FFFFFF;  /* White text */
            }
            QListView {
                border: 2px solid #303030;  /* Darker border for list view */
                border-radius: 8px;
                padding: 8px;
                background-color: #2E2E2E;  /* Slightly lighter background for list view */
            }
            QListView::item {
                padding: 23px;  /* Padding for each download item */
                background-color: #000000;  /* Black color for padding */
                margin-bottom: 5px;  /* Gap between each item */
                border-radius: 10px;  /* Curved edges */
            }
        ''')

    def center_on_screen(self):
        screen_geometry = QApplication.desktop().screenGeometry()
        center_x = (screen_geometry.width() - self.width()) // 2
        center_y = (screen_geometry.height() - self.height()) // 2
        self.move(center_x, center_y)

    def add_download(self, url, filename):
        path = os.path.join(os.path.expanduser("~"), "Downloads")
        self.downloads.append((url, filename, path))
        self.model.layoutChanged.emit()
        self.save_downloads()

    def save_downloads(self):
        try:
            with open("downloads.json", "w") as file:
                json.dump(self.downloads, file)
        except Exception as e:
            print(f"Error saving downloads: {e}")

    def load_downloads(self):
        try:
            with open("downloads.json", "r") as file:
                return json.load(file)
        except FileNotFoundError:
            return []
        except Exception as e:
            print(f"Error loading downloads: {e}")
            return []

    def delete_selected_item(self, index):
        url, filename, path = self.downloads[index.row()]
        response = QMessageBox.question(self, 'Delete Download',
                                        f"Do you want to delete {filename}?",
                                        QMessageBox.Yes | QMessageBox.No)

        if response == QMessageBox.Yes:
            filepath = os.path.join(path, filename)
            try:
                if os.path.exists(filepath):
                    os.remove(filepath)
                    print(f"{filename} deleted from the actual location")
                else:
                    print(f"File not found: {filename}")
            except OSError as e:
                print(f"Failed to delete {filename} from the actual location: {e}")

            self.model.beginRemoveRows(self.model.index(0, 0), index.row(), index.row())
            del self.downloads[index.row()]
            self.model.endRemoveRows()
            self.save_downloads()

    def show_in_folder(self, index):
        url, filename, path = self.downloads[index.row()]
        try:
            os.startfile(path)
        except OSError as e:
            print(f"Failed to open the folder: {e}")

    def clear_all(self):
        self.model.beginRemoveRows(self.model.index(0, 0), 0, len(self.downloads) - 1)
        self.downloads.clear()
        self.model.endRemoveRows()
        self.save_downloads()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    manager = DownloadManager()
    manager.show()
    sys.exit(app.exec_())
