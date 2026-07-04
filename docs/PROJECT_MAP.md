# PROJECT_MAP.md

b10backend/
├── backend/
│   ├── core/
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py / asgi.py
│   ├── apps/
│   │   ├── accounts/ (JWT Auth, Permissions, create_initial_admin command)
│   │   ├── chatbot/ (ChatService, OpenRouter Integration)
│   │   ├── leads/ (Lead extraction, Qualification, Notifications)
│   │   ├── analytics/ (Event tracking, Dashboard metrics)
│   │   └── crm/ (Lead activities, Status histories, Follow-ups)
│   └── tests/ (Distributed inside each app directory)
├── knowledge/
│   ├── company.json
│   ├── services.json
│   ├── industries.json
│   └── faq.json
├── docs/ (System Architecture, API Specs, Deployment Guides)
├── requirements.txt (Strict pinned dependencies)
├── .env (Local environment variables)
└── .env.example (Environment template)

## Responsibilities

chatbot
→ Handles anonymous AI business consultation interactions.

leads
→ Extracts PII, auto-qualifies leads, triggers email notifications.

analytics
→ Centralized event logging for charts and funnels.

crm
→ Automated internal sales tracking, scheduling, and activity logging.

accounts
→ Issues JWTs, manages User profiles, enforces RBAC (Admin, Sales, Support).