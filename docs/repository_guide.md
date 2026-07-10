# Repository Guide

Welcome to the definitive navigation guide for the **B10 AI Assistant** repository. This document serves to orient new engineers, deployment specialists, and maintainers by explaining the *why* and *where* of the project's layout.

---

## Repository Philosophy

The B10 AI Assistant is engineered using a **Decoupled Modular Monolith** approach. 

- **Decoupled**: The frontend (`adminfrontend/`) and the backend (`backend/`) are completely distinct applications. They do not share build pipelines, dependencies, or direct code. They communicate exclusively over RESTful APIs via HTTP.
- **Modular Monolith**: The backend avoids the complexity of microservices but retains strict internal boundaries. Each business domain (e.g., `leads`, `crm`, `chatbot`) is isolated into its own Django app. 

---

## High-Level Architecture Diagram

```mermaid
flowchart TD
    %% Define external actors
    User((Public User))
    Admin((Internal Sales/Admin))

    %% Define frontend environments
    subgraph Frontend Layer
        Widget[Public Chat Widget]
        AdminApp[Next.js Admin Dashboard\n'adminfrontend/']
    end

    %% Define proxy
    Proxy[Nginx Reverse Proxy]

    %% Define backend environment
    subgraph Backend Layer [Django Modular Monolith]
        AuthApp(Accounts / Auth API)
        ChatApp(Chatbot API)
        LeadApp(Leads API)
        CRMApp(CRM API)
        AnalyticsApp(Analytics API)
    end

    %% Define Infrastructure
    DB[(PostgreSQL)]
    Redis[(Redis Cache & Queue)]
    Celery[Celery Workers]

    %% Define External Services
    OpenRouter[OpenRouter API\n(LLM Engine)]

    %% Map connections
    User -->|Interacts with| Widget
    Admin -->|Logs into| AdminApp

    Widget -->|HTTP Requests| Proxy
    AdminApp -->|HTTP Requests / JWT| Proxy

    Proxy -->|Routes /api/v1/*| AuthApp
    Proxy -->|Routes /api/v1/*| ChatApp
    Proxy -->|Routes /api/v1/*| LeadApp
    Proxy -->|Routes /api/v1/*| CRMApp
    Proxy -->|Routes /api/v1/*| AnalyticsApp

    %% Backend internal routing
    AuthApp --> DB
    ChatApp --> OpenRouter
    ChatApp --> DB
    LeadApp --> DB
    LeadApp --> Redis
    CRMApp --> DB
    AnalyticsApp --> DB

    %% Async Tasks
    Redis --- Celery
    Celery -->|Executes background emails| LeadApp
```

---

## Deep Folder Explanations

### `/backend`
**Purpose**: The central API server and database manager.
**Responsibilities**: Processing business logic, managing database transactions, authenticating requests, interacting with OpenRouter, and processing asynchronous Celery tasks.
**Important Files/Folders**:
- `apps/`: The heart of the backend. Contains all the business domains. If you need to change how a lead is qualified, you go to `apps/leads/`.
- `core/`: The Django configuration center. `settings.py` manages environment variables and installed apps. `urls.py` acts as the master router.
- `requirements.txt`: The strictly pinned list of production Python packages.

### `/adminfrontend`
**Purpose**: The visual interface for the internal team to manage the system.
**Responsibilities**: Providing UI for CRM management, rendering analytics funnels, and managing role-based views using React.
**Important Files/Folders**:
- `app/`: Next.js App Router. Contains the physical route paths (e.g., `app/(dashboard)/leads/page.tsx`).
- `features/`: The business logic of the frontend. If you need to change how the Lead Table fetches data, you go to `features/leads/`.
- `lib/axios.ts`: Critical file configuring the base HTTP client and handling automatic JWT refresh interceptors.
- `package.json`: Manages Node dependencies and build scripts.

### `/knowledge`
**Purpose**: The AI's brain.
**Responsibilities**: Providing static, pre-defined factual information about B10 IT Solution. The backend `chatbot` service reads these files to inject context into the LLM prompts.
**Important Files/Folders**:
- `company.json`: Core business details.
- `services.json`: Detailed definitions of what the company sells (used for recommendations).
- `industries.json`: Target markets.

### `/docs`
**Purpose**: The system's blueprint.
**Responsibilities**: Storing architectural decisions, API specifications, and historical context.
**Important Files/Folders**:
- `archive/`: A clean storage folder containing past audits, old implementation reports, and completed checklists to keep the root directory free of clutter.
- `CURRENT_PHASE.md`: The active status of the project.
- `TESTING_STRATEGY.md`: The blueprint for how quality is maintained via Vitest, pytest, and Playwright.

---

## Frontend-Backend Contract

Understanding how `adminfrontend` talks to `backend` is critical for feature development.

1. **Authentication**: The frontend sends credentials to the backend `/api/v1/auth/token/`. The backend returns a short-lived `access` token and a long-lived `refresh` token.
2. **Persistence**: The frontend stores these tokens securely (typically in HTTP-only cookies or secure local storage mechanisms).
3. **Interception**: Every time the frontend needs data (e.g., fetching a list of leads), the Axios interceptor in `lib/axios.ts` attaches `Authorization: Bearer <access_token>`.
4. **Validation**: The backend verifies the token. If it is valid and the user has the correct Django Group (e.g., `Sales`), it returns the JSON data. If the token is expired, the backend returns a `401 Unauthorized`.
5. **Rotation**: Upon receiving a `401`, the frontend Axios interceptor automatically pauses the request, calls the backend refresh endpoint using the `refresh` token, receives a new `access` token, and retries the original request seamlessly without user disruption.
