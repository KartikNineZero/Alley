import os
import sys
import json
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication,
    QDialog,
    QVBoxLayout,
    QPushButton,
    QListView,
    QHBoxLayout,
    QLabel,
    QMessageBox
)


class DownloadDialog(QDialog):
    def __init__(self, url, filename, parent=None, downloads=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint)  # Hide titlebar

        self.url = url
        self.filename = filename
        self.parent = parent
        self.downloads = downloads or []

        # Refined filepath storage
        self.dirpath = os.path.join(os.path.expanduser("~"), "Downloads")
        self.filepath = os.path.join(self.dirpath, self.filename)

        layout = QVBoxLayout()

        self.label = QLabel(f'Downloading {filename}...')
        layout.addWidget(self.label)

        # Removed progress bar

        self.deleteButton = QPushButton('Delete')
        self.deleteButton.clicked.connect(self.delete_download)
        layout.addWidget(self.deleteButton)

        self.showInFolderButton = QPushButton('Show in Folder')
        self.showInFolderButton.clicked.connect(self.show_in_folder)
        layout.addWidget(self.showInFolderButton)

        self.setLayout(layout)

        self.start_download()

    def start_download(self):
        # Implement your download logic here
        pass

    def delete_download(self):
        confirmation = QMessageBox.question(
            self,
            'Confirmation',
            f"Do you really want to delete {self.filename}?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if confirmation == QMessageBox.Yes:
            try:
                os.remove(self.filepath)
                print(f"{self.filename} deleted")
                self.downloads.remove((self.url, self.filename))
                self.save_downloads()
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
            os.startfile(self.filepath)  # Open the file
        except OSError as e:
            print(f"Failed to open the file: {e}")

    def open_folder(self):
        try:
            folder_path = os.path.dirname(self.filepath)
            os.startfile(folder_path)  # Open the folder
        except OSError as e:
            print(f"Failed to open the folder: {e}")

    def show_in_folder(self):
        try:
            folder_path = os.path.dirname(self.filepath)
            os.startfile(folder_path)  # Open the folder
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


from PyQt5.QtCore import QAbstractListModel

class DownloadModel(QAbstractListModel):
    def __init__(self, downloads, parent=None):
        super().__init__(parent)
        self.downloads = downloads

    def rowCount(self, parent=None):
        return len(self.downloads)

    def data(self, index, role=None):
        if role == Qt.DisplayRole:
            return self.downloads[index.row()][1]

class DownloadManager(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Download Manager')
        self.setGeometry(100, 100, 800, 400)  # Set a larger window size
        # ... rest of the code ...
        self.setWindowTitle('Download Manager')
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

        self.downloads = self.load_downloads()

        layout = QVBoxLayout()

        self.listView = QListView()
        self.model = DownloadModel(self.downloads)
        self.listView.setModel(self.model)
        self.listView.clicked.connect(self.listview_clicked)
        layout.addWidget(self.listView)

        self.deleteSelectedButton = QPushButton('Delete Selected')
        self.deleteSelectedButton.clicked.connect(self.delete_selected)
        layout.addWidget(self.deleteSelectedButton)

        self.setLayout(layout)

    def add_download(self, url, filename):
        self.downloads.append((url, filename))
        self.model.layoutChanged.emit()
        # Add the download to the list and save
        self.save_downloads()

        # Optionally, you can handle other aspects of the download here

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

    def listview_clicked(self, index):
        url, filename = self.downloads[index.row()]
        dialog = DownloadDialog(url, filename, self)
        layout = QHBoxLayout()

        openFileButton = QPushButton('Open File')
        openFileButton.clicked.connect(dialog.open_file)
        layout.addWidget(openFileButton)

        openFolderButton = QPushButton('Open Folder')
        openFolderButton.clicked.connect(dialog.open_folder)
        layout.addWidget(openFolderButton)

        showInFolderButton = QPushButton('Show in Folder')
        showInFolderButton.clicked.connect(dialog.show_in_folder)  # Connect the new button
        layout.addWidget(showInFolderButton)

        dialog.setLayout(layout)
        dialog.exec_()

    def delete_selected(self):
        selected_indexes = self.listView.selectedIndexes()
        if not selected_indexes:
            return

        selected_index = selected_indexes[0]
        confirmation = QMessageBox.question(
            self,
            'Confirmation',
            'Do you really want to delete the selected item?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if confirmation == QMessageBox.Yes:
            try:
                selected_row = selected_index.row()
                self.model.beginRemoveRows(selected_index.parent(), selected_row, selected_row)
                url, filename = self.model.downloads[selected_row]
                file_path = os.path.join(os.path.expanduser("~"), "Downloads", filename)

                print(f"Deleting file: {file_path}")  # Log the file path for debugging

                os.remove(file_path)
                print(f"{filename} deleted")
                self.model.downloads.pop(selected_row)
                self.model.endRemoveRows()
                self.save_downloads()
            except OSError as e:
                print(f"Failed to delete the item: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    manager = DownloadManager()
    manager.show()
    sys.exit(app.exec_())
