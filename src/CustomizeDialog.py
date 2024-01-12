from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QRadioButton, QVBoxLayout,QLabel


class CustomizeDialog(QDialog):
    def __init__(self, parent=None):
        super(CustomizeDialog, self).__init__(parent)

        self.setWindowTitle('Appearance')
        self.setMinimumWidth(300)

        layout = QVBoxLayout()

        self.dark_mode_radio = QRadioButton('Dark Mode')
        self.light_mode_radio = QRadioButton('Light Mode')
        self.default_radio = QRadioButton('Default')

        layout.addWidget(self.dark_mode_radio)
        layout.addWidget(self.light_mode_radio)
        layout.addWidget(self.default_radio)

        layout.addSpacing(15)  # Add spacing between color and theme sections

        # Themes Section
        self.theme_label = QLabel('Themes:')
        self.blue_theme_radio = QRadioButton('Blue Theme')
        self.green_theme_radio = QRadioButton('Green Theme')
        self.red_theme_radio = QRadioButton('Red Theme')

        layout.addWidget(self.theme_label)
        layout.addWidget(self.blue_theme_radio)
        layout.addWidget(self.green_theme_radio)
        layout.addWidget(self.red_theme_radio)

        # Button Box
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        layout.addWidget(button_box)

        self.setLayout(layout)

        # Connect radio buttons to change_color method
        self.dark_mode_radio.clicked.connect(lambda: self.change_color("dark"))
        self.light_mode_radio.clicked.connect(lambda: self.change_color("light"))
        self.default_radio.clicked.connect(lambda: self.change_color("default"))

        # Connect radio buttons to change_theme method
        self.blue_theme_radio.clicked.connect(lambda: self.change_theme("blue"))
        self.green_theme_radio.clicked.connect(lambda: self.change_theme("green"))
        self.red_theme_radio.clicked.connect(lambda: self.change_theme("red"))

    def change_color(self, mode):
        template = "background-color: {}; color: {};"
        if mode == "dark":
            style = template.format("#333333", "white")
        elif mode == "light":
            style = template.format("#FFFFFF", "black")
        else:
            style = ""
        self.parent().setStyleSheet(style)

    def change_theme(self, theme):
        template = "background-color: {}; color: {};"
        if theme == "blue":
            style = template.format("#0000FF", "white")
        elif theme == "green":
            style = template.format("#008000", "white")
        elif theme == "red":
            style = template.format("#FF0000", "white")
        else:
            style = ""
        self.parent().setStyleSheet(style)
