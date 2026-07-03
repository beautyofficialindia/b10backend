# ARCHITECTURE_OVERVIEW.md

Browser
   │
   ▼
Next.js Website
   │
   ▼
Nginx
   │
   ▼
Django API
   │
   ├── Chat Service
   ├── Lead Service
   ├── Knowledge Service
   └── Analytics Service
            │
            ▼
      OpenRouter Client
            │
            ▼
       PostgreSQL
            │
            ▼
           Redis
            │
            ▼
          Celery

Knowledge Sources:

knowledge/
├── company.json
├── services.json
├── industries.json
├── faq.json
└── prompts/

Architecture Style:
Modular Monolith