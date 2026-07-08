# 02 — Environment Variables Audit

**Date:** 2026-07-08

---

## Files Inspected

| File | Exists |
|---|---|
| `.env.local` | ✅ Yes |
| `.env.example` | ✅ Yes |
| `.env` | ❌ Not found |
| `.env.production` | ❌ Not found |

---

## Variables in .env.local

| Variable | Value | Used? |
|---|---|---|
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000/api/v1` (MASKED — local dev URL only) | ✅ Yes |

---

## Variables in .env.example

| Variable | Value |
|---|---|
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000/api/v1` |

---

## Variable Usage Analysis

### NEXT_PUBLIC_API_URL

Used in two places:

1. **`lib/axios.ts` (line 4):**
   ```ts
   baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1',
   ```

2. **`lib/axios.ts` (line 69 — token refresh):**
   ```ts
   `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'}/auth/refresh/`
   ```

> ⚠️ **ISSUE**: The refresh endpoint is constructed via raw string concatenation using
> `process.env.NEXT_PUBLIC_API_URL` **directly** in the response interceptor, bypassing
> the axios instance `baseURL`. This means the refresh call goes through plain `axios.post()`
> not through the configured `api` instance. This is intentional to avoid infinite loops,
> but creates a second place where the base URL must be in sync.

---

## Missing Required Variables

| Variable | Status | Impact |
|---|---|---|
| `NEXT_PUBLIC_API_URL` set to production URL | ❌ Only set to localhost | **CRITICAL**: Production deployment will hit `localhost:8000` if not overridden |

---

## Unused Variables

None detected. The project only declares and uses a single environment variable.

---

## Recommendations

| Item | Detail |
|---|---|
| No production `.env` | No `.env.production` exists — relies entirely on deployment environment variables |
| Hard-coded fallback | Both axios locations fall back to `http://localhost:8000/api/v1` — safe for dev, dangerous if env is not set in prod |
| No `NEXT_PUBLIC_SENTRY_DSN` or logging variables | No error tracking environment variables configured |
| No feature flags via env | All feature flags are managed via backend Settings API, not env vars |
