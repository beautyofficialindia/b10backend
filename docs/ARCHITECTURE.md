# ARCHITECTURE.md

## Overview
The B10 IT Solution backend is a Modular Monolith built on Django 5.0 and Django REST Framework. It follows a highly decoupled event-driven flow where public AI consultations passively trigger internal CRM and Analytics micro-workflows.

## Core Pillars
1. **Public AI Chatbot**: Completely unauthenticated, highly throttled (`AnonRateThrottle`), relying on the OpenRouter LLM infrastructure.
2. **Passive Lead Engine**: Uses lightweight heuristics and regex to extract contact data (Email, Phone, Industry) from raw conversational text. 
3. **Internal CRM**: Restricted heavily by JWT Authorization, allowing Sales agents to manipulate leads and schedule follow-ups.
4. **Security**: Stateless JSON Web Tokens (`SimpleJWT`), mapped to Django Groups (`Admin`, `Sales`, `Support`).

## Database
Deployed entirely on **Supabase (PostgreSQL)**. 
- Uses UUIDs as primary external identifiers to prevent enumeration attacks.
- Enforces strict foreign-key relationships (`AnalyticsEvent` -> `ConversationSession`, `LeadActivity` -> `Lead`).
