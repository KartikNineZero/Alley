from PyQt5.QtWidgets import QWidget, QVBoxLayout, QListWidget, QListWidgetItem, QPushButton, QLineEdit, QMessageBox
from PyQt5.QtCore import QSize, Qt, QUrl

class BookmarksManager(QWidget):
    def __init__(self, browser):
        super().__init__()

        self.browser = browser
        self.bookmarks = []

        layout = QVBoxLayout()

        self.list_widget = QListWidget()
        self.list_widget.itemClicked.connect(self.on_item_clicked)
        self.list_widget.setFixedSize(300, 500)
        layout.addWidget(self.list_widget)

        input_layout = QVBoxLayout()

        self.input_url = QLineEdit()
        self.input_url.setPlaceholderText('URL')
        input_layout.addWidget(self.input_url)

        self.input_title = QLineEdit()
        self.input_title.setPlaceholderText('Title')
        input_layout.addWidget(self.input_title)

        add_button = QPushButton('Add Bookmark')
        add_button.clicked.connect(self.add_bookmark)
        input_layout.addWidget(add_button)

        layout.addLayout(input_layout)

        self.setLayout(layout)

        self.load_bookmarks()

    def load_bookmarks(self):
        self.list_widget.clear()

        for bookmark in self.bookmarks:
            self.add_bookmark_item(bookmark['title'], bookmark['url'])

    def add_bookmark_item(self, title, url):
        item = QListWidgetItem(title)
        item.setData(Qt.UserRole, url)
        self.list_widget.addItem(item)

    def add_bookmark(self):
        url = self.input_url.text()
        title = self.input_title.text()

        if not url or not title:
            QMessageBox.warning(self, 'Error', 'Please fill in both the URL and Title fields.')
            return

        self.bookmarks.append({'title': title, 'url': QUrl(url)})
        self.load_bookmarks()

    def on_item_clicked(self, item):
        url = item.data(Qt.UserRole)
        self.browser.setUrl(url)

    def sizeHint(self):
        return QSize(600, 600)
