from nltk.chat.util import Chat

class CustomChatbot:
    def __init__(self):
        self.responses = [
            [
                r"hi|hello|hey",
                ["Hello!", "Hi there!", "Hey!"]
            ],
            [
                r"how are you|how's it going|how are things",
                ["I'm doing well, thank you!", "I'm good! How about you?", "Things are great! How can I help you?"]
            ],
            [
                r"(.*) weather",
                ["The weather is often mentioned as the main topic of conversation.", ]
            ],
            [
                r"(.*)",
                ["Please try asking a different question!", ]
            ],
        ]
        self.chat = Chat(self.responses)

    def get_response(self, user_input):
        return self.chat.respond(user_input)
    

