# DEPLOYMENT_ARCHITECTURE.md

---

# Document Information

| Field | Value |
|-------|--------|
| Document Name | DEPLOYMENT_ARCHITECTURE.md |
| Project | B10 AI Assistant |
| Company | B10 IT Solution |
| Version | 1.0 |
| Status | Draft |
| Authors | Engineering Team |
| Last Updated | YYYY-MM-DD |

---

# Executive Summary

This document defines the deployment architecture for the B10 AI Assistant platform.

The platform consists of:

- Existing Next.js website frontend
- Django REST API backend
- PostgreSQL database
- Redis cache and task broker
- Celery background workers
- OpenRouter AI provider integration
- Future analytics and administration systems

The deployment architecture is designed to:

- Minimize operational complexity
- Support rapid startup iteration
- Maintain production readiness
- Provide scalability paths
- Enable future infrastructure evolution

---

# Deployment Objectives

## Primary Objectives

- Production-grade deployment
- Low operational overhead
- Secure infrastructure
- Horizontal scalability
- High observability
- Fault tolerance
- Disaster recovery readiness
- Environment parity

---

# Non Functional Requirements

## Availability

Target Uptime:

99.9%

---

## Recovery Objectives

Recovery Time Objective (RTO):

30 Minutes

Recovery Point Objective (RPO):

15 Minutes

---

## Performance Targets

Chat API Response:

< 3 Seconds

Health Endpoint:

< 500 ms

---

## Initial Capacity

Concurrent Users:

100+

Daily Users:

1000+

---

## Future Capacity

Concurrent Users:

5000+

Daily Users:

50000+

---

# Deployment Principles

1. Secure by Default
2. Container First
3. API First
4. Infrastructure as Code Ready
5. Environment Parity
6. Fault Tolerant
7. Observable
8. Low Operational Complexity
9. Horizontally Scalable
10. Disaster Recovery Ready

---

# Environment Strategy

## Development

Purpose:
Local engineering environment.

Characteristics:

- Docker Compose
- Local PostgreSQL
- Local Redis
- Debug enabled
- Mock services allowed

---

## Testing

Purpose:
Automated testing.

Characteristics:

- Isolated database
- Isolated Redis
- Mock OpenRouter
- Test fixtures

---

## Staging

Purpose:
Production-like validation.

Characteristics:

- Real OpenRouter
- Real PostgreSQL
- Limited traffic
- Monitoring enabled

---

## Production

Purpose:
Customer traffic.

Characteristics:

- Secure configuration
- Monitoring enabled
- Backups enabled
- Debug disabled
- HTTPS only

---

# Environment Configuration

## Environment Variables

### Django

```env
DEBUG=False
SECRET_KEY=
ALLOWED_HOSTS=
```

### PostgreSQL

```env
POSTGRES_DB=
POSTGRES_USER=
POSTGRES_PASSWORD=
DATABASE_URL=
```

### Redis

```env
REDIS_URL=
```

### OpenRouter

```env
OPENROUTER_API_KEY=
OPENROUTER_MODEL=
```

---

# Secrets Management

## Development

.env.dev

---

## Staging

.env.staging

---

## Production

.env.prod

Secrets must never:

- Exist in Git
- Exist in Docker images
- Be hardcoded

---

# Infrastructure Overview

## Phase 1 Architecture

```text
Internet
     │
     ▼
Nginx Reverse Proxy
     │
     ▼
Django API
     │
 ┌───┼────┐
 ▼   ▼    ▼
Redis PostgreSQL OpenRouter
     │
     ▼
Celery Worker
```

---

# Production Deployment Topology

```text
Internet
    │
    ▼
Nginx
    │
    ▼
Django REST API
    │
 ┌──┼──────┐
 ▼  ▼      ▼
Redis PostgreSQL OpenRouter
 │
 ▼
Celery Worker
```

---

# Request Flow

```text
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
   ▼
Chat Service
   │
   ▼
Knowledge Service
   │
   ▼
OpenRouter
   │
   ▼
Response
```

---

# Container Architecture

```text
Docker Network
│
├── nginx
├── django
├── postgres
├── redis
└── celery
```

---

# Container Responsibilities

## Nginx

Responsibilities:

- HTTPS termination
- Reverse proxy
- Compression
- Rate limiting
- Static asset serving

Port:

80
443

---

## Django

Responsibilities:

- REST APIs
- Business logic
- Chat service
- Lead service
- Authentication
- Administration APIs

Port:

8000

---

## PostgreSQL

Responsibilities:

- Persistent storage
- Conversations
- Leads
- Feedback
- Analytics

Port:

5432

---

## Redis

Responsibilities:

- Cache
- Celery broker
- Session storage
- Rate limiting state

Port:

6379

---

## Celery

Responsibilities:

- Background jobs
- Email sending
- Analytics aggregation
- Scheduled jobs

---

# Docker Network Architecture

## Public Network

Allowed Traffic:

Internet
↓

Nginx

---

## Internal Network

Allowed Traffic:

Nginx
↓

Django

Django
↓

Redis

Django
↓

PostgreSQL

Django
↓

OpenRouter

---

# Port Mapping Recommendations

| Service | Internal | External |
|---------|----------|----------|
| Nginx | 80 | 80 |
| Nginx TLS | 443 | 443 |
| Django | 8000 | Internal Only |
| PostgreSQL | 5432 | Internal Only |
| Redis | 6379 | Internal Only |

---

# Service Discovery

Phase 1:

Docker DNS

Examples:

```text
postgres:5432
redis:6379
django:8000
```

---

# Database Deployment

## Deployment Mode

Single PostgreSQL Container

Volume:

postgres_data

---

## Backup Policy

Full Backup:

Daily

Retention:

30 Days

---

## Recovery Testing

Monthly

---

# Redis Deployment

## Deployment Mode

Single Redis Container

Persistence:

Disabled initially.

Can be enabled later.

---

# Celery Deployment

## Workers

Phase 1:

1 Worker

Future:

Multiple workers.

Queues:

- default
- emails
- analytics

---

# OpenRouter Connectivity

## Connection Strategy

Django
↓

LLM Service Layer
↓

OpenRouter

---

## Timeout

15 Seconds

---

## Retries

2 Attempts

---

## Fallback

Graceful failure response.

---

# Logging Architecture

## Logs

Application Logs

Access Logs

Error Logs

Security Logs

OpenRouter Logs

Audit Logs

---

# Logging Flow

```text
Application
      │
      ▼
Structured Logs
      │
      ▼
Console/File
      │
      ▼
Monitoring System
```

---

# Monitoring Architecture

Metrics:

- CPU
- Memory
- Disk
- API Latency
- Database Connections
- Redis Usage
- OpenRouter Errors
- Lead Submission Rate

---

# Health Checks

## Django

Endpoint:

/api/v1/health

Checks:

- Database
- Redis
- OpenRouter

---

## PostgreSQL

Health Query:

```sql
SELECT 1;
```

---

## Redis

Health Command:

```text
PING
```

---

# Scaling Strategy

## Phase 1

Single VM

```text
Nginx
Django
Redis
PostgreSQL
Celery
```

---

## Phase 2

```text
Load Balancer
      │
      ▼
Multiple Django Containers
      │
      ▼
Redis
      │
      ▼
PostgreSQL
```

---

## Phase 3

```text
Load Balancer
       │
 ┌─────┼─────┐
 ▼     ▼     ▼
Django Django Django
       │
       ▼
Redis Cluster
       │
       ▼
Managed PostgreSQL
```

---

# High Availability Strategy

Phase 1:

Single VM.

Phase 2:

Multiple application containers.

Phase 3:

Managed database.

---

# Backup Strategy

## Database

Frequency:

Daily

Retention:

30 Days

---

## Configuration

Frequency:

Every deployment.

---

## Environment Files

Encrypted backups.

---

# Disaster Recovery Strategy

## Database Failure

1. Stop writes
2. Restore backup
3. Validate integrity
4. Resume traffic

---

## OpenRouter Outage

1. Retry
2. Fallback message
3. Log incident
4. Alert operators

---

## Deployment Failure

1. Stop rollout
2. Restore previous image
3. Validate health checks

---

# Deployment Pipeline

```text
Developer
     │
     ▼
GitHub
     │
     ▼
CI Pipeline
     │
     ▼
Tests
     │
     ▼
Build Docker Images
     │
     ▼
Staging
     │
     ▼
Smoke Tests
     │
     ▼
Production
```

---

# Release Strategy

Deployment Method:

Rolling Deployment

Future:

Blue-Green Deployment

---

# Rollback Strategy

1. Stop deployment
2. Restore previous container image
3. Restore configuration
4. Execute health checks
5. Resume traffic

Target:

< 15 Minutes

---

# CI/CD Recommendations

## CI

- Linting
- Unit Tests
- Integration Tests
- Security Scanning
- Docker Build Validation

---

## CD

- Build Image
- Deploy Staging
- Smoke Tests
- Manual Approval
- Deploy Production

---

# Infrastructure Security

Recommendations:

- HTTPS Only
- HSTS Enabled
- Secure Headers
- Internal Database Access
- Internal Redis Access
- Secrets in Environment Variables
- Principle of Least Privilege

---

# Cost Considerations

## Initial Infrastructure

Single Ubuntu VM

Recommended:

4 vCPU
8 GB RAM
100 GB SSD

Suitable for:

1000+ daily users.

---

## Future Scaling

Separate:

- Database
- Application Containers
- Monitoring Services

---

# Future Infrastructure Evolution

Phase 1

```text
Single VM
Docker Compose
```

Phase 2

```text
Multiple Django Containers
```

Phase 3

```text
Load Balancer
```

Phase 4

```text
Managed Database
Managed Redis
```

Phase 5

```text
Cloud Migration Ready
```

---

# Risks

- OpenRouter outage
- Database corruption
- Secret leakage
- Resource exhaustion
- Misconfigured deployments
- Dependency vulnerabilities

---

# Assumptions

- Small engineering team
- Low initial traffic
- Budget-conscious deployment
- Docker-based workflows
- Future scaling requirements

---

# Open Questions

1. Which cloud provider will be used?
2. Is managed PostgreSQL required?
3. Is managed Redis required?
4. Is object storage required?
5. Are multi-region deployments required?

---

# Architectural Decisions

- Modular monolith architecture
- Docker-first deployment
- Single VM initially
- PostgreSQL for persistence
- Redis for caching and broker
- Celery for background processing
- OpenRouter abstraction layer
- Future cloud portability

---

# Appendix

## Recommended Directory Structure

```text
deployments/
├── docker/
│   ├── Dockerfile
│   ├── docker-compose.dev.yml
│   ├── docker-compose.staging.yml
│   └── docker-compose.prod.yml
│
├── nginx/
│   ├── nginx.conf
│   └── sites/
│
├── scripts/
│   ├── deploy.sh
│   ├── backup.sh
│   ├── restore.sh
│   └── rollback.sh
│
└── monitoring/
    ├── healthchecks/
    └── alerts/
```

---

**End of Document**