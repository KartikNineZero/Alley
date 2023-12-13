import sys
import json
from urllib.parse import urlparse

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
                cookie = QNetworkCookie(b"download_warning",     b"a; filename*=UTF-8''{}".format(filename))
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
        background-color: #3ab4e1; /* Edge Blue Color */
        border-radius: 0; /* Remove border-radius */
    }
    
    QTabWidget::tab-bar {
        alignment: left;
    }
    QTabBar::tab {
        background-color: #3ab4e1; /* Lightened Blue Color */
        border: none; /* Remove border */
        padding: 8px 20px;
        color: white;
        min-width: 120px;
    }
    QTabBar::tab:selected {
        background-color: #4f93e6; /* Lightened Selected Tab Background Color */
    }
""")
        
        toolbar = QToolBar()
        toolbar.setStyleSheet("""
    QToolBar {
        background-color: #3ab4e1; /* Edge Blue Color */
        color: white;
        spacing: 10px;
        border-radius: none; /* Add border-radius for a curved toolbar */
    }
    QToolButton {
        background-color: #3ab4e1; /* Edge Blue Color */
        border: none;
        color: white;
        font-size: 20px;
        padding: 8px;
        border-radius: 5px; /* Add border-radius for a curved button */
    }
    QToolButton:hover {
	    background-color: #3498db; /* Change color on hover */
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
        icon_width = 20
        icon_height = 20
        self.tabs.currentChanged.connect(self.update_url_from_active_tab)
        self.tabs.currentChanged.connect(self.update_url_from_tab)

        back_btn = QAction(QIcon(QPixmap('Icons/la.png').scaled(icon_width, icon_height)), '⮜', self)
        back_btn.triggered.connect(lambda: self.current_browser().back() if self.current_browser() else None)
        toolbar.addAction(back_btn)

        forward_btn = QAction(QIcon(QPixmap('Icons/ra.png').scaled(icon_width, icon_height)), '⮞', self)
        forward_btn.triggered.connect(lambda: self.current_browser().forward() if self.current_browser() else None)
        toolbar.addAction(forward_btn)

        reload_btn = QAction(QIcon(QPixmap('Icons/r.png').scaled(icon_width, icon_height)), '⟳', self)
        reload_btn.triggered.connect(lambda: self.current_browser().reload() if self.current_browser() else None)
        toolbar.addAction(reload_btn)

        home_btn = QAction(QIcon(QPixmap('Icons/home.png').scaled(icon_width, icon_height)), '⌂', self)
        home_btn.triggered.connect(self.navigate_home)
        toolbar.addAction(home_btn)

        add_tab_btn = QAction(QIcon(QPixmap('Icons/add.png').scaled(icon_width, icon_height)), '+', self)
        add_tab_btn.triggered.connect(self.add_tab)
        toolbar.addAction(add_tab_btn)
        
        self.url_bar = QLineEdit()
        self.url_bar.setFixedHeight(30)
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        self.url_bar.setStyleSheet("""
            height: 30px;
            border: 1px solid #000000; /* Edge Blue Color */
            padding: 5px 10px;
            color: white; /* Set text color to white */
            background-color: black; /* Set background color to black */
            font-size: 13px;
            border-radius: 5px; /* Add border-radius for rounded corners */
        """)
        toolbar.addWidget(self.url_bar)

        zoom_in_action = QAction(QIcon(QPixmap('Icons/p.png').scaled(icon_width, icon_height)), '+', self)
        zoom_in_action.setShortcut('Ctrl++')
        zoom_in_action.triggered.connect(self.zoom_in)
        toolbar.addAction(zoom_in_action)
	
	    # Zoom Out action
        zoom_out_action = QAction(QIcon(QPixmap('Icons/rm.png').scaled(icon_width, icon_height)), '-', self)
        zoom_out_action.setShortcut('Ctrl+-')
        zoom_out_action.triggered.connect(self.zoom_out)
        toolbar.addAction(zoom_out_action)

        self.dropdown_menu = QMenu(self)
        self.bookmarks_action = QAction('Bookmarks', self)
        self.history_action = QAction('History', self)
        self.customize_ui_action = QAction('Customize', self)
        self.dropdown_menu.addAction(self.bookmarks_action)
        self.dropdown_menu.addAction(self.history_action)

        dropdown_btn = QToolButton(self)
        dropdown_btn.setMenu(self.dropdown_menu)
        dropdown_btn.setPopupMode(QToolButton.InstantPopup)
        dropdown_btn.setIcon(QIcon('Icons/menu.png'))

        dropdown_btn.setStyleSheet("""
    QToolButton {
        background-color: #3ab4e1; /* Change to your desired background color */
        border: none;
        color: white;
        font-size: 20px;
        padding: 8px;
        border-radius: 5px; /* Add border-radius for a curved button */
    }
    QToolButton:hover {
        background-color: #3498db; /* Change color on hover */
    }
    QToolButton::menu-indicator {
        image: none; /* Hide the menu indicator arrow */
    }
    QMenu {
        background-color: #3498db; /* Change to your desired background color */
        font-size: 16px;
        border-radius: 5px; /* Add border-radius for a curved menu */
    }
    QMenu::item {
        background-color: #3498db; /* Change to your desired background color */
        padding: 8px 20px;
        border-radius: 5px; /* Add border-radius for curved menu items */
    }
    QMenu::item:selected {
        background-color: #2980b9; /* Selected Item Background Color */
    }
    QMenuBar {
        background-color: #2980b9; /* Background color for the menu bar */
    }
""")
        dropdown_menu_style = """
    QMenu {
        background-color: #000; /* Change to your desired background color */
        font-size: 16px;
        border: 3px solid #fff;
        border-radius: 5px; /* Add border-radius for a curved menu */
        padding: 10px;
    }
    QMenu::item {
        background-color: #000; /* Change to your desired background color */
        padding: 8px 20px;
        border-radius: 5px; /* Add border-radius for curved menu items */
        color: white; /* Set text color to white */
        
    }
    QMenu::item:selected {
        background-color: #3498db; /* Selected Item Background Color */
    }
"""

        self.dropdown_menu.setStyleSheet(dropdown_menu_style)

        # Replace 'Icons/bookmarks_icon.png' with the actual path to your bookmarks icon
        bookmarks_icon_path = 'Icons/bm.png'
        self.bookmarks_action.setIcon(QIcon(bookmarks_icon_path))


        # Replace 'Icons/history_icon.png' with the actual path to your history icon
        history_icon_path = 'Icons/h.png'
        self.history_action.setIcon(QIcon(history_icon_path))

        toolbar.addWidget(dropdown_btn)

        self.bookmarks_action.triggered.connect(self.show_bookmarks)
        self.history_action.triggered.connect(self.show_history)

        # customize
        self.customize_ui_action = QAction(QIcon('Icons/dm.png'), 'Dark', self)
        self.customize_ui_action.triggered.connect(self.open_customize_dialog)
        self.dropdown_menu.addAction(self.customize_ui_action) 

        # Connect CustomizeDialog to main window for color changes
        self.customize_dialog = CustomizeDialog(self)
        self.customize_ui_action.triggered.connect(self.customize_dialog.show)
        
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
        self.downloads_action = QAction(QIcon(downloads_icon_path),'Downloads', self)
        self.downloads_action.triggered.connect(self.show_downloads)
        self.dropdown_menu.addAction(self.downloads_action)

        # Media Downloader instance
        self.media_downloader = SaveFromNet()

        # Media Downloader action in the dropdown
        media_downloader_icon_path = 'Icons/md.png'
        media_downloader_action = QAction(QIcon(media_downloader_icon_path),'Media Downloader', self)
        media_downloader_action.triggered.connect(self.open_media_downloader)
        self.dropdown_menu.addAction(media_downloader_action)

        self.add_tab()

        # Chatbot overlay
        self.chat_overlay = ChatOverlay(chatbot=self.chatbot)
        self.chat_overlay.setVisible(False)  # Initially hide the chat overlay
        self.layout().addWidget(self.chat_overlay)  # Add to the main window layout
       
        self.load_tabs_data()  # Load saved tabs when the application starts

    def update_url_from_active_tab(self, index):
        current_browser = self.tabs.widget(index)
        if current_browser:
            self.url_bar.setText(current_browser.url().toString())
    
    def open_settings(self):
        # Replace this with your actual settings implementation
        QMessageBox.information(self, "Settings", "Placeholder for settings. Implement your settings logic here.")

    def current_browser(self):
        return self.tabs.currentWidget() if self.tabs.count() > 0 else None

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
            # Exclude 'https://www.google.com/' from being saved
            if url != 'https://www.google.com/':
                tabs_data.append({'url': url})

        with open('tabs_data.json', 'w') as file:
            json.dump(tabs_data, file)

    def closeEvent(self, event):
        self.save_tabs_data()  # Save tabs data when the application is closed
        event.accept()

    def current_browser(self):
        return self.tabs.currentWidget() if self.tabs.count() > 0 else None

    def add_tab(self, url=None):
    # Check if there are no tabs open and the JSON file is empty or not found
        if self.tabs.count() == 0 or (not self.is_tabs_data_file_found() or self.is_tabs_data_empty()):
            self.open_default_tab()
        else:
            browser = QWebEngineView()
            browser.setPage(CustomWebEnginePage())
            
            if url:
                browser.setUrl(QUrl(url))
            else:
                browser.setUrl(QUrl('https://google.com'))
            
            self.tabs.addTab(browser, 'New Tab')
            self.tabs.setCurrentWidget(browser)
            self.tabs.setTabText(self.tabs.currentIndex(), 'Loading...')
            
            browser.titleChanged.connect(lambda title, browser=browser: self.update_tab_title(browser))

            if self.current_browser():
                browser.urlChanged.connect(lambda url, browser=browser: self.update_url(url) if 
                    self.current_browser() == browser else None)

    # Helper methods for file and data checks
    def is_tabs_data_file_found(self):
        try:
            with open('tabs_data.json', 'r') as file:
                return True
        except FileNotFoundError:
            return False
    def is_tabs_data_empty(self):
        try:
            with open('tabs_data.json', 'r') as file:
                tabs_data = json.load(file)
                return not bool(tabs_data)
        except json.JSONDecodeError:
            return True
        
    def open_default_tab(self):
        browser = QWebEngineView()
        browser.setPage(CustomWebEnginePage())
        browser.setUrl(QUrl('https://google.com'))
        
        self.tabs.addTab(browser, 'New Tab')
        self.tabs.setCurrentWidget(browser)
        self.tabs.setTabText(self.tabs.currentIndex(), 'Loading...')
        
        browser.titleChanged.connect(lambda title, browser=browser: self.update_tab_title(browser))

        if self.current_browser():
            browser.urlChanged.connect(lambda url, browser=browser: self.update_url(url) if 
                self.current_browser() == browser else None)
            

    def update_tab_title(self, browser):
        # Get the domain name from the URL without "www."
        parsed_url = urlparse(browser.url().toString())
        domain = parsed_url.hostname.replace("www.", "") if parsed_url.hostname else "Unknown"
        self.tabs.setTabText(self.tabs.indexOf(browser), domain)


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
            self.layout().addWidget(self.bookmarks_manager)  # Fixed the typo here
        self.bookmarks_manager.setVisible(not self.bookmarks_manager.isVisible())

    def open_customize_dialog(self):
        customize_dialog = CustomizeDialog(self)
        customize_dialog.exec_()

    def show_history(self):
        if self.current_browser():
            history_menu = QMenu(self)
            for entry in self.current_browser().history().items():
                action = history_menu.addAction(entry.title())
                action.triggered.connect(lambda _, url=entry.url(): self.current_browser().setUrl(url))
            history_menu.exec_(QCursor.pos())

    def open_chatbot_overlay(self):
        # Toggle the visibility of the chat overlay
        self.chat_overlay.setVisible(not self.chat_overlay.isVisible())

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

    def zoom_in(self):
        if self.current_browser():
            self.current_browser().setZoomFactor(self.current_browser().zoomFactor() + 0.1)

    def zoom_out(self):
        if self.current_browser():
            self.current_browser().setZoomFactor(self.current_browser().zoomFactor() - 0.1)

#commenting this class for now -kellidan
#class CustomChatbot:
    #def get_response(self, user_input):
        #return "This is a placeholder response."
    
class SaveFromNet:
    def exec_(self):
        return QDialog.Accepted

class CustomizeDialog(QDialog):
    def __init__(self, parent=None):
        super(CustomizeDialog, self).__init__(parent)

        self.setWindowTitle('Dark mode')
        self.setMinimumWidth(300)
        

        layout = QVBoxLayout()

        self.dark_mode_radio = QRadioButton('Dark Mode')
        self.light_mode_radio = QRadioButton('Light Mode')
        
        

        layout.addWidget(self.dark_mode_radio)
        layout.addWidget(self.light_mode_radio)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        layout.addWidget(button_box)

        self.setLayout(layout)

        # Connect radio buttons to change_color method
        self.dark_mode_radio.clicked.connect(lambda: self.change_color("dark"))
        self.light_mode_radio.clicked.connect(lambda: self.change_color("light"))

    # New method to change the color of the main window
    def change_color(self, mode):
        if mode == "dark":
            self.parent().setStyleSheet("background-color: #333333; color: white;")
        elif mode == "light":
            self.parent().setStyleSheet("background-color: #FFFFFF; color: black;")

class ChatOverlay(QWidget):
    def __init__(self, chatbot, parent=None):
        super(ChatOverlay, self).__init__(parent)
        self.chatbot = chatbot
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Container for chat input
        input_container = QWidget()
        input_layout = QVBoxLayout(input_container)

        # Set white background for chat input
        self.user_input = QLineEdit()
        self.user_input.setStyleSheet("background-color: black; color: White; border: 5px solid black;")
        self.user_input.setPlaceholderText("Type your message...")
        input_layout.addWidget(self.user_input)

        # Set white background for the submit button
        submit_button = QPushButton("Submit")
        submit_button.setStyleSheet("background-color: black; color: White; border: 5px solid black;")
        submit_button.clicked.connect(self.get_chatbot_response)
        input_layout.addWidget(submit_button)

        layout.addWidget(input_container)

        # Container for chat display
        display_container = QWidget()
        display_layout = QVBoxLayout(display_container)

        # Set white background for chat display
        self.chat_display = QTextBrowser()
        self.chat_display.setStyleSheet("background-color: Black; color: White; border: 5px solid black;")
        display_layout.addWidget(self.chat_display)

        # Set white background for the exit button
        clear_button = QPushButton("Clear")
        clear_button.setStyleSheet("background-color: black; color: White; border: 5px solid black;")
        clear_button.clicked.connect(self.clear_chat_display)     
        display_layout.addWidget(clear_button) 
        exit_button = QPushButton("Exit")
        exit_button.setStyleSheet("background-color: black; color: White; border: 5px solid black;")
        exit_button.clicked.connect(self.exit_overlay)
        display_layout.addWidget(exit_button)

        layout.addWidget(display_container)

        # Set white background for the ChatOverlay widget
        self.setStyleSheet("background-color: #5D3BB6; border: 1px solid black;")

        self.setLayout(layout)

        # Set the size of ChatOverlay to be similar to BookmarksManager
        self.setFixedSize(300, 500)  # Adjust the size as needed

    def exit_overlay(self):
        self.hide()

    def clear_chat_display(self):
        self.chat_display.clear()

    def get_chatbot_response(self):
        user_input = self.user_input.text()
        response = self.chatbot.get_response(user_input)

        # Style for user messages (blue text)
        user_style = '<span style="color: #d265b7;">You: </span>'
        # Style for chatbot replies (green text)
        chatbot_style = '<span style="color: #b765d2;">Chatbot: </span>'

        # Append user message and chatbot reply to chat_display
        self.chat_display.append(f"{user_style}{user_input}")
        self.chat_display.append(f"{chatbot_style}{response}")

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
            ("History", self.show_history, "Icons/h.png"),
            ("Chatbot", self.open_chatbot_overlay, "Icons/cb.png"),
            ("Downloads", self.show_downloads, "Icons/d.png"),
            ("Media Downloader", self.open_media_downloader, "Icons/md.png"),
        ]

        for action_text, slot, icon_path in actions:
            action = QAction(QIcon(icon_path), action_text, self)
            action.triggered.connect(slot)
            menu.addAction(action)

        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName('Alley')
    app.setApplicationDisplayName('Alley')
    app.setOrganizationName('SDCCE')
    window = MainWindow()
    window.showMaximized()
    sys.exit(app.exec_())
