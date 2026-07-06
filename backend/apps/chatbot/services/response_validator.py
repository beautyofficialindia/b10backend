class ResponseValidator:
    blocked_fragments = (
        "system prompt",
        "developer message",
        "ignore previous instructions",
        "i am chatgpt",
    )

    def validate(self, response):
        text = (response or "").strip()
        if not text:
            return False, "empty_response"
        lowered = text.lower()
        if any(fragment in lowered for fragment in self.blocked_fragments):
            return False, "unsafe_response"
        return True, "ok"

    def fallback_message(self):
        return (
            "I don't have enough verified information to answer that safely. "
            "I can connect you with the B10 team or help with B10's services and project consultation."
        )
