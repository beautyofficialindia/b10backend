from dataclasses import dataclass


@dataclass
class AIResponse:
    content: str
    model: str
    token_count_input: int | None = None
    token_count_output: int | None = None
    latency_ms: int | None = None


class AIProviderClient:
    def generate_response(self, messages):
        raise NotImplementedError
