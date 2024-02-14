from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QFileDialog, QMessageBox, QApplication, QFrame, QHBoxLayout
from PyQt5.QtCore import Qt
from pytube import YouTube
import os

class SaveFromNet(QDialog):
    def __init__(self, parent=None):
        super(SaveFromNet, self).__init__(parent)

        # Set the window flags to make it frameless
        self.setWindowFlags(Qt.FramelessWindowHint)

        layout = QVBoxLayout()

        # Add a title bar with a title and close button
        title_bar = QFrame(self)
        title_bar.setStyleSheet("background-color: none;")
        title_bar.setFixedHeight(40)
        title_layout = QHBoxLayout(title_bar)

        title_label = QLabel("Media Downloader", self)
        title_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        title_layout.addWidget(title_label)

        close_button = QPushButton("X", self)
        close_button.setFixedSize(30, 30)
        close_button.clicked.connect(self.close)
        title_layout.addWidget(close_button, alignment=Qt.AlignRight)

        layout.addWidget(title_bar)

        self.label = QLabel("Enter the URL of the media you want to save:")
        layout.addWidget(self.label)

        self.url_bar = QLineEdit()
        layout.addWidget(self.url_bar)

        self.file_path_label = QLabel("Select the path to save the media:")
        layout.addWidget(self.file_path_label)

        self.file_path_edit = QLineEdit()
        layout.addWidget(self.file_path_edit)

        self.file_path_button = QPushButton("Choose...")
        self.file_path_button.clicked.connect(self.select_file_path)
        layout.addWidget(self.file_path_button)

        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_media)
        layout.addWidget(self.save_button)

        self.setLayout(layout)

    def select_file_path(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Select Save Location", "", "All Files (*)")
        if file_path:
            self.file_path_edit.setText(file_path)

    def download_youtube_video(self, url, file_path):
        try:
            yt = YouTube(url)
            video_title = yt.title
            save_path = os.path.join(file_path, f"{video_title}.mp4")
            
            if os.path.exists(save_path):
                raise Exception("File already exists. Choose a different save location.")
            
            yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first().download(output_path=file_path)
            return video_title
        except Exception as e:
            raise Exception(f"Failed to download YouTube video: {str(e)}")

    def save_media(self):
        url = self.url_bar.text()
        file_path = self.file_path_edit.text()

        if not url or not file_path:
            QMessageBox.warning(self, "Error", "URL and file path must be specified.")
            return

        try:
            video_title = self.download_youtube_video(url, file_path)
            QMessageBox.information(self, "Success", f"Media '{video_title}' saved successfully.")
            self.accept()  # Close the dialog

        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to download media: {str(e)}")

if __name__ == "__main__":
    app = QApplication([])

    media_downloader = SaveFromNet()
    result = media_downloader.exec_()

    app.exec_()
