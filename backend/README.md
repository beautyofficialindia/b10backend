# B10 AI Assistant - Backend API

This directory contains the Django REST Framework (DRF) backend for the B10 AI Assistant. It serves as a **Modular Monolith**, providing decoupled endpoints for the public AI chat widget and the private internal admin dashboard.

---

## Backend Architecture

The application is structured as a **Modular Monolith**. Rather than a single massive app, functionality is strictly siloed into domain-specific Django apps inside the `apps/` directory.

```text
backend/
├── core/                  # Django project root (settings.py, urls.py)
├── apps/                  # Isolated business domains
│   ├── accounts/          # JWT issuing, User models, Role-Based Access Control
│   ├── analytics/         # System events, Dashboard funnels & timelines
│   ├── chatbot/           # OpenRouter LLM orchestration, message parsing
│   ├── crm/               # Internal sales workflow, activity logging, follow-ups
│   ├── knowledge_base/    # Knowledge domain (Future Phase 6 feature)
│   ├── leads/             # Lead extraction via AI, auto-qualification, mailing
│   ├── role_management/   # Role domain (Future Phase 6 feature)
│   ├── settings_management/# System settings domain (Future Phase 6 feature)
│   └── user_management/   # User domain (Future Phase 6 feature)
└── requirements.txt       # Pinned production requirements
```

### App Responsibilities
- **`chatbot`**: Handles public anonymous AI consultation interactions. Acts as the primary client facing interface.
- **`leads`**: Parses chat context passively to extract PII (email, phone, industry) and triggers email notifications to the internal team.
- **`crm`**: Empowers internal sales members to log activities, change lead statuses, and schedule follow-ups.
- **`analytics`**: Centralized event tracking that logs usage to construct dashboard funnel metrics and timeline visualizations.
- **`accounts`**: Manages User profiles, issues JSON Web Tokens, and enforces the RBAC (Admin, Sales, Support) rules.

---

## Authentication & Authorization (RBAC)

The API is secured using **SimpleJWT** for stateless token authentication.

- **Tokens**: `Access` tokens (short-lived) and `Refresh` tokens (long-lived) are issued via `/api/v1/auth/token/`.
- **RBAC**: Handled natively using Django `Groups`.
  - `Admin`: Full access to all resources.
  - `Sales`: Access to CRM workflows, Leads, and general Analytics.
  - `Support`: Access to view chats and update KB entries.
- All non-public endpoints require the HTTP Header: `Authorization: Bearer <token>`.

---

## Database & Data Modeling

- **Database**: PostgreSQL (hosted on Supabase for production/staging).
- **Migration Policy**: Standard Django `makemigrations` and `migrate`.
- SQLite is utilized **strictly** for fast, in-memory local testing `core.settings_test.py`.

---

## API Documentation & Versioning

- **Versioning**: Implemented via URL routing (e.g., `/api/v1/...`).
- **Swagger UI**: The repository utilizes `drf-spectacular` to automatically generate OpenAPI 3 schemas.
- **Accessing Docs**: When running locally, navigate to `http://localhost:8000/api/docs/` to view and interact with the Swagger documentation.

---

## Local Development Setup

### 1. Environment Configuration
Ensure you have Python 3.11+ installed.
Create a `.env` file in the `backend/` directory by duplicating `.env.example`:
```env
DEBUG=True
SECRET_KEY=local-dev-secret
DATABASE_URL=postgresql://<user>:<password>@<supabase-host>:<port>/<db>
OPENROUTER_API_KEY=your-openrouter-key
OPENROUTER_MODEL=openai/gpt-4o-mini
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOW_ALL_ORIGINS=True
ADMIN_USERNAME=admin
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=ChangeMe123!
```

### 2. Installation & Running
```bash
# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create initial admin (Uses env variables)
python manage.py create_initial_admin

# Start the server
python manage.py runserver
```

---

## Testing

The backend relies on the native `unittest` / Django `TestCase` framework augmented with pytest configurations (if required in future). Currently, tests execute in memory utilizing SQLite to prevent database state corruption.

```bash
# Run the complete test suite
python manage.py test --settings=core.settings_test
```

---

## Deployment overview
The application is designed for containerized deployment (Docker).
- **Static Files**: Served via `WhiteNoise` (Requires running `python manage.py collectstatic` during the build phase).
- **Proxy**: Nginx routes `/api/` traffic to Gunicorn/Uvicorn.
- **Environment**: All configuration must be provided via System Environment Variables overriding the `.env` fallbacks.
