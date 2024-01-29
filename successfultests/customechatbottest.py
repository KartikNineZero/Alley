import unittest
from src.CustomChatbot import CustomChatbot

class TestCustomChatbot(unittest.TestCase):

    def setUp(self):
        self.chatbot = CustomChatbot()

    def test_get_response_hello(self):
        user_input = "hello"
        response = self.chatbot.get_response(user_input)
        self.assertIn(response, ["Hello!", "Hi there!", "Hey!"])

    def test_get_response_empty(self):
        user_input = ""
        response = self.chatbot.get_response(user_input)
        self.assertEqual(response, "I'm sorry, I don't have information on that. Please ask another question.")

    def test_get_response_no_match(self):
        user_input = "Tell me about quantum physics"
        response = self.chatbot.get_response(user_input)
        self.assertEqual(response, "I'm sorry, I don't have information on that. Please ask another question.")

if __name__ == '__main__':
    unittest.main()
