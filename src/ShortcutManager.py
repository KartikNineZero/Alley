from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence, QIcon
from PyQt5.QtWidgets import QShortcut, QAction

class ShortcutManager:
    def __init__(self, main_window):
        self.main_window = main_window

    def create_shortcuts(self):
        new_tab_shortcut = QShortcut(QKeySequence("Ctrl+T"), self.main_window)
        new_tab_shortcut.activated.connect(self.main_window.add_tab)

        close_tab_shortcut = QShortcut(QKeySequence("Ctrl+W"), self.main_window)
        close_tab_shortcut.activated.connect(lambda: self.main_window.close_tab(self.main_window.tabs.currentIndex()))

        home_btn_shortcut = QShortcut(QKeySequence("Alt+H"), self.main_window)
        home_btn_shortcut.activated.connect(self.main_window.navigate_home)

        back_shortcut = QShortcut(QKeySequence("Alt+Left"), self.main_window)
        back_shortcut.activated.connect(lambda: self.main_window.current_browser().back() if self.main_window.current_browser() else None)

        forward_shortcut = QShortcut(QKeySequence("Alt+Right"), self.main_window)
        forward_shortcut.activated.connect(lambda: self.main_window.current_browser().forward() if self.main_window.current_browser() else None)

        reload_shortcut = QShortcut(QKeySequence("Ctrl+R"), self.main_window)
        reload_shortcut.activated.connect(lambda: self.main_window.current_browser().reload() if self.main_window.current_browser() else None)

        focus_address_bar_shortcut = QShortcut(QKeySequence("Ctrl+L"), self.main_window)
        focus_address_bar_shortcut.activated.connect(self.main_window.focus_address_bar)

        bookmarks_shortcut = QShortcut(QKeySequence("Ctrl+B"), self.main_window)
        bookmarks_shortcut.activated.connect(self.open_bookmarks_dropdown)

        history_shortcut = QShortcut(QKeySequence("Ctrl+H"), self.main_window)
        history_shortcut.activated.connect(self.open_history_dropdown)

        zoom_out_shortcut = QShortcut(QKeySequence("Ctrl+-"), self.main_window)
        zoom_out_shortcut.activated.connect(self.main_window.zoom_out)
        
        zoom_in_shortcut = QShortcut(QKeySequence("Ctrl+="), self.main_window)
        zoom_in_shortcut.activated.connect(self.main_window.zoom_in)

        reset_zoom_shortcut = QShortcut(QKeySequence("Ctrl+0"), self.main_window)
        reset_zoom_shortcut.activated.connect(self.main_window.reset_zoom)

        downloads_shortcut = QShortcut(QKeySequence("Ctrl+J"), self.main_window)
        downloads_shortcut.activated.connect(self.main_window.show_download_manager)

        new_window_shortcut = QShortcut(QKeySequence("Ctrl+N"), self.main_window)
        new_window_shortcut.activated.connect(self.create_new_window)

        ctrl_k_shortcut = QShortcut(QKeySequence("Ctrl+K"), self.main_window)
        ctrl_k_shortcut.activated.connect(self.main_window.focus_address_bar)

        cut_shortcut = QShortcut(QKeySequence("Ctrl+X"), self.main_window)
        cut_shortcut.activated.connect(self.main_window.cut_text)

        copy_shortcut = QShortcut(QKeySequence("Ctrl+C"), self.main_window)
        copy_shortcut.activated.connect(self.main_window.copy_text)

        paste_shortcut = QShortcut(QKeySequence("Ctrl+V"), self.main_window)
        paste_shortcut.activated.connect(self.main_window.paste_text)

        undo_shortcut = QShortcut(QKeySequence("Ctrl+Z"), self.main_window)
        undo_shortcut.activated.connect(self.main_window.undo_text)

        redo_shortcut = QShortcut(QKeySequence("Ctrl+Y"), self.main_window)
        redo_shortcut.activated.connect(self.main_window.redo_text)

        screenshot_shortcut = QShortcut(QKeySequence(Qt.ALT + Qt.Key_S), self.main_window)
        screenshot_shortcut.activated.connect(self.main_window.take_screenshot)

        start_recording_shortcut = QShortcut(QKeySequence(Qt.CTRL + Qt.ALT + Qt.Key_R), self.main_window)
        start_recording_shortcut.activated.connect(self.main_window.start_recording)

        stop_recording_shortcut = QShortcut(QKeySequence(Qt.CTRL + Qt.ALT + Qt.Key_S), self.main_window)
        stop_recording_shortcut.activated.connect(self.main_window.stop_recording)

        toggle_overlay_shortcut = QShortcut("Alt+W", self.main_window)
        toggle_overlay_shortcut.activated.connect(self.toggle_custom_overlay)

        close_overlay_shortcut = QShortcut(QKeySequence("Alt+E"), self.main_window)
        close_overlay_shortcut.activated.connect(self.close_custom_overlay)

    def toggle_custom_overlay(self):
        if not self.main_window.custom_overlay.isVisible():
            self.main_window.show_custom_overlay()

    def close_custom_overlay(self):
        if self.main_window.custom_overlay.isVisible():
            self.main_window.hide_custom_overlay()

    def add_shortcut(self, key_sequence, callback, tooltip=None):
        shortcut = QShortcut(QKeySequence(key_sequence), self.main_window)
        shortcut.activated.connect(callback)

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
        home_shortcut = QShortcut(QKeySequence("Alt+H"), self.main_window)
        home_shortcut.activated.connect(self.main_window.navigate_home)
        action = QAction("Home", self.main_window)
        action.setShortcut(QKeySequence("Alt+H"))
        action.triggered.connect(self.main_window.navigate_home)
        self.main_window.addAction(action)
        if hasattr(self.main_window, 'toolbar'):
            self.main_window.toolbar.addAction(action)
    
    def open_bookmarks_dropdown(self):
        if hasattr(self.main_window, 'bookmarks_action'):
            self.main_window.bookmarks_action.trigger()

    def open_history_dropdown(self):
        if hasattr(self.main_window, 'history_action'):
            self.main_window.history_action.trigger()

    def zoom_in(self):
        if hasattr(self.main_window, 'zoom_in_dropdown_action'):
            self.main_window.zoom_in_dropdown_action.trigger()

    def zoom_out(self):
        if hasattr(self.main_window, 'zoom_out_dropdown_action'):
            self.main_window.zoom_out_dropdown_action.trigger()

    def reset_zoom(self):
        if hasattr(self.main_window, 'reset_zoom_action'):
            self.main_window.reset_zoom_action.trigger()

    def update_zoom(self):
        if hasattr(self.main_window, 'update_zoom_label'):
            self.main_window.update_zoom_label()

    def show_downloads(self):
        if hasattr(self.main_window, 'downloads_action'):
            self.main_window.downloads_action.trigger()

    def create_new_window(self):
        from src.MainWindow import MainWindow
        new_window = MainWindow()
        new_window.show()

    
