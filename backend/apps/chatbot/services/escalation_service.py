from django.utils import timezone


class EscalationService:
    human_terms = (
        "talk to a person", "talk to human", "real person", "call me",
        "speak to someone", "human", "representative", "sales team",
    )
    frustration_terms = ("frustrated", "annoyed", "not helpful", "useless", "angry")

    def should_escalate(self, message, scope_decision, session):
        text = (message or "").lower()
        if any(term in text for term in self.human_terms):
            return True, "human_requested"
        if any(term in text for term in self.frustration_terms):
            return True, "frustration_detected"
        if scope_decision.reason == "off_topic":
            refusal_count = session.metadata.get("off_topic_count", 0) if session.metadata else 0
            if refusal_count >= 2:
                return True, "repeated_off_topic"
        return False, None

    def mark_escalated(self, session, reason):
        metadata = session.metadata or {}
        metadata["escalation_reason"] = reason
        session.metadata = metadata
        session.status = "escalated"
        session.qualification_state = "escalated_to_human"
        session.escalated_at = timezone.now()
        session.save(update_fields=["metadata", "status", "qualification_state", "escalated_at", "updated_at"])

    def contact_payload(self):
        return {
            "email": "contact@b10itsolution.com",
            "phone": "+1-800-555-0199",
            "booking_url": "https://b10itsolution.com/book-consultation",
        }

    def message(self):
        contact = self.contact_payload()
        return (
            "Of course. You can reach the B10 team directly at "
            f"{contact['email']} or book a consultation at {contact['booking_url']}. "
            "I can also keep the project context we have captured so far for the team."
        )
