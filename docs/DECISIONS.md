# DECISIONS.md

Decision 001
Use Django + DRF.
Status: Approved
Reason: Future backend requirements.

Decision 002
Use PostgreSQL (via Supabase).
Status: Approved
Reason: Reliability, scalability, and ease of cloud access.

Decision 003
No Redis or Celery in Phase 1.
Status: Approved
Reason: Local development machine has limited resources. Can be added in later phases.

Decision 004
Use OpenRouter (openai/gpt-4o-mini).
Status: Approved
Reason: Model flexibility and cost-effectiveness.

Decision 005
Use Modular Monolith Architecture.
Status: Approved
Reason: Lower operational complexity.

Decision 006
Knowledge remains JSON-based.
Status: Approved
Reason: MVP simplicity.

Decision 007
No LangChain in MVP.
Status: Approved.

Decision 008
No Vector Database in MVP.
Status: Approved.

Decision 009
No Docker in Phase 1.
Status: Approved
Reason: Local development machine has limited resources.

Decision 010
Retrieval-scoped knowledge loading (Keyword-based).
Status: Approved
Reason: Avoid injecting all knowledge files into every prompt to save LLM tokens and improve response focus. Uses fast regex/keyword heuristics.

Decision 011
UUID for internal `id` and external `session_id`.
Status: Approved
Reason: Separating internal primary keys from external identifiers improves security and flexibility.

Decision 012
Strict DRF Throttling.
Status: Approved
Reason: Immediate implementation of AnonRateThrottle (10/min) to protect OpenRouter API costs from abuse.