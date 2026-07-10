# B10 AI Assistant

B10 AI Assistant is an AI-powered business consultant platform for B10 IT Solution. It serves as an intelligent front-line agent that assesses client needs, extracts lead information passively, and seamlessly feeds structured data into an internal CRM and Analytics backend for the sales team.

---

## Current Project Status

**Phase 6: Admin Dashboard React Frontend Implementation**

The core infrastructure and backend systems (Phases 1 through 5) are complete. The project has transitioned into building the `adminfrontend` using Next.js.

---

## Architecture Overview

The system follows a heavily decoupled **Modular Monolith** architecture for the backend API, paired with an independent Next.js App Router for the internal admin dashboard.

**Request Flow**:
```text
Browser (Client/Admin)
   │
   ▼
Next.js (Admin Dashboard) / Chat Widget (Public)
   │
   ▼
Nginx (Reverse Proxy)
   │
   ▼
Django REST API (Backend Monolith)
   │
   ├── Chat Service   ──▶ OpenRouter API (LLM)
   ├── Lead Service
   ├── Knowledge Service
   └── Analytics Service
             │
             ▼
        PostgreSQL (Database via Supabase)
             │
             ▼
           Redis (Cache & Message Broker)
             │
             ▼
          Celery (Background Tasks)
```

---

## Repository Structure

```text
b10backend/
├── adminfrontend/       # Internal React Dashboard for Sales/Admin
│   ├── app/             # Next.js App Router & Layouts
│   ├── features/        # Feature-sliced design (auth, leads, crm, roles)
│   ├── components/      # Shared shadcn UI elements
│   ├── lib/             # Axios clients and utility configurations
│   ├── services/        # External API interaction abstractions
│   └── types/           # Global TypeScript definitions
│
├── backend/             # Django Modular Monolith
│   ├── core/            # Main project configuration (settings, urls, wsgi)
│   ├── apps/            # Isolated business logic domains
│   │   ├── accounts/    # JWT Auth, Permissions, RBAC
│   │   ├── analytics/   # Event tracking & Funnel metrics
│   │   ├── chatbot/     # OpenRouter LLM integrations
│   │   ├── crm/         # Sales follow-ups and activity logging
│   │   └── leads/       # Lead extraction & automated qualification
│   └── tests/           # Dedicated unit and integration tests (in each app)
│
├── knowledge/           # Pre-configured AI Knowledge Base Sources
│   ├── company.json     # Business context
│   ├── services.json    # Service offerings
│   ├── industries.json  # Target verticals
│   └── faq.json         # Standard responses
│
└── docs/                # Comprehensive architectural and system documentation
    └── archive/         # Historical audit reports and completed implementation plans
```

---

## Technology Stack

**Frontend**:
- **Framework**: Next.js 16 (App Router)
- **UI/Styling**: React 19, Tailwind CSS v4, shadcn/ui
- **Data Fetching**: Axios, React Query
- **Testing**: Vitest, Playwright (Setup in progress)

**Backend**:
- **Framework**: Django 5.0, Django REST Framework 3.15
- **Database**: PostgreSQL (via Supabase)
- **Authentication**: SimpleJWT (Stateless JSON Web Tokens)
- **Task Queue**: Celery & Redis
- **AI Engine**: OpenRouter (Model: `openai/gpt-4o-mini`)
- **Documentation**: Swagger UI (`drf-spectacular`)

---

## Features

### ✅ Currently Implemented
- **AI Chatbot MVP**: Actively consults users using injected knowledge JSON sources.
- **Passive Lead Qualification**: Automatically extracts emails, phone numbers, and industries directly from chat sessions.
- **Automated Notifications**: Triggers alerts to the Sales team upon lead qualification.
- **Internal CRM & Analytics**: Records complete chat timeline logs, calculates conversion funnels, and schedules sales follow-ups.
- **RBAC Authentication**: Django Groups restrict access across `Admin`, `Sales`, and `Support` roles globally via JWT Bearer Tokens.
- **Deployment Hardening**: CORS configured, WhiteNoise static files, strict requirements pinned.

### 🚀 Planned (Phase 6+)
- **Next.js Admin Dashboard**: Full visual UI for tracking metrics and leads.
- **Knowledge Base Manager**: UI for editing `services.json` and `faq.json` directly.
- **User & Roles Management**: UI for assigning Sales and Support reps.

---

## Development Workflow & Local Setup

### Backend Local Setup
1. **Clone & Virtual Env**:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate  # Windows
   # or source venv/bin/activate # Linux/Mac
   ```
2. **Install Dependencies**:
   ```bash
   pip install -r backend/requirements.txt
   ```
3. **Configure Environment Variables**:
   Copy `backend/.env.example` to `backend/.env` and insert your Supabase `DATABASE_URL` and `OPENROUTER_API_KEY`.
4. **Migrate & Start**:
   ```bash
   cd backend
   python manage.py migrate
   python manage.py create_initial_admin  # Generates default superuser
   python manage.py runserver
   ```
5. **Run Backend Tests**:
   ```bash
   python manage.py test --settings=core.settings_test
   ```

### Frontend Local Setup
1. **Install Dependencies**:
   ```bash
   cd adminfrontend
   npm install
   ```
2. **Configure Environment Variables**:
   Copy `adminfrontend/.env.example` to `adminfrontend/.env.local`. Ensure `NEXT_PUBLIC_API_URL` points to your backend.
3. **Run Development Server**:
   ```bash
   npm run dev
   ```
4. **Run Frontend Builds & Tests**:
   ```bash
   npm run build
   # Testing tools (Vitest/Playwright) are currently being integrated
   ```

---

## Important Links & Documentation
- [System Architecture](docs/ARCHITECTURE.md)
- [API Reference & Schema](docs/API_REFERENCE.md)
- [Database Design](docs/DATABASE_DESIGN.md)
- [Security Specifications](docs/SECURITY_SPECIFICATION.md)
- [Repository Deep Guide](docs/repository_guide.md)
- **Local Swagger UI**: `http://localhost:8000/api/docs/` (Must have backend running)