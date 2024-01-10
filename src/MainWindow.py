import re
import os
from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtGui import QCursor, QIcon, QPixmap
from PyQt5.QtWebEngineWidgets import QWebEngineSettings, QWebEngineView
from PyQt5.QtWidgets import (
    QAction,
    QDialog,
    QDockWidget,
    QLineEdit,
    QMainWindow,
    QMenu,
    QMessageBox,
    QTabWidget,
    QToolBar,
    QToolButton,
)


import json
from urllib.parse import urlparse

from src.CustomChatbot import CustomChatbot
from src.CustomizeDialog import CustomizeDialog
from src.MediaDownloader import SaveFromNet
from src.ChatOverlay import ChatOverlay
from src.BookmarksManager import BookmarksManager


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.setWindowTitle("Alley Browser")
        self.setWindowIcon(QIcon("Icons/Logo.png"))

        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.setCentralWidget(self.tabs)
        self.tabs.currentChanged.connect(self.update_url_from_active_tab)
        toolbar = QToolBar()
        self.addToolBar(toolbar)
        icon_width = 20
        icon_height = 20
        self.icon_width = 20
        self.icon_height = 20 
        self.tabs.currentChanged.connect(self.update_url_from_active_tab)
        self.tabs.currentChanged.connect(self.update_url_from_tab)

        home_btn = QAction(
            QIcon(QPixmap("Icons/home.png").scaled(icon_width, icon_height)), "⌂ HomePage", self
        )
        home_btn.triggered.connect(self.navigate_home)
        toolbar.addAction(home_btn)
        
        back_btn = QAction(
            QIcon(QPixmap("Icons/la.png").scaled(icon_width, icon_height)), "⮜ Navigate to Previous Page", self
        )
        back_btn.triggered.connect(
            lambda: self.current_browser().back() if self.current_browser() else None
        )
        toolbar.addAction(back_btn)
        forward_btn = QAction(
            QIcon(QPixmap("Icons/ra.png").scaled(icon_width, icon_height)), "⮞ Navigate to Next Page", self
        )
        forward_btn.triggered.connect(
            lambda: self.current_browser().forward() if self.current_browser() else None
        )
        toolbar.addAction(forward_btn)
        reload_btn = QAction(
            QIcon(QPixmap("Icons/r.png").scaled(icon_width, icon_height)), "⟳ Reload the Page", self
        )
        reload_btn.triggered.connect(
            lambda: self.current_browser().reload() if self.current_browser() else None
        )
        toolbar.addAction(reload_btn)

        self.url_bar = QLineEdit()
        self.url_bar.setFixedHeight(30)
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        toolbar.addWidget(self.url_bar)
        
        add_tab_btn = QAction(
            QIcon(QPixmap("Icons/add.png").scaled(icon_width, icon_height)), "+ New Tab", self
        )
        add_tab_btn.triggered.connect(self.add_tab)
        toolbar.addAction(add_tab_btn)
        
        self.bookmarks_action = QAction(
            QIcon(QPixmap("Icons/bm.png").scaled(icon_width,icon_height)),
            "Bookmarks",
            self,
        )
        
        toolbar.addAction(self.bookmarks_action)

        self.dropdown_menu = QMenu(self)
        self.bookmarks_action = QAction("Bookmarks", self)
        self.history_action = QAction("History", self)
        self.customize_ui_action = QAction("Customize", self)
        self.dropdown_menu.addAction(self.bookmarks_action)
        self.dropdown_menu.addAction(self.history_action)

        dropdown_btn = QToolButton(self)
        dropdown_btn.setMenu(self.dropdown_menu)
        dropdown_btn.setPopupMode(QToolButton.InstantPopup)
        dropdown_btn.setIcon(QIcon("Icons/menu.png"))
        # Add a separator to make the menu visually more appealing
        self.dropdown_menu.addSeparator()

        # Create actions for zoom in and zoom out
        zoom_in_dropdown_action = QAction(QIcon(QPixmap('Icons/zi.png').scaled(self.icon_width, self.icon_height)), 'Zoom In', self)
        zoom_in_dropdown_action.triggered.connect(self.zoom_in)

        zoom_out_dropdown_action = QAction(QIcon(QPixmap('Icons/zo.png').scaled(self.icon_width, self.icon_height)), 'Zoom Out', self)
        zoom_out_dropdown_action.triggered.connect(self.zoom_out)

        # Add a separator before adding zoom actions
        self.dropdown_menu.addSeparator()

        # Add zoom in and zoom out actions to the dropdown menu
        self.dropdown_menu.addAction(zoom_out_dropdown_action)
        self.dropdown_menu.addAction(zoom_in_dropdown_action)

        # Create action for reset zoom
        reset_zoom_action = QAction(QIcon('Icons/reset_zoom_icon.png'), 'Reset Zoom', self)
        reset_zoom_action.triggered.connect(self.reset_zoom)

        # Add reset zoom action to the dropdown menu
        self.dropdown_menu.addAction(reset_zoom_action)

        self.dropdown_menu.addSeparator()

        personalization_menu = self.dropdown_menu.addMenu("Themes")
        # Add theme actions dynamically from the Themes folder
        themes_folder = "themes"
        themes = self.get_available_themes(themes_folder)
        for theme in themes:
            theme_action = QAction(theme, self)
            theme_action.triggered.connect(lambda _, t=theme: self.apply_theme(t))
            personalization_menu.addAction(theme_action)
            
        # Replace 'Icons/bookmarks_icon.ico' with the actual path to your bookmarks icon
        bookmarks_icon_path = 'Icons/saved.png'
        self.bookmarks_action.setIcon(QIcon(bookmarks_icon_path))

        inspect_element_action_dropdown = QAction(QIcon('Icons/dev.png'), 'Dev tool', self)
        inspect_element_action_dropdown.triggered.connect(self.inspect_element)
        self.dropdown_menu.addAction(inspect_element_action_dropdown)
        
        # Replace 'Icons/bookmarks_icon.ico' with the actual path to your bookmarks icon
        bookmarks_icon_path = "Icons/bm.png"
        self.bookmarks_action.setIcon(QIcon(bookmarks_icon_path))

        # Replace 'Icons/history_icon.ico' with the actual path to your history icon
        history_icon_path = "Icons/h.png"
        self.history_action.setIcon(QIcon(history_icon_path))
        toolbar.addWidget(dropdown_btn)

        self.bookmarks_action.triggered.connect(self.show_bookmarks)
        self.history_action.triggered.connect(self.show_history)

        # customize
        self.customize_ui_action = QAction(QIcon("Icons/dm.png"), "Dark", self)
        self.customize_ui_action.triggered.connect(self.open_customize_dialog)
        self.dropdown_menu.addAction(self.customize_ui_action)

        # Connect CustomizeDialog to main window for color changes
        self.customize_dialog = CustomizeDialog(self)
        self.customize_ui_action.triggered.connect(self.customize_dialog.show)

        # Chatbot instance
        self.chatbot = CustomChatbot()

        # Action for opening chatbot overlay
        chatbot_icon_path = "Icons/cb.png"
        chatbot_action = QAction(QIcon(chatbot_icon_path), "Chatbot", self)
        chatbot_action.triggered.connect(self.open_chatbot_overlay)
        self.dropdown_menu.addAction(chatbot_action)

        # Downloads action in the dropdown
        self.downloaded_files = []  # List to keep track of downloaded files
        downloads_icon_path = "Icons/d.png"
        self.downloads_action = QAction(QIcon(downloads_icon_path), "Downloads", self)
        self.downloads_action.triggered.connect(self.show_downloads)
        self.dropdown_menu.addAction(self.downloads_action)

        # Media Downloader instance
        self.media_downloader = SaveFromNet()

        # Media Downloader action in the dropdown
        media_downloader_icon_path = "Icons/md.png"
        media_downloader_action = QAction(
            QIcon(media_downloader_icon_path), "Media Downloader", self
        )
        media_downloader_action.triggered.connect(self.open_media_downloader)
        self.dropdown_menu.addAction(media_downloader_action)

        self.add_tab()

        # Chatbot overlay
        self.chat_overlay = ChatOverlay(chatbot=self.chatbot)
        self.chat_overlay.setVisible(False)  # Initially hide the chat overlay
        print("Bug Here")
        self.layout().addWidget(self.chat_overlay)  # Add to the main window layout

        self.load_tabs_data()  # Load saved tabs when the application starts

    def reset_zoom(self):
        if self.current_browser():
            self.current_browser().setZoomFactor(1.0)
            self.update_zoom_label()

    def set_zoom_factor(self, factor):
        if self.current_browser():
            self.current_browser().setZoomFactor(factor)
            self.update_zoom_label()

    def zoom_in(self):
        if self.current_browser():
            current_factor = self.current_browser().zoomFactor()
            self.current_browser().setZoomFactor(current_factor + 0.1)
            self.update_zoom_label()

    def zoom_out(self):
        if self.current_browser():
            current_factor = self.current_browser().zoomFactor()
            self.current_browser().setZoomFactor(max(current_factor - 0.1, 0.1))
            self.update_zoom_label()

    def update_zoom_label(self):
        if self.current_browser():
            zoom_percentage = int(self.current_browser().zoomFactor() * 100)
            self.statusBar().showMessage(f"Zoom: {zoom_percentage}%")

    def update_url_from_active_tab(self, index):
        current_browser = self.tabs.widget(index)
        if current_browser:
            self.url_bar.setText(current_browser.url().toString())

    def open_settings(self):
        # Replace this with your actual settings implementation
        QMessageBox.information(
            self,
            "Settings",
            "Placeholder for settings. Implement your settings logic here.",
        )

    def current_browser(self):
        return self.tabs.currentWidget() if self.tabs.count() > 0 else None

    def load_tabs_data(self):
        try:
            with open("tabs_data.json", "r") as file:
                tabs_data = json.load(file)
                if not tabs_data:  # Check if the file is empty
                    print("No data found in tabs_data.json")
                    return
                for tab_data in tabs_data:
                    if tab_data["url"] != "https://duckduckgo.com/":
                        self.add_tab(url=tab_data["url"])
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
            if url != "https://duckduckgo.com/":
                tabs_data.append({"url": url})

        with open("tabs_data.json", "w") as file:
            json.dump(tabs_data, file)

    def closeEvent(self, event):
        self.save_tabs_data()  # Save tabs data when the application is closed
        event.accept()

    def current_browser(self):
        return self.tabs.currentWidget() if self.tabs.count() > 0 else None

    def add_tab(self, url=None):
        # Check if there are no tabs open and the JSON file is empty or not found
        if self.tabs.count() == 0 or (
            not self.is_tabs_data_file_found() or self.is_tabs_data_empty()
        ):
            self.open_default_tab()
        else:
            browser = QWebEngineView()

            if url:
                browser.setUrl(QUrl(url))
            else:
                browser.setUrl(QUrl("https://duckduckgo.com/"))

            self.tabs.addTab(browser, "New Tab")
            self.tabs.setCurrentWidget(browser)
            self.tabs.setTabText(self.tabs.currentIndex(), "Loading...")

            browser.titleChanged.connect(
                lambda title, browser=browser: self.update_tab_title(browser)
            )

            if self.current_browser():
                browser.urlChanged.connect(
                    lambda url, browser=browser: self.update_url(url)
                    if self.current_browser() == browser
                    else None
                )
            
            browser.page().profile().downloadRequested.connect(self.on_download_requested)

    
    # Helper methods for file and data checks
    def is_tabs_data_file_found(self):
        try:
            with open("tabs_data.json", "r") as file:
                return True
        except FileNotFoundError:
            return False

    def is_tabs_data_empty(self):
        try:
            with open("tabs_data.json", "r") as file:
                tabs_data = json.load(file)
                return not bool(tabs_data)
        except json.JSONDecodeError:
            return True

    def open_default_tab(self):
        browser = QWebEngineView()
        browser.setUrl(QUrl("https://duckduckgo.com/"))

        self.tabs.addTab(browser, "New Tab")
        self.tabs.setCurrentWidget(browser)
        self.tabs.setTabText(self.tabs.currentIndex(), "Loading...")

        browser.titleChanged.connect(
            lambda title, browser=browser: self.update_tab_title(browser)
        )

        if self.current_browser():
            browser.urlChanged.connect(
                lambda url, browser=browser: self.update_url(url)
                if self.current_browser() == browser
                else None
            )

    def update_tab_title(self, browser):
        # Get the domain name from the URL without "www."
        parsed_url = urlparse(browser.url().toString())
        domain = (
            parsed_url.hostname.replace("www.", "")
            if parsed_url.hostname
            else "Unknown"
        )
        self.tabs.setTabText(self.tabs.indexOf(browser), domain)

    def close_tab(self, index):
        browser_widget = self.tabs.widget(index)

        if browser_widget.url().host() == "www.youtube.com":
            browser_widget.page().runJavaScript(
                "document.getElementsByTagName('video')[0].pause();"
            )

        if self.tabs.count() < 2:
            self.close()
        else:
            self.tabs.removeTab(index)
            browser_widget.deleteLater()

    def navigate_home(self):

        if self.current_browser():
            self.current_browser().setUrl(QUrl("https://duckduckgo.com/"))

    def navigate_to_url(self):
        if self.current_browser():
            input_text = self.url_bar.text()

            if ".com" in input_text:
                url = input_text
            else:
                url = f'https://duckduckgo.com/?hps=1&q={"+".join(input_text.split())}&ia=web'


            if not url.startswith("http://") and not url.startswith("https://"):
                url = "https://" + url

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

        bookmarks = ["Bookmark 1", "Bookmark 2", "Bookmark 3"]  # Replace with your actual bookmarks data
        self.bookmark_dialog = BookmarkDialog(self)
        self.bookmark_dialog.populate_bookmarks(bookmarks)

        result = self.bookmark_dialog.exec_()
        if result == QDialog.Accepted:
            # Handle bookmark selection if needed
            pass

    def show_bookmark_dialog(self):
        dialog = BookmarkDialog(self)
        result = dialog.exec_()
        if result == QDialog.Accepted:
            bookmark_name = dialog.get_bookmark_name()
            current_url = self.url_bar.text()

            if bookmark_name and current_url:
                # Save the bookmark (you can implement your saving logic here)
                print(f"Bookmark saved - Name: {bookmark_name}, URL: {current_url}")
            else:
                print("Bookmark not saved - Name or URL is empty.")

    def create_toolbar_action(self, icon_path, callback, shortcut=None, text=''):
        # Use self.icon_width and self.icon_height to access class attributes
        action = QAction(QIcon(QPixmap(icon_path).scaled(self.icon_width, self.icon_height)), text, self)
        if shortcut:
            action.setShortcut(shortcut)
        if text == 'Bookmark':
            action.triggered.connect(self.show_bookmark_dialog)  # Corrected this line
        else:
            action.triggered.connect(callback)
        return action

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
                action.triggered.connect(
                    lambda _, url=entry.url(): self.current_browser().setUrl(url)
                )
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
                QMessageBox.information(
                    self,
                    "Download Complete",
                    f"File '{filename}' downloaded successfully.",
                )

    def show_downloads(self):
        if not self.downloaded_files:
            QMessageBox.information(self, "Downloads", "No files downloaded yet.")
            return

        downloads_text = "\n".join(self.downloaded_files)
        QMessageBox.information(
            self, "Downloads", f"Downloaded Files:\n{downloads_text}"
        )

    def inspect_element(self):
        if self.current_browser():
            # Get the current browser page
            page = self.current_browser().page()
            # Enable remote debugging
            page.settings().setAttribute(QWebEngineSettings.LocalStorageEnabled, True)
            # Create a new QWebEngineView for DevTools
            dev_tools_browser = QWebEngineView()
            dev_tools_browser.page().setDevToolsPage(page)
            # Create a QDockWidget to contain the DevTools browser
            dock_widget = QDockWidget("DevTools", self)
            dock_widget.setWidget(dev_tools_browser)
            dock_widget.setFeatures(
                QDockWidget.DockWidgetFloatable | QDockWidget.DockWidgetMovable
            )
            # Set the QDockWidget to be a right dock
            self.addDockWidget(Qt.LeftDockWidgetArea, dock_widget)
            # Open DevTools using the remote debugging URL
            dev_tools_url = (
                page.url()
                .toString()
                .replace("http://", "chrome-devtools://devtools/remote/")
            )
            dev_tools_browser.setUrl(QUrl(dev_tools_url))

    def get_available_themes(self, themes_folder):
        themes = []
        if os.path.exists(themes_folder):
            themes = [f for f in os.listdir(themes_folder) if f.endswith(".qss")]
        return themes

    def apply_theme(self, theme):
        theme_path = os.path.join("Themes", theme)
        with open(theme_path, "r") as file:
            qss_content = file.read()
            self.setStyleSheet(qss_content)

    def on_download_requested(self, download):
        download.finished.connect(self.on_download_finished)
        download.downloadProgress.connect(self.on_download_progress)

        # Set your download path here
        default_downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
        download.setPath(default_downloads_path)  # Set the default Downloads directory
        # Start the download
        download.accept()

    def on_download_progress(self, bytes_received, bytes_total):
        print(f"Downloaded {bytes_received} of {bytes_total} bytes")

    def on_download_finished(self):
        print("Download finished")