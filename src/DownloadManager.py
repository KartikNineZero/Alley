import os
import sys
import json
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtWidgets import (
    QApplication,
    QDialog,
    QVBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QListView,
    QHBoxLayout
)
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest

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

        self.setLayout(layout)

        self.start_download()

    def start_download(self):
        # Implement your download logic here
        pass

    # Refined delete method
    def delete_download(self):
        try:
            os.remove(self.filepath)
            print(f"{self.filename} deleted")
            self.downloads.remove((self.url, self.filename))
            self.save_downloads()
        except OSError:
            print(f"Failed to delete {self.filename}")

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

    def setup_buttons_layout(self):
        layout = QHBoxLayout()

        openFileButton = QPushButton('Open File')
        openFileButton.clicked.connect(self.open_file)
        layout.addWidget(openFileButton)

        openFolderButton = QPushButton('Open Folder')
        openFolderButton.clicked.connect(self.open_folder)
        layout.addWidget(openFolderButton)

        return layout


        
from PyQt5.QtCore import QAbstractListModel, Qt

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

        self.downloads = self.load_downloads()

        layout = QVBoxLayout()

        self.listView = QListView()
        self.model = DownloadModel(self.downloads)
        self.listView.setModel(self.model)
        self.listView.clicked.connect(self.listview_clicked)
        layout.addWidget(self.listView)

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

        dialog.setLayout(layout)
        dialog.exec_()

    def rowCount(self, parent=None):
        return len(self.downloads)

    def data(self, index, role=None):
        if role == Qt.DisplayRole:
            return self.downloads[index.row()][1]
        
    

