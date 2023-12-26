from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QRadioButton, QVBoxLayout


class CustomizeDialog(QDialog):
    def __init__(self, parent=None):
        super(CustomizeDialog, self).__init__(parent)

        self.setWindowTitle('Dark mode')
        self.setMinimumWidth(300)

        layout = QVBoxLayout()

        self.dark_mode_radio = QRadioButton('Dark Mode')
        self.light_mode_radio = QRadioButton('Light Mode')
        self.default_radio = QRadioButton('Default')

        layout.addWidget(self.dark_mode_radio)
        layout.addWidget(self.light_mode_radio)
        layout.addWidget(self.default_radio)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        layout.addWidget(button_box)

        self.setLayout(layout)

        # Connect radio buttons to change_color method
        self.dark_mode_radio.clicked.connect(lambda: self.change_color("dark"))
        self.light_mode_radio.clicked.connect(lambda: self.change_color("light"))
        self.default_radio.clicked.connect(lambda: self.change_color("default"))


    def change_color(self, mode):
        template = "background-color: {}; color: {};"
        if mode == "dark":
            style = template.format("#333333", "white")
        elif mode == "light":
            style = template.format("#FFFFFF", "black")
        else:
            style = ""
        self.parent().setStyleSheet(style)
