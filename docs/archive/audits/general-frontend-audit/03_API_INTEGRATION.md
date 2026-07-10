# 03 — API Integration Audit

**Date:** 2026-07-08

---

## Axios Instance (lib/axios.ts)

| Property | Value |
|---|---|
| File | `lib/axios.ts` |
| Base URL | `process.env.NEXT_PUBLIC_API_URL \|\| http://localhost:8000/api/v1` |
| Default Headers | `Content-Type: application/json` |
| Token Storage | `localStorage.access_token` / `localStorage.refresh_token` |

---

## Request Interceptor

- Reads `localStorage.getItem('access_token')` on every request
- Attaches `Authorization: Bearer <token>` header
- Guards with `typeof window !== 'undefined'` (SSR-safe)

---

## Response Interceptor — Token Refresh Flow

```
401 received
  ├── Exclude: /auth/login, /auth/refresh
  ├── isRefreshing = true
  ├── Other 401s during refresh → queued in failedQueue[]
  ├── POST /auth/refresh/ with { refresh: refreshToken }
  │   ├── Success → store new access_token, replay queue, retry original request
  │   └── Failure → clear tokens, reject queue, DO NOT redirect (AuthGuard handles it)
  └── isRefreshing = false
```

> ⚠️ **BUG**: The refresh POST uses plain `axios.post()` (not the `api` instance).
> If `NEXT_PUBLIC_API_URL` is not set, this correctly falls back to the hardcoded URL.
> However, `data.access` is expected from the response — if the backend returns a different
> key (e.g., `data.token`), the refresh will silently fail and tokens will be cleared.

> ⚠️ **BUG**: `isRefreshing` is a module-level variable (not React state). On page
> navigation, it persists. If a refresh is in-flight and navigation occurs, the state
> may not reset correctly.

---

## React Query Configuration (providers/query-provider.tsx)

| Setting | Value |
|---|---|
| `staleTime` (default) | 60,000ms (1 minute) |
| `retry` (default) | 1 |
| `refetchOnWindowFocus` | `false` |

---

## Complete Endpoint List

### Auth Endpoints (features/auth/api/index.ts)

| Method | Frontend URL | Backend URL | File | Possible Mismatch |
|---|---|---|---|---|
| POST | `/auth/login/` | `api/v1/auth/login/` | features/auth/api/index.ts | ✅ Match |
| POST | `/auth/logout/` | `api/v1/auth/logout/` | features/auth/api/index.ts | ✅ Match |
| GET | `/auth/me/` | `api/v1/auth/me/` | features/auth/api/index.ts | ✅ Match |
| POST | `/auth/refresh/` | `api/v1/auth/refresh/` | lib/axios.ts (interceptor) | ✅ Match |

### Dashboard Endpoints (features/dashboard/api/index.ts)

| Method | Frontend URL | Backend URL | File | Possible Mismatch |
|---|---|---|---|---|
| GET | `/admin/analytics/` | `api/v1/admin/analytics/` | features/dashboard/api/index.ts | ✅ Match |
| GET | `/admin/dashboard/` | `api/v1/admin/dashboard/` | features/dashboard/api/index.ts | ✅ Match |
| GET | `/admin/analytics/timeline/` | `api/v1/admin/analytics/timeline/` | features/dashboard/api/index.ts | ✅ Match |
| GET | `/admin/analytics/funnel/` | `api/v1/admin/analytics/funnel/` | features/dashboard/api/index.ts | ✅ Match |
| GET | `/admin/leads/?page_size=5&ordering=-created_at` | `api/v1/admin/leads/` | features/dashboard/api/index.ts | ✅ Match |

### Analytics Endpoints (features/analytics/api/index.ts)

| Method | Frontend URL | Backend URL | File | Possible Mismatch |
|---|---|---|---|---|
| GET | `/admin/analytics/` | `api/v1/admin/analytics/` | features/analytics/api/index.ts | ⚠️ DUPLICATE of dashboard API |
| GET | `/admin/analytics/timeline/` | `api/v1/admin/analytics/timeline/` | features/analytics/api/index.ts | ⚠️ DUPLICATE |
| GET | `/admin/analytics/funnel/` | `api/v1/admin/analytics/funnel/` | features/analytics/api/index.ts | ⚠️ DUPLICATE |
| GET | `/admin/dashboard/` | `api/v1/admin/dashboard/` | features/analytics/api/index.ts | ⚠️ DUPLICATE |

> **⚠️ CRITICAL DUPLICATION**: `features/dashboard/api` and `features/analytics/api` call
> EXACTLY the same four backend endpoints. Different React Query cache keys mean 2x requests
> are fired when both pages are visited. Cache is not shared.

### Users Endpoints (features/users/api/index.ts)

| Method | Frontend URL | Backend URL | File | Possible Mismatch |
|---|---|---|---|---|
| GET | `/admin/users/?{params}` | `api/v1/admin/users/` | features/users/api/index.ts | ✅ Match |
| GET | `/admin/users/{id}/` | `api/v1/admin/users/{id}/` | features/users/api/index.ts | ✅ Match |
| POST | `/admin/users/` | `api/v1/admin/users/` | features/users/api/index.ts | ✅ Match |
| PATCH | `/admin/users/{id}/` | `api/v1/admin/users/{id}/` | features/users/api/index.ts | ✅ Match |
| POST | `/admin/users/{id}/activate/` | `api/v1/admin/users/{id}/activate/` | features/users/api/index.ts | ✅ Match |
| POST | `/admin/users/{id}/deactivate/` | `api/v1/admin/users/{id}/deactivate/` | features/users/api/index.ts | ✅ Match |
| POST | `/admin/users/{id}/reset-password/` | `api/v1/admin/users/{id}/reset-password/` | features/users/api/index.ts | ✅ Match |
| POST | `/admin/users/bulk-activate/` | `api/v1/admin/users/bulk-activate/` | features/users/api/index.ts | ✅ Match |
| POST | `/admin/users/bulk-deactivate/` | `api/v1/admin/users/bulk-deactivate/` | features/users/api/index.ts | ✅ Match |
| GET | `/admin/users/{id}/audit-log/?page={p}` | `api/v1/admin/users/{id}/audit-log/` | features/users/api/index.ts | ✅ Match |

> **⚠️ TYPE MISMATCH**: `usersApi.getById` return type is declared as `Promise<{ data: UserDetail }>`,
> but the frontend reads `data?.data`. Backend response wrapped in `success_response()` includes
> `{ success: true, data: ..., meta: ... }`. This wrapping must be consistent on the backend.

### Leads Endpoints (features/leads/api/index.ts)

| Method | Frontend URL | Backend URL | File | Possible Mismatch |
|---|---|---|---|---|
| GET | `/admin/leads/?{params}` | `api/v1/admin/leads/` | features/leads/api/index.ts | ✅ Match |
| GET | `/admin/leads/{id}/` | `api/v1/admin/leads/{uuid}/` | features/leads/api/index.ts | ✅ Match |
| PATCH | `/admin/leads/{id}/` | `api/v1/admin/leads/{uuid}/` | features/leads/api/index.ts | ✅ Match |

> **⚠️ RESPONSE FORMAT MISMATCH**: `LeadListResponse` expects `{ count, next, previous, results }` (DRF standard pagination).
> But `leads/page.tsx` reads `data.count` and `data.results`.
> The `DashboardSummaryAPIView` returns raw dict (no DRF envelope).
> `getRecentLeads` in dashboard expects `{ results: Lead[] }` — this matches DRF pagination. ✅

### Knowledge Base Endpoints (features/knowledge/api/index.ts)

| Method | Frontend URL | Backend URL | File | Possible Mismatch |
|---|---|---|---|---|
| GET | `/admin/kb/entries/?{params}` | `api/v1/admin/kb/entries/` | features/knowledge/api/index.ts | ✅ Match |
| GET | `/admin/kb/entries/{id}/` | `api/v1/admin/kb/entries/{uuid}/` | features/knowledge/api/index.ts | ✅ Match |
| POST | `/admin/kb/entries/` | `api/v1/admin/kb/entries/` | features/knowledge/api/index.ts | ✅ Match |
| PATCH | `/admin/kb/entries/{id}/` | `api/v1/admin/kb/entries/{uuid}/` | features/knowledge/api/index.ts | ✅ Match |
| DELETE | `/admin/kb/entries/{id}/` | `api/v1/admin/kb/entries/{uuid}/` | features/knowledge/api/index.ts | ✅ Match |
| POST | `/admin/kb/entries/{id}/publish/` | `api/v1/admin/kb/entries/{uuid}/publish/` | features/knowledge/api/index.ts | ✅ Match |
| POST | `/admin/kb/entries/{id}/unpublish/` | `api/v1/admin/kb/entries/{uuid}/unpublish/` | features/knowledge/api/index.ts | ✅ Match |
| POST | `/admin/kb/entries/{id}/archive/` | `api/v1/admin/kb/entries/{uuid}/archive/` | features/knowledge/api/index.ts | ✅ Match |

### Roles Endpoints (features/roles/api/index.ts)

| Method | Frontend URL | Backend URL | File | Possible Mismatch |
|---|---|---|---|---|
| GET | `/admin/roles/?{params}` | `api/v1/admin/roles/` | features/roles/api/index.ts | ✅ Match |
| GET | `/admin/roles/{id}/` | `api/v1/admin/roles/{id}/` | features/roles/api/index.ts | ✅ Match |
| POST | `/admin/roles/` | `api/v1/admin/roles/` | features/roles/api/index.ts | ✅ Match |
| PATCH | `/admin/roles/{id}/` | `api/v1/admin/roles/{id}/` | features/roles/api/index.ts | ✅ Match |
| DELETE | `/admin/roles/{id}/` | `api/v1/admin/roles/{id}/` | features/roles/api/index.ts | ✅ Match |
| GET | `/admin/roles/permissions/` | `api/v1/admin/roles/permissions/` | features/roles/api/index.ts | ✅ Match |
| PUT | `/admin/roles/{id}/set-permissions/` | `api/v1/admin/roles/{id}/set-permissions/` | features/roles/api/index.ts | ✅ Match |
| GET | `/admin/roles/{id}/users/` | `api/v1/admin/roles/{id}/users/` | features/roles/api/index.ts | ✅ Match |
| POST | `/admin/roles/{id}/assign-users/` | `api/v1/admin/roles/{id}/assign-users/` | features/roles/api/index.ts | ✅ Match |
| POST | `/admin/roles/{id}/remove-users/` | `api/v1/admin/roles/{id}/remove-users/` | features/roles/api/index.ts | ✅ Match |

### Settings Endpoints (features/settings/api/index.ts)

| Method | Frontend URL | Backend URL | File | Possible Mismatch |
|---|---|---|---|---|
| GET | `/admin/settings/?{params}` | `api/v1/admin/settings/` | features/settings/api/index.ts | ✅ Match |
| GET | `/admin/settings/{category}/` | `api/v1/admin/settings/{category}/` | features/settings/api/index.ts | ✅ Match |
| PATCH | `/admin/settings/{category}/` | `api/v1/admin/settings/{category}/` | features/settings/api/index.ts | ✅ Match |
| GET | `/settings/public/` | `api/v1/settings/public/` | features/settings/api/index.ts | ✅ Match |

> ⚠️ **SETTINGS URL CONFLICT**: Both `api/v1/admin/settings/` and `api/v1/settings/` map to
> the SAME Django url file `settings_management/urls.py` (both included in `core/urls.py`).
> The `public/` endpoint is mounted under both paths. This is technically harmless but confusing.

---

## Summary of API Issues

| Severity | Issue |
|---|---|
| 🔴 HIGH | `features/dashboard/api` and `features/analytics/api` call identical endpoints with different cache keys |
| 🔴 HIGH | Response wrapper mismatch possible: some endpoints use `success_response()` envelope, others (analytics) return raw data |
| 🟡 MEDIUM | Token refresh uses raw axios, not the api instance — second base URL hardcoded |
| 🟡 MEDIUM | Module-level `isRefreshing` flag could get stuck if a network error occurs during refresh |
| 🟡 MEDIUM | No global error handler for non-401 errors (500, 403, 429 handled per-component) |
| 🟢 LOW | Leads list uses DRF standard pagination (`count/results`), but Users/Knowledge/Roles use custom `success_response` wrapper |
