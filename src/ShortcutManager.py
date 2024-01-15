from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence, QIcon
from PyQt5.QtWidgets import QShortcut, QAction

class ShortcutManager:
    def __init__(self, main_window):
        self.main_window = main_window

    def create_shortcuts(self):
        # new tab
        new_tab_shortcut = QShortcut(QKeySequence("Ctrl+T"), self.main_window)
        new_tab_shortcut.activated.connect(self.main_window.add_tab)

        #close tab
        close_tab_shortcut = QShortcut(QKeySequence("Ctrl+W"), self.main_window)
        close_tab_shortcut.activated.connect(lambda: self.main_window.close_tab(self.main_window.tabs.currentIndex()))

        # Add a shortcut for the Home button (Ctrl+H)
        home_btn_shortcut = QShortcut(QKeySequence("Alt+H"), self.main_window)
        home_btn_shortcut.activated.connect(self.main_window.navigate_home)

        # Add a shortcut for navigating to the previous page (Alt+Left arrow)
        back_shortcut = QShortcut(QKeySequence("Alt+Left"), self.main_window)
        back_shortcut.activated.connect(lambda: self.main_window.current_browser().back() if self.main_window.current_browser() else None)

        # Add a shortcut for navigating to the next page (Alt+Right arrow)
        forward_shortcut = QShortcut(QKeySequence("Alt+Right"), self.main_window)
        forward_shortcut.activated.connect(lambda: self.main_window.current_browser().forward() if self.main_window.current_browser() else None)

        # Add a shortcut for reloading the current page (Ctrl+R)
        reload_shortcut = QShortcut(QKeySequence("Ctrl+R"), self.main_window)
        reload_shortcut.activated.connect(lambda: self.main_window.current_browser().reload() if self.main_window.current_browser() else None)

        # Add a shortcut for focusing the address bar (Ctrl+L)
        focus_address_bar_shortcut = QShortcut(QKeySequence("Ctrl+L"), self.main_window)
        focus_address_bar_shortcut.activated.connect(self.main_window.focus_address_bar)

        # Add Ctrl + B shortcut for opening bookmarks from the dropdown menu
        bookmarks_shortcut = QShortcut(QKeySequence("Ctrl+B"), self.main_window)
        bookmarks_shortcut.activated.connect(self.open_bookmarks_dropdown)

        # Add ctrl + h to show history
        history_shortcut = QShortcut(QKeySequence("Ctrl+H"), self.main_window)
        history_shortcut.activated.connect(self.open_history_dropdown)

        #ctrl + - zoom out
        zoom_out_shortcut = QShortcut(QKeySequence("Ctrl+-"), self.main_window)
        zoom_out_shortcut.activated.connect(self.main_window.zoom_out)
        
        #ctrl + + zoom in
        # Add a shortcut for zooming in (Ctrl++)
        zoom_in_shortcut = QShortcut(QKeySequence("Ctrl+="), self.main_window)
        zoom_in_shortcut.activated.connect(self.main_window.zoom_in)

        #ctrl + 0 reset zoom
        reset_zoom_shortcut = QShortcut(QKeySequence("Ctrl+0"), self.main_window)
        reset_zoom_shortcut.activated.connect(self.main_window.reset_zoom)

        downloads_shortcut = QShortcut(QKeySequence("Ctrl+J"), self.main_window)
        downloads_shortcut.activated.connect(self.show_downloads)


    def add_shortcut(self, key_sequence, callback, tooltip=None):
        shortcut = QShortcut(QKeySequence(key_sequence), self.main_window)
        shortcut.activated.connect(callback)

        # Optionally, create corresponding actions for menu and toolbar
        if tooltip:
            action = QAction(tooltip, self.main_window)
            action.setShortcut(QKeySequence(key_sequence))
            action.triggered.connect(callback)
            self.main_window.addAction(action)

            if hasattr(self.main_window, 'toolbar'):
                self.main_window.toolbar.addAction(action)

    def close_tab(self, index=None):
        if index is None:
            index = self.tabs.currentIndex()

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

    def add_home_shortcut(self):
        # Add a shortcut for the home button (using Alt+H)
        home_shortcut = QShortcut(QKeySequence("Alt+H"), self.main_window)
        home_shortcut.activated.connect(self.main_window.navigate_home)
        # Optionally, create a corresponding action for the menu and toolbar
        action = QAction("Home", self.main_window)
        action.setShortcut(QKeySequence("Alt+H"))
        action.triggered.connect(self.main_window.navigate_home)
        self.main_window.addAction(action)
        if hasattr(self.main_window, 'toolbar'):
            self.main_window.toolbar.addAction(action)
    
    def open_bookmarks_dropdown(self):
        # logic to select the "Bookmarks" action from the dropdown menu
        if hasattr(self.main_window, 'bookmarks_action'):
            self.main_window.bookmarks_action.trigger()

    def open_history_dropdown(self):
        # Check if history_action is present in the main window
        if hasattr(self.main_window, 'history_action'):
            # Trigger the action directly
            self.main_window.history_action.trigger()

    def zoom_in(self):
        # Check if zoom_in_dropdown_action is present in the main window
        if hasattr(self.main_window, 'zoom_in_dropdown_action'):
            # Trigger the action directly
            self.main_window.zoom_in_dropdown_action.trigger()

    def zoom_out(self):
        # Check if zoom_out_dropdown_action is present in the main window
        if hasattr(self.main_window, 'zoom_out_dropdown_action'):
            # Trigger the action directly
            self.main_window.zoom_out_dropdown_action.trigger()

    def reset_zoom(self):
        # Check if reset_zoom_action is present in the main window
        if hasattr(self.main_window, 'reset_zoom_action'):
            # Trigger the action directly
            self.main_window.reset_zoom_action.trigger()

    def update_zoom(self):
        # Check if update_zoom_label is a method in the main window
        if hasattr(self.main_window, 'update_zoom_label'):
            # Call the method to update zoom label
            self.main_window.update_zoom_label()

    def show_downloads(self):
        # Check if downloads_action is present in the main window
        if hasattr(self.main_window, 'downloads_action'):
            # Trigger the action directly
            self.main_window.downloads_action.trigger()
