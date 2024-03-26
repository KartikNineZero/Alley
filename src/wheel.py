import sys
from math import cos, sin, radians
from PyQt5.QtCore import pyqtSignal, Qt, QPoint, QSize, QFile, QTextStream, QPropertyAnimation, QRectF, QSequentialAnimationGroup
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, QDesktopWidget, QLineEdit, QHBoxLayout, QTextEdit, QFileDialog, QGraphicsDropShadowEffect
from PyQt5.QtGui import QPainter, QColor, QIcon, QBrush, QLinearGradient

class NotepadWidget(QWidget):
    closed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setWindowTitle("Notepad")
        self.setGeometry(0, 0, 500, 600)  # Increased window size
        self.center_on_screen()
        layout = QVBoxLayout()

        title_label = QLabel("Notepad")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 24px; color: #FFFFFF; padding: 10px; background-color: #303030;")
        layout.addWidget(title_label)

        self.text_edit = QTextEdit()
        self.text_edit.setStyleSheet("font-size: 16px; background-color: #252525; color: #FFFFFF; border: 2px solid #404040; padding: 10px;")
        layout.addWidget(self.text_edit)

        save_button = QPushButton("Save")
        save_button.setStyleSheet("font-size: 18px; background-color: #606060; color: #FFFFFF; border: none; padding: 10px;")
        save_button.clicked.connect(self.save_file)
        layout.addWidget(save_button)

        load_button = QPushButton("Load")
        load_button.setStyleSheet("font-size: 18px; background-color: #606060; color: #FFFFFF; border: none; padding: 10px;")
        load_button.clicked.connect(self.load_file)
        layout.addWidget(load_button)

        close_button = QPushButton("Close Notepad")
        close_button.setStyleSheet("font-size: 18px; background-color: #606060; color: #FFFFFF; border: none; padding: 10px;")
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button)

        self.setLayout(layout)

    def save_file(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save File", "", "Text Files (*.txt)")
        if file_path:
            with open(file_path, "w") as file:
                text = self.text_edit.toPlainText()
                file.write(text)

    def load_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open File", "", "Text Files (*.txt)")
        if file_path:
            with open(file_path, "r") as file:
                text = file.read()
                self.text_edit.setPlainText(text)

    def center_on_screen(self):
        screen_geometry = QDesktopWidget().screenGeometry()
        center_point = screen_geometry.center() - QPoint(self.width() // 2, self.height() // 2)
        self.move(center_point)

class CalculatorWidget(QWidget):
    closed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setWindowTitle("Calculator")
        self.setGeometry(0, 0, 300, 400)
        self.move(QApplication.desktop().screen().rect().center() - self.rect().center())
        layout = QVBoxLayout()

        self.display = QLineEdit()
        self.display.setAlignment(Qt.AlignRight)
        self.display.setReadOnly(True)
        self.display.setStyleSheet("font-size: 20px; background-color: #303030; color: #FFFFFF; border: none; padding: 10px;")
        layout.addWidget(self.display)

        buttons = [
            ("7", "8", "9", "/"),
            ("4", "5", "6", "*"),
            ("1", "2", "3", "-"),
            ("0", ".", "=", "+")
        ]

        for row in buttons:
            button_row = QWidget()
            row_layout = QHBoxLayout(button_row)
            for text in row:
                button = QPushButton(text)
                button.setStyleSheet("font-size: 18px; background-color: #606060; color: #FFFFFF; border: none; padding: 10px;")
                button.clicked.connect(lambda _, text=text: self.on_button_click(text))
                row_layout.addWidget(button)
            layout.addWidget(button_row)

        close_button = QPushButton("Close Calculator")
        close_button.setStyleSheet("font-size: 16px; background-color: #C0C0C0; color: #000000; border: none; padding: 10px;")
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button)

        self.setLayout(layout)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_pos = event.globalPos() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            self.move(event.globalPos() - self.drag_pos)

    def on_button_click(self, text):
        if text == "=":
            try:
                result = eval(self.display.text())
                self.display.setText(str(result))
            except Exception as e:
                self.display.setText("Error")
        else:
            self.display.setText(self.display.text() + text)

class CustomOverlay(QWidget):
    closed = pyqtSignal()

    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowOpacity(0.0)  # Start with opacity 0 for smooth fade-in animation
        self.animation = QPropertyAnimation(self, b'windowOpacity')
        self.animation.setDuration(500)  # Animation duration in milliseconds

        self.setFixedSize(500, 500)
        self.setupButtons()
        self.setupHomeButton()


    def setupButtons(self):
        self.buttons = []
        num_divisions = 5
        angle_step = 360 / num_divisions
        button_radius = 30
        for i in range(num_divisions):
            angle = i * angle_step
            if i == 0:
                button = QPushButton(self)
                calculator_icon = QIcon("Icons/Calculator.png")  # Icon for Calculator
                calculator_icon_actual_size = calculator_icon.actualSize(QSize(100, 100))  # Adjust size as needed
                button.setIcon(calculator_icon)
                button.setIconSize(calculator_icon_actual_size)  # Set icon size
                button.setStyleSheet("background-color: none; border: none; padding: 0px;")
                button.clicked.connect(self.show_calculator)
            elif i == 1:
                button = QPushButton(self)
                notes_icon = QIcon("Icons/notes.png")
                notes_icon_actual_size = notes_icon.actualSize(QSize(100, 100))
                button.setIcon(notes_icon)
                button.setIconSize(notes_icon_actual_size)
                button.setStyleSheet("background-color: none; border: none; padding: 0px;")
                button.clicked.connect(self.show_notepad)
            elif i == 2:
                button = QPushButton(self)  # Add screenshot button
                screenshot_icon = QIcon("Icons/screenshot_icon.png")  # Provide icon path
                screenshot_icon_actual_size = screenshot_icon.actualSize(QSize(100, 100))  # Adjust size as needed
                button.setIcon(screenshot_icon)
                button.setIconSize(screenshot_icon_actual_size)
                button.setStyleSheet("background-color: none; border: none; padding: 0px;")
                button.clicked.connect(self.main_window.take_screenshot)
            elif i == 3:
                button = QPushButton(self)  # Add screen recording button
                screen_recording_icon = QIcon("Icons/start_recording_icon.png")  # Provide icon path
                screen_recording_icon_actual_size = screen_recording_icon.actualSize(QSize(100, 100))  # Adjust size as needed
                button.setIcon(screen_recording_icon)
                button.setIconSize(screen_recording_icon_actual_size)
                button.setStyleSheet("background-color: none; border: none; padding: 0px;")
                button.clicked.connect(self.main_window.start_recording)
            else:
                button = QPushButton('Feature {}'.format(i - 2), self)
                button.setStyleSheet("background-color: none; border: none; padding: 0px;")

                                               

            button.setCursor(Qt.PointingHandCursor)
            shadow = QGraphicsDropShadowEffect(blurRadius=5, xOffset=3, yOffset=3)
            button.setGraphicsEffect(shadow)
            self.buttons.append((button, angle, angle + angle_step / 2))

    def setupHomeButton(self):
        self.home_button = QPushButton(self)
        self.home_button.setIcon(QIcon("homewheel.png"))
        self.home_button.setIconSize(QSize(30, 30))  # Adjusted size
        self.home_button.setStyleSheet("background-color: #CCCCCC; border: none; border-radius: 15px;")

        self.home_button.setCursor(Qt.PointingHandCursor)
        shadow = QGraphicsDropShadowEffect(blurRadius=5, xOffset=3, yOffset=3)
        self.home_button.setGraphicsEffect(shadow)
        self.home_button.clicked.connect(self.close)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw gradient background
        gradient = QLinearGradient(self.rect().topLeft(), self.rect().bottomRight())
        gradient.setColorAt(0, QColor("#333333"))  # Dark grey
        gradient.setColorAt(1, QColor("#CCCCCC"))  # Light grey
        painter.setBrush(QBrush(gradient))
        painter.drawEllipse(self.rect())

        # Draw a circle in the center
        center_circle_radius = 40  # Adjust the radius as needed
        center_circle_center = self.rect().center()
        center_circle_rect = QRectF(center_circle_center.x() - center_circle_radius, center_circle_center.y() - center_circle_radius,
                                    2 * center_circle_radius, 2 * center_circle_radius)
        painter.setBrush(QColor("#555555"))  # Color of the center circle
        painter.drawEllipse(center_circle_rect)

        # Position buttons inside each divided part
        for button, angle, _ in self.buttons:
            button_center = self.get_point_on_circle(self.rect().center(), self.rect().height() / 3, angle)
            button_radius = button.width() // 2
            button.setGeometry(button_center.x() - button_radius, button_center.y() - button_radius, 2 * button_radius, 2 * button_radius)

        # Position home button in the center
        home_button_radius = self.home_button.width() // 2
        self.home_button.setGeometry(self.rect().center().x() - home_button_radius, self.rect().center().y() - home_button_radius, 2 * home_button_radius, 2 * home_button_radius)

    def get_point_on_circle(self, center, radius, angle):
        x = center.x() + radius * cos(radians(angle))
        y = center.y() + radius * sin(radians(angle))
        return QPoint(int(x), int(y))

    def center_on_screen(self):
        screen_geometry = QDesktopWidget().screenGeometry()
        center_point = screen_geometry.center() - QPoint(self.width() // 2, self.height() // 2)
        self.move(center_point)

    def animate(self, fade_in=True):
        if fade_in:
            self.animation.setStartValue(0.0)
            self.animation.setEndValue(0.95)
        else:
            self.animation.setStartValue(0.95)
            self.animation.setEndValue(0.0)
        self.animation.start()

    def show_calculator(self):
        self.calculator_widget = CalculatorWidget()
        self.calculator_widget.show()
        self.close()

    def show_notepad(self):
        self.notepad_widget = NotepadWidget()
        self.notepad_widget.show()
        self.close()

    def showEvent(self, event):
        self.animate(fade_in=True)

    def closeEvent(self, event):
        self.animate(fade_in=False)
        event.accept()

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.initUI()

    def initUI(self):
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setGeometry(100, 100, 800, 600)

        self.custom_overlay = CustomOverlay(self)
        self.setCentralWidget(self.custom_overlay)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

