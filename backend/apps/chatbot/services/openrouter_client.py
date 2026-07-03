import os
import requests
import json

class OpenRouterClient:
    def __init__(self):
        self.api_key = os.environ.get('OPENROUTER_API_KEY')
        self.model = os.environ.get('OPENROUTER_MODEL', 'openai/gpt-4o-mini')
        self.url = "https://openrouter.ai/api/v1/chat/completions"

    def get_completion(self, messages):
        if not self.api_key or self.api_key == 'your_openrouter_api_key':
            raise ValueError("OPENROUTER_API_KEY is not set correctly.")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://b10itsolution.com",
            "X-Title": "B10 AI Assistant",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": messages
        }

        response = requests.post(self.url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        data = response.json()
        
        try:
            return data['choices'][0]['message']['content']
        except (KeyError, IndexError):
            return "I'm sorry, I couldn't generate a response at this time."
