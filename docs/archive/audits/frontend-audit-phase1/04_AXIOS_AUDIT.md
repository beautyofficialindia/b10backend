# Axios Configuration Audit

## Base URL
```
process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'
```
✅ Correct. Matches backend mount at `/api/v1/`.

## Request Interceptor
- Reads `access_token` from localStorage
- Sets `Authorization: Bearer {token}`
- SSR-safe: checks `typeof window !== 'undefined'`
✅ No issues.

## Response Interceptor — Token Refresh

### Flow
1. Detect 401 response
2. Skip if request URL includes `/auth/login` or `/auth/refresh`
3. If already refreshing, queue the request
4. Otherwise, attempt refresh via `POST /auth/refresh/` with `{refresh: token}`
5. On success: update `access_token`, retry original request, process queue
6. On failure: clear tokens, reject (AuthGuard handles redirect)

### ✅ Verified Correct
- Uses a dedicated axios instance (not the intercepted one) for the refresh call — prevents infinite loop
- `_retry` flag prevents double-retry
- Queue handles concurrent 401s correctly
- Does NOT redirect on failure (delegates to AuthGuard)

### Potential Edge Case (Not a Bug)
- If `refresh_token` is missing from localStorage (cleared by another tab), the interceptor throws immediately and clears tokens. This is acceptable behavior — AuthGuard will redirect.

## Headers
```
Content-Type: application/json
```
✅ Correct for all API calls.

## Summary
No issues found in Axios configuration.
