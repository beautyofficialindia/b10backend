from django.utils import timezone


class QualificationService:
    """
    Evaluates whether a Lead has sufficient data to be considered qualified,
    and performs the mechanical status transition when it does.

    Architectural rule:
        This service owns WHETHER a lead qualifies and the direct model writes
        (status, qualified_at). It does NOT dispatch notifications, analytics,
        or CRM logs. Those are the responsibility of LeadTransitionService.
    """

    def __init__(self):
        # Only these three fields are mandatory for qualification.
        # All other fields (company, phone, industry, project_type, budget, timeline)
        # are optional enrichment — extracted and stored, but never block qualification.
        self.required_fields = ['full_name', 'email', 'requirements']

    def calculate_status(self, lead):
        """
        Evaluate the lead's qualification status.

        Returns:
            tuple: (status: str, missing_fields: list, just_qualified: bool)
                   just_qualified is True only when this call caused the transition
                   from 'gathering' to 'qualified'.
        """
        if not lead:
            return None, self.required_fields, False

        missing_fields = [
            field for field in self.required_fields
            if not getattr(lead, field)
        ]

        just_qualified = False

        if not missing_fields and lead.status == 'gathering':
            lead.status = 'qualified'
            # qualified_at is write-once: only set on the first qualification transition
            if lead.qualified_at is None:
                lead.qualified_at = timezone.now()
            lead.save(update_fields=['status', 'qualified_at'])
            just_qualified = True

        return lead.status, missing_fields, just_qualified

