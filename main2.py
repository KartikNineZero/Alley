import json
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

# Custom WebEnginePage to handle cookies
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
                # Set the SameSite attribute to Lax
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

        self.tabs.setStyleSheet("""
    QTabWidget::pane {
        background-color: #4d31b6; /* Edge Blue Color */
        border-radius: 0; /* Remove border-radius */
    }
    
    QTabWidget::tab-bar {
        alignment: left;
    }
    QTabBar::tab {
        background-color: #5d3bb6; /* Lightened Blue Color */
        border: none; /* Remove border */
        padding: 8px 20px;
        color: white;
    }
    QTabBar::tab:selected {
        background-color: #b765d2; /* Lightened Selected Tab Background Color */
    }
""")
        
        toolbar = QToolBar()
        toolbar.setStyleSheet("""
    QToolBar {
        background-color: #4d31b6; /* Edge Blue Color */
        color: white;
        spacing: 10px;
        border-radius: none; /* Add border-radius for a curved toolbar */
    }
    QToolButton {
        background-color: #4d31b6; /* Edge Blue Color */
        border: none;
        color: white;
        font-size: 20px;
        padding: 8px;
        border-radius: 5px; /* Add border-radius for a curved button */
    }
    QLineEdit {
        height: 30px;
        border: 1px solid #000000; /* Edge Blue Color */
        padding: 2px;
        color: white; /* Set text color to white */
        background-color: black; /* Set background color to black */
        font-size: 16px;
        border-radius: 5px; /* Add border-radius for a curved input field */
    }
    QMenu {
        background-color: #FFFF;
        font-size: 16px;
        border-radius: 5px; /* Add border-radius for a curved menu */
    }
    QMenu::item {
        padding: 8px 20px;
        border-radius: 5px; /* Add border-radius for curved menu items */
    }
    QMenu::item:selected {
        background-color: #2a1f68; /* Selected Item Background Color */
    }
    QTabMenu{
        
    }
""")
        self.addToolBar(toolbar)
        

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
        self.url_bar.setFixedHeight(30)
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        toolbar.addWidget(self.url_bar)

        self.dropdown_menu = QMenu(self)
        self.bookmarks_action = QAction('Bookmarks', self)
        self.cookies_action = QAction('Cookies', self)
        self.history_action = QAction('History', self)
        self.dropdown_menu.addAction(self.bookmarks_action)
        self.dropdown_menu.addAction(self.cookies_action)
        self.dropdown_menu.addAction(self.history_action)

        dropdown_btn = QToolButton(self)
        dropdown_btn.setMenu(self.dropdown_menu)
        dropdown_btn.setPopupMode(QToolButton.InstantPopup)
        dropdown_btn.setIcon(QIcon('Icons/menu.png'))

        # Replace 'Icons/bookmarks_icon.png' with the actual path to your bookmarks icon
        bookmarks_icon_path = 'Icons/bm.png'
        self.bookmarks_action.setIcon(QIcon(bookmarks_icon_path))

        # Replace 'Icons/cookies_icon.png' with the actual path to your cookies icon
        cookies_icon_path = 'Icons/c.png'
        self.cookies_action.setIcon(QIcon(cookies_icon_path))

        # Replace 'Icons/history_icon.png' with the actual path to your history icon
        history_icon_path = 'Icons/h.png'
        self.history_action.setIcon(QIcon(history_icon_path))

        toolbar.addWidget(dropdown_btn)

        self.bookmarks_action.triggered.connect(self.show_bookmarks)
        self.cookies_action.triggered.connect(self.show_cookies)
        self.history_action.triggered.connect(self.show_history)

        # Chatbot instance
        self.chatbot = CustomChatbot()

        # Action for opening chatbot overlay
        chatbot_icon_path = 'Icons/cb.png'
        chatbot_action = QAction('Chatbot', self)
        chatbot_action.triggered.connect(self.open_chatbot_overlay)
        self.dropdown_menu.addAction(chatbot_action)

        # Downloads action in the dropdown
        self.downloaded_files = []  # List to keep track of downloaded files
        downloads_icon_path = 'Icons/d.png'
        self.downloads_action = QAction('Downloads', self)
        self.downloads_action.triggered.connect(self.show_downloads)
        self.dropdown_menu.addAction(self.downloads_action)

        # Media Downloader instance
        self.media_downloader = SaveFromNet()

        # Media Downloader action in the dropdown
        media_downloader_icon_path = 'Icons/md.png'
        media_downloader_action = QAction('Media Downloader', self)
        media_downloader_action.triggered.connect(self.open_media_downloader)
        self.dropdown_menu.addAction(media_downloader_action)

        self.add_tab()

        # Chatbot overlay
        self.chat_overlay = ChatOverlay(chatbot=self.chatbot)
        self.overlay_widget = OverlayWidget(self.chat_overlay, parent=self)
        self.overlay_widget.hide()

        '''# Enlarge button
        enlarge_btn = QAction('Enlarge', self)
        enlarge_btn.triggered.connect(self.enlarge_components)
        toolbar.addAction(enlarge_btn)
        
        # Make Small button
        make_small_btn = QAction('Make Small', self)
        make_small_btn.triggered.connect(self.make_small_components)
        toolbar.addAction(make_small_btn)'''

        self.load_tabs_data()  # Load saved tabs when the application starts

    def update_url_from_active_tab(self, index):
        current_browser = self.tabs.widget(index)
        if current_browser:
            self.url_bar.setText(current_browser.url().toString())
    
    def load_tabs_data(self):
        try:
            with open('tabs_data.json', 'r') as file:
                tabs_data = json.load(file)
                if not tabs_data:  # Check if the file is empty
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

    def show_bookmarks(self):
        if not hasattr(self, 'bookmarks_manager'):
            self.bookmarks_manager = BookmarksManager(browser=self.current_browser())
            self.layout().addWidget(self.bookmarks_manager)
        self.bookmarks_manager.setVisible(not self.bookmarks_manager.isVisible())

    def show_cookies(self):
        print("Cookies action triggered")

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
        # Show the Media Downloader dialog
        result = self.media_downloader.exec_()
        if result == QDialog.Accepted:
            # Handle downloaded file
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


class ChatOverlay(QWidget):
    def __init__(self, chatbot, parent=None):
        super(ChatOverlay, self).__init__(parent)

        self.chatbot = chatbot
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.user_input = QLineEdit()
        self.user_input.setFixedHeight(30)
        self.user_input.setPlaceholderText("Type your message...")
        layout.addWidget(self.user_input)

        submit_button = QPushButton("Submit")
        submit_button.setFixedSize(80, 30)
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
        #self.setStyleSheet("background-color: rgba(255, 255, 255); border: 1px solid black;")  
        
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

    def create_dropdown_menu(self):
        menu = QMenu(self)
        menu.setStyleSheet(
            """
            QMenu {
                background-color: #4d31b6; /* Menu Background Color */
                color: white;
                border: 1px solid #2a1f68; /* Border Color */
            }
            QMenu::item {
                padding: 8px 20px;
            }
            QMenu::item:selected {
                background-color: #2a1f68; /* Selected Item Background Color */
            }
            """
        )

        # Add actions to the menu with icons
        actions = [
            ("Bookmarks", self.show_bookmarks,"Icons/bm.png"),
            ("Cookies", self.show_cookies, "Icons/d.png"),
            ("History", self.show_history, "Icons/h.png"),
            ("Chatbot", self.open_chatbot_overlay, "Icons/cb.png"),
            ("Downloads", self.show_downloads, "Icons/d.png"),
            ("Media Downloader", self.open_media_downloader, "Icons/md.png"),
        ]

        for action_text, slot, icon_path in actions:
            action = QAction(QIcon(icon_path), action_text, self)
            action.triggered.connect(slot)
            menu.addAction(action)

        # Add a separator between regular actions and settings
        menu.addSeparator()

        # Add settings action with a gear icon
        settings_action = QAction(QIcon("Icons/s.png"), "Settings", self)
        settings_action.triggered.connect(self.open_settings)
        menu.addAction(settings_action)

        return menu

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName('Alley')
    app.setApplicationDisplayName('Alley')
    app.setOrganizationName('SDCCE')
    window = MainWindow()
    window.showMaximized()
    sys.exit(app.exec_())
