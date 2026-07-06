import json
import os
import time

import requests

from .base import AIProviderClient, AIResponse
from .exceptions import AIProviderConfigurationError, AIProviderError, AIProviderTimeoutError


class OpenRouterAIClient(AIProviderClient):
    url = "https://openrouter.ai/api/v1/chat/completions"

    def __init__(self, api_key=None, model=None, timeout=None):
        self.api_key = api_key or os.environ.get("OPENROUTER_API_KEY")
        self.model = model or os.environ.get("OPENROUTER_MODEL", "openai/gpt-4o-mini")
        self.timeout = int(timeout or os.environ.get("AI_REQUEST_TIMEOUT_SECONDS", 8))

    def generate_response(self, messages):
        if not self.api_key or self.api_key == "your_openrouter_api_key":
            raise AIProviderConfigurationError("OPENROUTER_API_KEY is not configured.")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://b10itsolution.com",
            "X-Title": "B10 AI Assistant",
            "Content-Type": "application/json",
        }
        payload = {"model": self.model, "messages": messages}
        started_at = time.monotonic()

        try:
            response = requests.post(
                self.url,
                headers=headers,
                data=json.dumps(payload),
                timeout=self.timeout,
            )
            response.raise_for_status()
        except requests.Timeout as exc:
            raise AIProviderTimeoutError("OpenRouter request timed out.") from exc
        except requests.RequestException as exc:
            raise AIProviderError("OpenRouter request failed.") from exc

        data = response.json()
        try:
            content = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise AIProviderError("OpenRouter returned an invalid response.") from exc

        usage = data.get("usage") or {}
        return AIResponse(
            content=content,
            model=data.get("model") or self.model,
            token_count_input=usage.get("prompt_tokens"),
            token_count_output=usage.get("completion_tokens"),
            latency_ms=int((time.monotonic() - started_at) * 1000),
        )
