# TASK.md

Current Task:
Phase 8 Validation & Preparation for Phase 9 Frontend

Out of Scope (Completed in previous phases):
- Authentication (Completed in Phase 7)
- Analytics (Completed in Phase 5)
- CRM / Lead Tracking (Completed in Phases 2-6)
- Email (Completed in Phase 3)
- API Documentation (Completed in Phase 8.2)

Acceptance Criteria (Backend fully validated):
- [x] Chat API securely throttles and integrates with OpenRouter
- [x] Lead Service passively extracts contact info and auto-qualifies
- [x] JWT endpoints issue short-lived access and long-lived refresh tokens
- [x] Logout successfully blacklists refresh tokens
- [x] Admin, Sales, and Support roles strictly enforced via Custom Permissions
- [x] Swagger UI perfectly renders request bodies at `/api/docs/`
- [x] Unit tests pass locally