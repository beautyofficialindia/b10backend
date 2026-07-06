from dataclasses import dataclass


@dataclass
class ScopeDecision:
    allowed: bool
    reason: str
    mode: str
    risk_level: str = "low"


class ScopeGuard:
    in_scope_terms = {
        "b10", "service", "services", "company", "consultation", "contact",
        "website", "web", "mobile", "app", "software", "project", "industry",
        "health", "healthcare", "healthtech", "education", "edtech", "saas",
        "marketplace", "ecommerce", "e-commerce", "enterprise", "cloud",
        "ai", "automation", "support", "maintenance", "timeline", "budget",
        "price", "pricing", "quote", "business", "startup", "mvp", "build",
        "develop", "development", "design", "ui", "ux",
    }
    off_scope_terms = {
        "recipe", "homework", "sports", "politics", "movie", "song", "poem",
        "joke", "cricket", "ipl", "weather", "stock", "medical advice",
        "legal advice", "financial advice", "diagnose", "prescription",
        "python code", "write code", "debug code", "sort a list",
    }
    injection_terms = {
        "ignore previous instructions", "ignore all previous", "system prompt",
        "reveal your prompt", "developer message", "act as chatgpt", "you are now",
        "jailbreak", "dan mode", "print your instructions", "show your instructions",
    }

    def classify(self, message):
        text = (message or "").strip().lower()
        if not text:
            return ScopeDecision(False, "empty_message", "refusal")

        if any(term in text for term in self.injection_terms):
            return ScopeDecision(False, "prompt_injection", "refusal", "high")

        if any(term in text for term in self.off_scope_terms):
            return ScopeDecision(False, "off_topic", "refusal", "medium")

        if any(term in text for term in self.in_scope_terms):
            return ScopeDecision(True, "in_scope", self._mode_for(text))

        return ScopeDecision(True, "ambiguous", "requirement_discovery", "low")

    def validate_response(self, response, original_decision):
        text = (response or "").lower()
        if not response or not response.strip():
            return ScopeDecision(False, "empty_response", "refusal", "medium")
        if any(term in text for term in self.injection_terms):
            return ScopeDecision(False, "prompt_leakage", "refusal", "high")
        if original_decision.risk_level == "high" and original_decision.mode == "refusal":
            return ScopeDecision(False, original_decision.reason, "refusal", original_decision.risk_level)
        return ScopeDecision(True, "response_valid", original_decision.mode, original_decision.risk_level)

    def _mode_for(self, text):
        if any(word in text for word in ["contact", "book", "call", "email"]):
            return "consultation"
        if any(word in text for word in ["price", "pricing", "budget", "timeline"]):
            return "faq"
        if any(word in text for word in ["industry", "health", "education", "saas", "ecommerce", "enterprise"]):
            return "industry_recommendation"
        if any(word in text for word in ["service", "web", "mobile", "ai", "cloud", "design"]):
            return "service_discovery"
        return "company_information"

    def refusal_message(self, reason):
        if reason == "prompt_injection":
            return (
                "I can't help with requests to reveal or change my instructions. "
                "I'm B10 IT Solution's AI assistant, and I can help with B10's services, industries, or project consultation."
            )
        if reason == "empty_message":
            return "Please send a message about your project or what you'd like to know about B10 IT Solution."
        return (
            "That's outside what I'm here to help with. I'm B10 IT Solution's AI assistant, "
            "focused on B10's services, industries, and project consultation. Are you exploring a software or app development need?"
        )
