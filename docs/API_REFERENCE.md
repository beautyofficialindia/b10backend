# API_REFERENCE.md

The API is fully documented via an interactive OpenAPI 3.0 UI.

## Accessing Documentation
1. Run the local server: `python manage.py runserver`
2. Navigate to: `http://localhost:8000/api/docs/`
3. View the raw schema: `http://localhost:8000/api/schema/`

## Core Endpoint Overview

### Public Routes
- `POST /api/v1/chat/`: Starts or continues an AI conversation. Does not require authentication.
- `GET /health/`: Passive ping endpoint for cloud load balancers.

### Authentication Routes
- `POST /api/v1/auth/login/`: Accepts `username`/`password`, returns `access` and `refresh` tokens.
- `POST /api/v1/auth/refresh/`: Accepts `refresh` token, returns new `access` token.
- `POST /api/v1/auth/logout/`: Accepts `refresh` token, blacklists it to prevent reuse.
- `GET /api/v1/auth/me/`: Returns profile and active `role`. Requires `Authorization: Bearer <token>`.

### Protected Admin Routes (Requires Bearer Token)
- `GET /api/v1/admin/leads/`: Returns paginated lists of extracted leads.
- `GET /api/v1/admin/analytics/dashboard/`: Returns aggregate chat/message metrics.
- `PATCH /api/v1/admin/crm/followups/<id>/`: Modifies scheduled sales follow-ups.
