from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLineEdit, QPushButton, QTextBrowser, QVBoxLayout, QHBoxLayout, QLabel, QWidget


class ChatOverlay(QWidget):
    def __init__(self, chatbot, parent=None):
        super(ChatOverlay, self).__init__(parent)
        self.chatbot = chatbot
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Container for chat input
        input_container = QWidget()
        input_layout = QVBoxLayout(input_container)



        # Container for chat input and X button
        input_and_exit_container = QWidget()
        input_and_exit_layout = QHBoxLayout(input_and_exit_container)



        # Set white background for chat input
        self.user_input = QLineEdit()
        self.user_input.setStyleSheet("background-color: black; color: White; border: 5px solid black;")
        self.user_input.setPlaceholderText("Type your message...")
        input_and_exit_layout.addWidget(self.user_input)




        # Set white background for the exit button
        exit_button = QPushButton("X")
        exit_button.setStyleSheet("background-color: red; color: white;")
        exit_button.clicked.connect(self.exit_overlay)
        input_and_exit_layout.addWidget(exit_button)

        layout.addWidget(input_and_exit_container)




        # Set white background for the submit button
        submit_button = QPushButton("Submit")
        submit_button.setStyleSheet("background-color: black; color: White; border: 5px solid black;")
        submit_button.clicked.connect(self.get_chatbot_response)
        input_layout.addWidget(submit_button)

        layout.addWidget(input_container)

        # Container for chat display
        display_container = QWidget()
        display_layout = QVBoxLayout(display_container)

        # Set white background for chat display
        self.chat_display = QTextBrowser()
        self.chat_display.setStyleSheet("background-color: Black; color: White; border: 5px solid black;")
        display_layout.addWidget(self.chat_display)

        # Set white background for the exit button
        clear_button = QPushButton("Clear")
        clear_button.setStyleSheet("background-color: black; color: White; border: 5px solid black;")
        clear_button.clicked.connect(self.clear_chat_display)
        display_layout.addWidget(clear_button)


        '''
        exit_button = QPushButton("Exit")
        exit_button.setStyleSheet("background-color: black; color: White; border: 5px solid black;")
        exit_button.clicked.connect(self.exit_overlay)
        display_layout.addWidget(exit_button)'''

        layout.addWidget(display_container)

        self.setLayout(layout)

        # Set the size of ChatOverlay to be similar to BookmarksManager
        self.setFixedSize(400, 700)  # Adjust the size as needed

    def exit_overlay(self):
        self.hide()

    def clear_chat_display(self):
        self.chat_display.clear()

    def get_chatbot_response(self):
        user_input = self.user_input.text()
        response = self.chatbot.get_response(user_input)

        # Append user message and chatbot reply to chat_display
        self.chat_display.append(f"{user_style}{user_input}")
        self.chat_display.append(f"{chatbot_style}{response}")

        self.user_input.clear()