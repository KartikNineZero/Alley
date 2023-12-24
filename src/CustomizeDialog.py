#commenting this class for now -kellidan
#class CustomChatbot:
    #def get_response(self, user_input):
        #return "This is a placeholder response."

from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QRadioButton, QVBoxLayout


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