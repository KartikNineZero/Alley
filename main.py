import sys
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtGui import QIcon

class MainWindow(QMainWindow):


    def __init__(self):
        super(MainWindow, self).__init__()

        # Set window properties
        self.setWindowTitle('Alley Browser')
        self.setWindowIcon(QIcon('Icons/Logo.png'))

        # Create tab widget
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.setCentralWidget(self.tabs)

        # Create toolbar
        toolbar = QToolBar()
        self.addToolBar(toolbar)

        # Add back button
        back_btn = QAction('⮜', self)
        back_btn.triggered.connect(lambda: self.current_browser().back() if self.current_browser() else None)
        toolbar.addAction(back_btn)

        # Add forward button
        forward_btn = QAction('⮞', self)
        forward_btn.triggered.connect(lambda: self.current_browser().forward() if self.current_browser() else None)
        toolbar.addAction(forward_btn)

        # Add reload button
        reload_btn = QAction('⟳', self)
        reload_btn.triggered.connect(lambda: self.current_browser().reload() if self.current_browser() else None)
        toolbar.addAction(reload_btn)

        # Add home button
        home_btn = QAction('⌂', self)
        home_btn.triggered.connect(self.navigate_home)
        toolbar.addAction(home_btn)

        # Add new tab button
        add_tab_btn = QAction('+', self)
        add_tab_btn.triggered.connect(self.add_tab)
        toolbar.addAction(add_tab_btn)

        # Add Inspect Element action
        inspect_element_action = QAction('🔍', self)
        inspect_element_action.triggered.connect(self.inspect_element)
        toolbar.addAction(inspect_element_action)

        # Add URL bar
        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        toolbar.addWidget(self.url_bar)

        # Add first tab
        self.add_tab()

    def current_browser(self):
        return self.tabs.currentWidget() if self.tabs.count() > 0 else None

    def add_tab(self):
        browser = QWebEngineView()
        browser.setUrl(QUrl('https://google.com'))
        self.tabs.addTab(browser, 'New Tab')
        self.tabs.setCurrentWidget(browser)
        self.tabs.setTabText(self.tabs.currentIndex(), 'Loading...')
        browser.titleChanged.connect(
            lambda title, browser=browser: self.tabs.setTabText(self.tabs.indexOf(browser), title))
        if self.current_browser():
            browser.urlChanged.connect(
                lambda url, browser=browser: self.update_url(url) if self.current_browser() == browser else None)

    def close_tab(self, index):
        # Get the browser widget at the specified index
        browser_widget = self.tabs.widget(index)

        # Stop the video (if it is a video)
        if browser_widget.url().host() == "www.youtube.com":
            browser_widget.page().runJavaScript("document.getElementsByTagName('video')[0].pause();")

        # Remove the tab
        if self.tabs.count() < 2:
            # If this is the last tab, close the whole window
            self.close()
        else:
            # Remove the tab and delete the associated browser widget
            self.tabs.removeTab(index)
            browser_widget.deleteLater()

    def navigate_home(self):
        if self.current_browser():
            self.current_browser().setUrl(QUrl('https://www.google.com'))

    def navigate_to_url(self):
        if self.current_browser():
            url = self.url_bar.text()
            if 'http' not in url:
                url = 'https://' + url
            self.current_browser().setUrl(QUrl(url))

    def update_url(self, q):
        if self.sender() == self.current_browser():
            self.url_bar.setText(q.toString())
            self.url_bar.setCursorPosition(0)

    def inspect_element(self):
        if self.current_browser():
            # Get the current browser page
            page = self.current_browser().page()

            # Enable remote debugging
            page.settings().setAttribute(QWebEngineSettings.LocalStorageEnabled, True)

            # Create a new tab for DevTools
            dev_tools_browser = QWebEngineView()
            dev_tools_browser.page().setDevToolsPage(page)
            self.tabs.addTab(dev_tools_browser, 'DevTools')
            self.tabs.setCurrentWidget(dev_tools_browser)

            # Open DevTools using the remote debugging URL
            dev_tools_url = page.url().toString().replace('http://', 'chrome-devtools://devtools/remote/')
            dev_tools_browser.setUrl(QUrl(dev_tools_url))


app = QApplication(sys.argv)
app.setApplicationName('Alley')
app.setApplicationDisplayName('Alley')
app.setOrganizationName('SDCCE')
window = MainWindow()
window.showMaximized()
app.exec_()

