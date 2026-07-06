from common.ai import OpenRouterAIClient

class OpenRouterClient:
    def __init__(self):
        self.client = OpenRouterAIClient()

    def get_completion(self, messages):
        return self.client.generate_response(messages).content

    def generate_response(self, messages):
        return self.client.generate_response(messages)
