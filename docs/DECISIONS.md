# DECISIONS.md

Decision 001: Use Django + DRF.
Status: Approved. Reason: Future backend requirements.

Decision 002: Use PostgreSQL (via Supabase).
Status: Approved. Reason: Reliability, scalability, and ease of cloud access.

Decision 003: No Redis or Celery in Phase 1-8.
Status: Approved. Reason: Keep architecture simple and deployable anywhere.

Decision 004: Use OpenRouter (openai/gpt-4o-mini).
Status: Approved. Reason: Model flexibility and cost-effectiveness.

Decision 005: Use Modular Monolith Architecture.
Status: Approved. Reason: Lower operational complexity.

Decision 006: Knowledge remains JSON-based.
Status: Approved. Reason: MVP simplicity.

Decision 007: No LangChain or Vector Database in MVP.
Status: Approved.

Decision 008: Retrieval-scoped knowledge loading (Keyword-based).
Status: Approved. Reason: Avoid injecting all knowledge files into every prompt to save LLM tokens. Uses fast regex/keyword heuristics.

Decision 009: Strict DRF Throttling.
Status: Approved. Reason: Protect OpenRouter API costs from abuse.

Decision 010: Use `djangorestframework-simplejwt`.
Status: Approved. Reason: Industry standard, stateless token architecture preventing database lookups on every request, with secure refresh token blacklisting.

Decision 011: Use Django Groups for Role-Based Access Control (RBAC).
Status: Approved. Reason: Avoids building a complex custom permissions system when Django already supports normalized `Group` relationships. Custom `IsAdminOrSales` DRF Permission classes overlay this nicely.

Decision 012: Use `drf-spectacular` for OpenAPI documentation.
Status: Approved. Reason: Superior to `drf-yasg` for modern Django 5.x and DRF architectures, providing perfect integration with our custom `APIView` serializers.

Decision 013: Use `WhiteNoise` for static file serving.
Status: Approved. Reason: Allows the Python WSGI application to securely compress and serve its own static files (like the Swagger UI interface) without requiring a separate Nginx or Apache server in production.