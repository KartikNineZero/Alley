import src.MainWindow    
# The MainWindow is initialized with the correct window title and icon.
def test_initialized_with_correct_title_and_icon(self):
        from PyQt5.QtWidgets import QApplication
        app = QApplication([])
        window = MainWindow()
        assert window.windowTitle() == 'Alley Browser'
        assert window.windowIcon().isNull() == False

    # The MainWindow has a QTabWidget as its central widget.
def test_has_qtabwidget_as_central_widget(self):
        from PyQt5.QtWidgets import QApplication
        app = QApplication([])
        window = MainWindow()
        assert isinstance(window.centralWidget(), QTabWidget)

    # The MainWindow can add new tabs with a default URL.
def test_can_add_new_tabs_with_default_url(self):
        from PyQt5.QtWidgets import QApplication
        app = QApplication([])
        window = MainWindow()
        assert window.tabs.count() == 1
        assert window.tabs.tabText(0) == 'Loading...'

    # The MainWindow can handle closing the application.
def test_can_handle_closing_application(self):
        from PyQt5.QtWidgets import QApplication
        from PyQt5.QtGui import QCloseEvent
        app = QApplication([])
        window = MainWindow()
        window.closeEvent(QCloseEvent())
        assert window.isVisible() == False

       # The MainWindow can handle closing a tab.
def test_can_handle_closing_tab(self):
        from PyQt5.QtWidgets import QApplication
        app = QApplication([])
        window = MainWindow()
        window.add_tab()
        window.close_tab(0)
        assert window.tabs.count() == 1

          # The MainWindow can handle adding a new tab when there are no existing tabs.
def test_can_handle_adding_new_tab_with_no_existing_tabs(self):
        from PyQt5.QtWidgets import QApplication
        app = QApplication([])
        window = MainWindow()
        window.add_tab()
        window.close_tab(0)
        window.add_tab()
        assert window.tabs.count() == 2       