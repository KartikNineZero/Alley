import sys
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtNetwork import QNetworkCookie
from PyQt5.QtGui import *
from PyQt5.QtNetwork import *
import requests
from Classes.Chatbot import CustomChatbot
from Classes.BookmarksManager import BookmarksManager
from Classes.MediaDownloader import SaveFromNet
from PyQt5.QtWidgets import QDialog
import json

class CustomWebEnginePage(QWebEnginePage):
    def setCookie(self, filename):
        cookies = self.profile().cookieStore().getAllCookies()
        for cookie in cookies:
            if cookie.name() == b"download_warning":
                self.profile().cookieStore().deleteAllCookies()
                cookie = QNetworkCookie(b"download_warning", b"a; filename*=UTF-8''{}".format(filename))
                cookie.setPath(b"/")
                cookie.setHttpOnly(False)
                cookie.setSecure(False)
                cookie.setSameSite(QNetworkCookie.SameSiteLax)
                self.profile().cookieStore().setCookie(cookie)

class MainWindow(QMainWindow):
    def __init__(self):

        super(MainWindow, self).__init__()

        self.setWindowTitle('Alley Browser')
        self.setWindowIcon(QIcon('Icons/Logo.png'))

        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.setCentralWidget(self.tabs)

        self.tabs.currentChanged.connect(self.update_url_from_active_tab)

        
        toolbar = QToolBar()
        self.addToolBar(toolbar)
        self.tabs.currentChanged.connect(self.update_url_from_active_tab)
        self.tabs.currentChanged.connect(self.update_url_from_tab)

        back_btn = QAction('⮜', self)
        back_btn.triggered.connect(lambda: self.current_browser().back() if self.current_browser() else None)
        toolbar.addAction(back_btn)

        forward_btn = QAction('⮞', self)
        forward_btn.triggered.connect(lambda: self.current_browser().forward() if self.current_browser() else None)
        toolbar.addAction(forward_btn)

        reload_btn = QAction('⟳', self)
        reload_btn.triggered.connect(lambda: self.current_browser().reload() if self.current_browser() else None)
        toolbar.addAction(reload_btn)

        home_btn = QAction('⌂', self)
        home_btn.triggered.connect(self.navigate_home)
        toolbar.addAction(home_btn)

        add_tab_btn = QAction('+', self)
        add_tab_btn.triggered.connect(self.add_tab)
        toolbar.addAction(add_tab_btn)

        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        toolbar.addWidget(self.url_bar)

        self.dropdown_menu = QMenu(self)
        self.bookmarks_action = QAction('Bookmarks', self)
        self.history_action = QAction('History', self)
        self.dropdown_menu.addAction(self.bookmarks_action)
        self.dropdown_menu.addAction(self.history_action)

        dropdown_btn = QToolButton(self)
        dropdown_btn.setMenu(self.dropdown_menu)
        dropdown_btn.setPopupMode(QToolButton.InstantPopup)
        dropdown_btn.setIcon(QIcon('Icons/menu.png'))

        toolbar.addWidget(dropdown_btn)

        self.bookmarks_action.triggered.connect(self.show_bookmarks)
        self.history_action.triggered.connect(self.show_history)

        self.chatbot = CustomChatbot()

        chatbot_action = QAction('Chatbot', self)
        chatbot_action.triggered.connect(self.open_chatbot_overlay)
        self.dropdown_menu.addAction(chatbot_action)

        self.downloaded_files = []
        self.downloads_action = QAction('Downloads', self)
        self.downloads_action.triggered.connect(self.show_downloads)
        self.dropdown_menu.addAction(self.downloads_action)

        self.media_downloader = SaveFromNet()

        media_downloader_action = QAction('Media Downloader', self)
        media_downloader_action.triggered.connect(self.open_media_downloader)
        self.dropdown_menu.addAction(media_downloader_action)

        self.add_tab()

        self.chat_overlay = ChatOverlay(chatbot=self.chatbot)
        self.overlay_widget = OverlayWidget(self.chat_overlay, parent=self)
        self.overlay_widget.hide()

        self.load_tabs_data()  # Load saved tabs when the application starts

    def update_url_from_active_tab(self, index):
        current_browser = self.tabs.widget(index)
        if current_browser:
            self.url_bar.setText(current_browser.url().toString())
    
    def load_tabs_data(self):
        try:
            with open('tabs_data.json', 'r') as file:
                tabs_data = json.load(file)
                if not tabs_data:  # Check if the file is empty dee
                    print("No data found in tabs_data.json")
                    return
                for tab_data in tabs_data:
                    if tab_data['url'] != 'https://google.com':
                        self.add_tab(url=tab_data['url'])
        except FileNotFoundError:
            print("File tabs_data.json not found.")
        except json.JSONDecodeError:
            print("Error decoding JSON data in tabs_data.json")

    def save_tabs_data(self):
        tabs_data = []
        for i in range(self.tabs.count()):
            browser = self.tabs.widget(i)
            url = browser.url().toString()
            tabs_data.append({'url': url})

        with open('tabs_data.json', 'w') as file:
            json.dump(tabs_data, file)

    def closeEvent(self, event):
        self.save_tabs_data()  # Save tabs data when the application is closed
        event.accept()



    def make_small_components(self):
        # Decrease the font size of labels, buttons, or other components
        self.decrease_font_size(self)

    def enlarge_components(self):
        # Increase the font size of labels, buttons, or other components
        self.increase_font_size(self)

    def increase_font_size(self, widget, factor=1.2):
        font = widget.font()
        font.setPointSizeF(font.pointSizeF() * factor)
        widget.setFont(font)

        for child in widget.findChildren(QWidget):
            self.increase_font_size(child, factor)
    
    def decrease_font_size(self, widget, factor=1.2):
        font = widget.font()
        font.setPointSizeF(font.pointSizeF() / factor)
        widget.setFont(font)

        for child in widget.findChildren(QWidget):
            self.decrease_font_size(child, factor)

    def current_browser(self):
        return self.tabs.currentWidget() if self.tabs.count() > 0 else None

    def add_tab(self, url=None):  # Set url as an optional parameter
        browser = QWebEngineView()
        browser.setPage(CustomWebEnginePage())
        if url:
            browser.setUrl(QUrl(url))  # Set the URL if provided
        else:
            browser.setUrl(QUrl('https://google.com'))  # Default URL
        self.tabs.addTab(browser, 'New Tab')
        self.tabs.setCurrentWidget(browser)
        self.tabs.setTabText(self.tabs.currentIndex(), 'Loading...')
        browser.titleChanged.connect(
            lambda title, browser=browser: self.tabs.setTabText(self.tabs.indexOf(browser), title))
        if self.current_browser():
            browser.urlChanged.connect(
                lambda url, browser=browser: self.update_url(url) if self.current_browser() == browser else None)

    def close_tab(self, index):
        browser_widget = self.tabs.widget(index)

        if browser_widget.url().host() == "www.youtube.com":
            browser_widget.page().runJavaScript("document.getElementsByTagName('video')[0].pause();")

        if self.tabs.count() < 2:
            self.close()
        else:
            self.tabs.removeTab(index)
            browser_widget.deleteLater()

    def navigate_home(self):
        if self.current_browser():
            self.current_browser().setUrl(QUrl('https://www.google.com'))

    def navigate_to_url(self):
        if self.current_browser():
            input_text = self.url_bar.text()

            if '.com' in input_text:
                url = input_text
            else:
                url = 'https://www.google.com/search?q=' + input_text

            if not url.startswith('http://') and not url.startswith('https://'):
                url = 'https://' + url

            self.current_browser().setUrl(QUrl(url))

    def update_url(self, q):
        if self.sender() == self.current_browser():
            self.url_bar.setText(q.toString())
            self.url_bar.setCursorPosition(0)

    def update_url_from_tab(self, index):
        current_browser = self.tabs.widget(index)
        if current_browser:
            self.update_url(current_browser.url())

    def show_bookmarks(self):
        if not hasattr(self, 'bookmarks_manager'):
            self.bookmarks_manager = BookmarksManager(browser=self.current_browser())
            self.layout().addWidget(self.bookmarks_manager)
        self.bookmarks_manager.setVisible(not self.bookmarks_manager.isVisible())

    def show_cookies(self):
        if not hasattr(self, 'cookie_overlay'):
            self.cookie_overlay = CookieOverlay(cookie_jar=self.cookie_jar)
            self.layout().addWidget(self.cookie_overlay)
            self.cookie_jar.cookies_changed.connect(self.cookie_overlay.update_cookies)

        self.cookie_overlay.setVisible(not self.cookie_overlay.isVisible())

    def show_history(self):
        if self.current_browser():
            history_menu = QMenu(self)
            for entry in self.current_browser().history().items():
                action = history_menu.addAction(entry.title())
                action.triggered.connect(lambda _, url=entry.url(): self.current_browser().setUrl(url))
            history_menu.exec_(QCursor.pos())

    def open_chatbot_overlay(self):
        self.overlay_widget.show()

    def open_media_downloader(self):
        result = self.media_downloader.exec_()
        if result == QDialog.Accepted:
            filename = self.media_downloader.get_filename()
            if filename:
                self.downloaded_files.append(filename)
                QMessageBox.information(self, "Download Complete", f"File '{filename}' downloaded successfully.")

    def show_downloads(self):
        if not self.downloaded_files:
            QMessageBox.information(self, "Downloads", "No files downloaded yet.")
            return

        downloads_text = "\n".join(self.downloaded_files)
        QMessageBox.information(self, "Downloads", f"Downloaded Files:\n{downloads_text}")

    def update_url_from_active_tab(self, index):
        current_browser = self.tabs.widget(index)
        if current_browser:
            self.url_bar.setText(current_browser.url().toString())

class CustomChatbot:
    def get_response(self, user_input):
        return "This is a placeholder response."

class SaveFromNet:
    def exec_(self):
        return QDialog.Accepted

class ChatOverlay(QWidget):
    def __init__(self, chatbot, parent=None):
        super(ChatOverlay, self).__init__(parent)

        self.chatbot = chatbot
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("Type your message...")
        layout.addWidget(self.user_input)

        submit_button = QPushButton("Submit")
        submit_button.clicked.connect(self.get_chatbot_response)
        layout.addWidget(submit_button)

        self.chat_display = QTextBrowser()
        layout.addWidget(self.chat_display)

        self.setLayout(layout)

    def get_chatbot_response(self):
        user_input = self.user_input.text()
        response = self.chatbot.get_response(user_input)
        self.chat_display.append(f"You: {user_input}")
        self.chat_display.append(f"Chatbot: {response}")
        self.user_input.clear()

class OverlayWidget(QWidget):
    def __init__(self, content_widget, parent=None):
        super(OverlayWidget, self).__init__(parent)

        self.content_widget = content_widget
        self.setWindowFlags(Qt.Window | Qt.CustomizeWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setStyleSheet("background-color: rgba(255, 255, 255, 200); border: 1px solid black;")

        layout = QVBoxLayout()
        layout.addWidget(self.content_widget)
        self.setLayout(layout)

    def showEvent(self, event):
        self.setGeometry(
            self.parent().geometry().x(),
            self.parent().geometry().y(),
            self.parent().geometry().width(),
            self.parent().geometry().height()
        )

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName('Alley')
    app.setApplicationDisplayName('Alley')
    app.setOrganizationName('SDCCE')
    window = MainWindow()
    window.showMaximized()
    sys.exit(app.exec_())
