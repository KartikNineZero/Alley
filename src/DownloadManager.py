import os
import sys
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import (
    QApplication,
    QDialog,
    QVBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QListView
)
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest

class DownloadDialog(QDialog):
    def __init__(self, url, filename, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Download File')

        self.url = url
        self.filename = filename
        self.bytes_received = 0
        self.bytes_total = 0

        # Store filepath as an instance variable
        self.filepath = os.path.join(os.path.expanduser("~"), "Downloads", self.filename)

        layout = QVBoxLayout()

        self.label = QLabel(f'Downloading {filename}...')
        layout.addWidget(self.label)

        self.progressBar = QProgressBar()
        layout.addWidget(self.progressBar)

        # Add a delete button
        self.deleteButton = QPushButton('Delete')
        self.deleteButton.clicked.connect(self.delete_download)
        layout.addWidget(self.deleteButton)

        self.setLayout(layout)

        # Start the download
        self.start_download()

    def start_download(self):
        self.networkManager = QNetworkAccessManager()
        self.reply = self.networkManager.get(QNetworkRequest(QUrl(self.url)))
        self.reply.finished.connect(self.download_finished)
        self.reply.downloadProgress.connect(self.download_progress)

        self.file = open(self.filepath, 'wb')

    def download_progress(self, bytesReceived, bytesTotal):
        self.bytes_received = bytesReceived
        self.bytes_total = bytesTotal

        # Update progress bar value and text
        self.progressBar.setValue(int((bytesReceived / bytesTotal) * 100))

        self.label.setText(f'Downloading {self.filename}... ({self.bytes_received} of {self.bytes_total} bytes)')

    def download_finished(self):
        self.file.close()

    def delete_download(self):
        try:
            os.remove(self.filepath)
            print(f"File '{self.filename}' deleted successfully.")
        except Exception as e:
            print(f"Error deleting file '{self.filename}': {e}")

        # Close the dialog
        self.close()
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

        self.downloads = []

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

    def listview_clicked(self, index):
        url, filename = self.downloads[index.row()]
        dialog = DownloadDialog(url, filename, self)
        dialog.exec_()

    def rowCount(self, parent=None):
        return len(self.downloads)

    def data(self, index, role=None):
        if role == Qt.DisplayRole:
            return self.downloads[index.row()][1]
        
    

