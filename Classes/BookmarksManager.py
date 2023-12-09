from PyQt5.QtWidgets import QWidget, QVBoxLayout, QListWidget, QListWidgetItem, QPushButton, QLineEdit, QMessageBox, QMenu, QAction, QInputDialog
from PyQt5.QtCore import Qt, QSettings, QUrl

class BookmarksManager(QWidget):
    def __init__(self, browser):
        super().__init__()

        self.browser = browser
        self.bookmarks = []

        layout = QVBoxLayout()

        self.list_widget = QListWidget()
        self.list_widget.itemClicked.connect(self.on_item_clicked)
        self.list_widget.setFixedSize(300, 500)
        self.list_widget.setStyleSheet(
            """
            QListWidget {
                background-color: #F5F5F5;
                border: 1px solid #CCCCCC;
            }

            QListWidget:item {
                padding: 5px;
            }
            """
        )
        self.list_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.list_widget.customContextMenuRequested.connect(self.show_context_menu)
        layout.addWidget(self.list_widget)

        input_layout = QVBoxLayout()

        self.input_url = QLineEdit()
        self.input_url.setPlaceholderText('URL')
        self.input_url.setStyleSheet("QLineEdit { padding: 5px; }")
        self.input_url.setMaximumWidth(280)
        input_layout.addWidget(self.input_url)

        self.input_title = QLineEdit()
        self.input_title.setPlaceholderText('Title')
        self.input_title.setStyleSheet("QLineEdit { padding: 5px; }")
        self.input_title.setMaximumWidth(280)
        input_layout.addWidget(self.input_title)

        add_button = QPushButton('Add Bookmark')
        add_button.clicked.connect(self.add_bookmark)
        add_button.setMaximumWidth(280)
        add_button.setStyleSheet(
            """
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 5px;
            }
            """
        )
        input_layout.addWidget(add_button)

        layout.addLayout(input_layout)

        self.setLayout(layout)

        # Load bookmarks
        self.load_bookmarks()

    def load_bookmarks(self):
        settings = QSettings('MySoft', 'MyApp')
        settings.beginGroup('Bookmarks')

        for key in settings.childKeys():
            bookmark = settings.value(key)
            self.add_bookmark_item(bookmark['title'], bookmark['url'])

        settings.endGroup()

    def save_bookmarks(self):
        settings = QSettings('MySoft', 'MyApp')
        settings.beginGroup('Bookmarks')

        for i in range(self.list_widget.count()):
            bookmark_item = self.list_widget.item(i)
            settings.setValue(str(i), {'title': bookmark_item.text(), 'url': bookmark_item.data(Qt.UserRole)})

        settings.endGroup()

    def add_bookmark(self):
        url = self.input_url.text()
        title = self.input_title.text()

        if not url or not title:
            QMessageBox.warning(self, 'Error', 'URL and Title must be filled out')
            return

        self.add_bookmark_item(title, url)

        # Clear input fields
        self.input_url.clear()
        self.input_title.clear()

        # Save bookmarks
        self.save_bookmarks()

    def add_bookmark_item(self, title, url):
        item = QListWidgetItem(title)
        item.setData(Qt.UserRole, url)
        self.list_widget.addItem(item)

    def on_item_clicked(self, item):
        self.browser.load(QUrl(item.data(Qt.UserRole)))

    def show_context_menu(self, position):
        item = self.list_widget.itemAt(position)
        if not item:
            return

        menu = QMenu(self)
        remove_action = QAction('Remove Bookmark', self)
        remove_action.triggered.connect(lambda: self.remove_bookmark(item))
        menu.addAction(remove_action)

        edit_action = QAction('Edit Bookmark', self)
        edit_action.triggered.connect(lambda: self.edit_bookmark(item))
        menu.addAction(edit_action)

        menu.exec_(self.list_widget.mapToGlobal(position))

    def remove_bookmark(self, item):
        self.list_widget.takeItem(self.list_widget.row(item))
        self.save_bookmarks()

    def edit_bookmark(self, item):
        current_title = item.text()
        current_url = item.data(Qt.UserRole)

        new_title, ok1 = QInputDialog.getText(self, 'Edit Bookmark', 'Enter new title:', QLineEdit.Normal, current_title)
        new_url, ok2 = QInputDialog.getText(self, 'Edit Bookmark', 'Enter new URL:', QLineEdit.Normal, current_url)

        if ok1 and ok2:
            item.setText(new_title)
            item.setData(Qt.UserRole, new_url)
            # Save bookmarks
            self.save_bookmarks()
