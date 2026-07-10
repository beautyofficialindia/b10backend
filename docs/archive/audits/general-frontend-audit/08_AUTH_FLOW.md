# 08 — Auth Flow Audit

**Date:** 2026-07-08

---

## Token Storage

| Item | Storage | Key |
|---|---|---|
| Access Token | `localStorage` | `access_token` |
| Refresh Token | `localStorage` | `refresh_token` |

> **⚠️ SECURITY NOTE**: Tokens stored in `localStorage` are accessible to JavaScript
> (XSS risk). For a production admin panel, `httpOnly` cookies are recommended.
> This is an accepted tradeoff for SPA simplicity, but should be documented.

---

## Login Flow

```
User submits LoginForm
  → loginMutation.mutateAsync({ username, password })
  → POST /api/v1/auth/login/
  ← { access, refresh }
  → localStorage.setItem('access_token', access)
  → localStorage.setItem('refresh_token', refresh)
  → queryClient.invalidateQueries(['auth', 'me'])
  → router.push('/dashboard')
  → useAuth() query fires: GET /api/v1/auth/me/
  ← User object
  → isAuthenticated = true
  → AuthGuard renders children
```

### Login Error Handling

| Status Code | Frontend Message |
|---|---|
| 401 | "Invalid username or password." |
| 403 | "Your account has been deactivated." |
| No response | "Unable to connect to server." |
| Other | "An unexpected error occurred." |

---

## Logout Flow

```
User clicks "Log out" in header dropdown
  → useAuth().logout()
  → GET refresh_token from localStorage
  → POST /api/v1/auth/logout/ { refresh }  (if token exists)
  → [catch any errors — silently ignored]
  → localStorage.removeItem('access_token')
  → localStorage.removeItem('refresh_token')
  → queryClient.clear()  ← clears ALL React Query cache
  → router.push('/login')
```

> ⚠️ **POTENTIAL BUG**: If `router.push('/login')` fires before the logout API responds
> and the user navigates away, the logout POST is cancelled. The refresh token may remain
> valid on the backend. This is an edge case but can leave orphaned sessions.

---

## Protected Routes

All routes under `app/(dashboard)/` are protected via:

```tsx
// app/(dashboard)/layout.tsx
<AuthGuard>
  <AppShell>{children}</AppShell>
</AuthGuard>
```

### AuthGuard Logic

```
AuthGuard renders
  → useAuth() → { isLoading, isAuthenticated }
  → if (isLoading): render <FullPageLoader>
  → if (!isLoading && !isAuthenticated): router.replace('/login')
  → if (!isAuthenticated): render <FullPageLoader>  ← NOTE: renders loader WHILE redirecting
  → if (isAuthenticated): render children
```

> **⚠️ RACE CONDITION**: `AuthGuard` renders `<FullPageLoader>` in BOTH the loading state
> AND the "not authenticated, redirect pending" state. This means during the redirect,
> the user briefly sees a loading spinner before `/login` page appears. Minor UX issue.

> **⚠️ REDIRECT LOOP RISK**: `app/page.tsx` uses Next.js server-side `redirect('/dashboard')`.
> This fires BEFORE client-side auth check. Flow:
> 1. User visits `/` (not logged in)
> 2. Server redirect → `/dashboard`
> 3. AuthGuard check → `isAuthenticated = false`
> 4. AuthGuard redirect → `/login`
> This is 2 extra redirects. While functionally correct, it adds latency and can
> confuse browser history.

---

## Token Refresh Flow (Interceptor)

```
Any API request returns 401
  ├── Is this /auth/login or /auth/refresh? → Skip refresh, reject
  ├── Is isRefreshing = true? → Queue request in failedQueue
  └── Else:
      → isRefreshing = true
      → originalRequest._retry = true
      → GET refresh_token from localStorage
      → If no refresh_token: throw error → clear tokens → reject
      → POST /api/v1/auth/refresh/ { refresh: refreshToken }
      ← { access: newAccessToken }  [or { token: ...} ???]
      → localStorage.setItem('access_token', newAccessToken)
      → processQueue(null, newAccessToken)  ← replay all queued requests
      → retry originalRequest with new token
      → isRefreshing = false
      [On refresh failure]:
      → processQueue(error, null)
      → localStorage.removeItem('access_token')
      → localStorage.removeItem('refresh_token')
      → isRefreshing = false
      → DO NOT redirect (AuthGuard handles it)
```

### Refresh Critical Issues

| Issue | Detail |
|---|---|
| **Response key assumption** | `const { data } = await axios.post(...)` → `data.access`. Backend `RefreshAPIView` must return `{ access: "..." }`. If it returns `{ token: "..." }` or `{ access_token: "..." }`, this silently fails and logs out the user. |
| **Module-level flag** | `isRefreshing` is not reset on unhandled exceptions — if the refresh POST throws a network error (not a JSON error), the `finally` block resets it correctly ✅. |
| **Queue memory leak** | `failedQueue` is never bounded — if many requests arrive during a long refresh, all are queued. This is fine in practice. |
| **No redirect from interceptor** | Comment says "let AuthGuard handle routing" — this is correct design ✅. |

---

## Redirect Flow Summary

| Scenario | What Happens |
|---|---|
| Unauthenticated user visits `/` | Server redirect → `/dashboard` → AuthGuard → `/login` |
| Unauthenticated user visits `/dashboard` | AuthGuard → `/login` |
| Authenticated user visits `/login` | Login page `useEffect` → `/dashboard` |
| Token expired during use | Interceptor refreshes token silently → request retried |
| Refresh token expired | Tokens cleared → AuthGuard detects → `/login` |
| User logs out | Tokens cleared → `router.push('/login')` |

---

## Session Persistence

| Scenario | Behavior |
|---|---|
| Page refresh (F5) | Tokens remain in localStorage → `useAuth` refetches `/auth/me/` → session restored |
| Tab close and reopen | Same — tokens persist in localStorage |
| Different browser | No session — localStorage is tab-specific by origin |

---

## Race Conditions Identified

| Race | Description | Severity |
|---|---|---|
| Login → Invalidate → Navigate | `invalidateQueries` fires, navigation starts. If `/auth/me/` refetch is slow, brief auth flash | Low |
| Multiple 401s during refresh | Correctly handled via `failedQueue` | ✅ Resolved |
| AuthGuard renders while isRefreshing | Shows spinner — acceptable | Low |
| `hasAccessToken()` in `enabled` prop | Called at render time. If token added between renders, hook may not re-enable | Medium |
