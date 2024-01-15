from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QRadioButton, QVBoxLayout, QLabel

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
        self.orange_theme_radio = QRadioButton('Orange Theme')
        self.purple_theme_radio = QRadioButton('Purple Theme')
        self.teal_theme_radio = QRadioButton('Teal Theme')
        self.brown_theme_radio = QRadioButton('Brown Theme')
        self.gray_theme_radio = QRadioButton('Gray Theme')

        layout.addWidget(self.theme_label)
        layout.addWidget(self.blue_theme_radio)
        layout.addWidget(self.green_theme_radio)
        layout.addWidget(self.red_theme_radio)
        layout.addWidget(self.orange_theme_radio)
        layout.addWidget(self.purple_theme_radio)
        layout.addWidget(self.teal_theme_radio)
        layout.addWidget(self.brown_theme_radio)
        layout.addWidget(self.gray_theme_radio)

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
        self.orange_theme_radio.clicked.connect(lambda: self.change_theme("orange"))
        self.purple_theme_radio.clicked.connect(lambda: self.change_theme("purple"))
        self.teal_theme_radio.clicked.connect(lambda: self.change_theme("teal"))
        self.brown_theme_radio.clicked.connect(lambda: self.change_theme("brown"))
        self.gray_theme_radio.clicked.connect(lambda: self.change_theme("gray"))

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
        template = "background-color: {}; color: {}; border-color: #000;"
        color_mapping = {
            "blue": "#3202F8",
            "green": "#008000",
            "red": "#FF0000",
            "orange": "#FFA500",
            "purple": "#800080",
            "teal": "#008080",
            "brown": "#A52A2A",
            "gray": "#808080",
        }

        if theme in color_mapping:
            style = template.format(color_mapping[theme], "white")
        else:
            style = ""
        self.parent().setStyleSheet(style)
