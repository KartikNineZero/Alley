from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QLineEdit, QPushButton, QTextBrowser, QVBoxLayout, QHBoxLayout, QWidget

class ChatOverlay(QWidget):
    def __init__(self, chatbot, parent=None):
        super(ChatOverlay, self).__init__(parent)
        self.chatbot = chatbot
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Container for chat display
        self.chat_display = QTextBrowser()
        self.chat_display.setStyleSheet("background-color: #000; color: #fff; border-radius: 10px; padding: 10px; margin-bottom: 10px;")
        layout.addWidget(self.chat_display)

        # Container for chat input and submit button
        input_container = QWidget()
        input_layout = QHBoxLayout(input_container)

        self.user_input = QLineEdit()
        self.user_input.setStyleSheet("background-color: #000; color: #fff; border-radius: 20px; padding: 10px;")
        self.user_input.setPlaceholderText("Type your message...")
        input_layout.addWidget(self.user_input)

        submit_button = QPushButton("Send")
        submit_button.setStyleSheet("background-color: #800080; color: #fff; border-radius: 20px; padding: 10px;")
        submit_button.clicked.connect(self.get_chatbot_response)
        input_layout.addWidget(submit_button)

        layout.addWidget(input_container)

        # Add close button
        close_button = QPushButton("Close")
        close_button.setStyleSheet("background-color: #800080; color: #fff; border-radius: 20px; padding: 10px;")
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button)

        self.setLayout(layout)

        # Set the size of ChatOverlay
        self.setFixedSize(400, 600)

    def get_chatbot_response(self):
        user_input = self.user_input.text()
        response = self.chatbot.get_response(user_input)

        # Append user message to chat display
        self.append_message(user_input, user=True)

        # Append chatbot response to chat display
        self.append_message(response)

        # Clear the user input
        self.user_input.clear()

    def append_message(self, message, user=False):
        message_html = f'<div style="background-color: {"#b084d7" if user else "#e6bbff"}; color: #fff; border-radius: 10px; padding: 10px; margin-bottom: 5px; {"text-align: right;" if user else "text-align: left;"}"><div style="border: 2px solid {"#800080" if user else "#7d62a5"}; border-radius: 10px; padding: 5px;">{message}</div></div>'
        current_html = self.chat_display.toHtml()
        updated_html = f"{current_html}{message_html}"
        self.chat_display.setHtml(updated_html)
