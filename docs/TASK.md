# TASK.md

Current Task:
Phase 1 Validation & Preparation for Phase 2

Phase 1 Scope (Completed):
- [x] 1. POST /api/v1/chat/
- [x] 2. GET /api/v1/health/ (Added for monitoring)
- [x] 3. OpenRouter integration
- [x] 4. Knowledge loading (Scoped by Intent)
- [x] 5. Prompt building (Strict rules)
- [x] 6. Domain restrictions
- [x] 7. Conversation state (Postgres)
- [x] 8. Error handling & Payload Validation
- [x] 9. DRF Throttling

Out of Scope (For MVP Phase 1):
- Docker Setup
- Redis / Celery
- Authentication
- Analytics
- CRM / Lead Tracking
- Email
- Admin Dashboard

Acceptance Criteria (Phase 1):
- [x] Answers company questions
- [x] Answers service questions
- [x] Answers FAQs
- [x] Recommends services
- [x] Refuses unrelated questions
- [x] Guides users toward consultation
- [x] Returns 429 when rate limited
- [x] Responds safely when OpenRouter fails