# Authentication Flow Verification

## Login Flow

### Backend
1. `POST /auth/login/` accepts `{username, password}`
2. Returns `{access, refresh, user: {id, username, email, role}}`
3. Status 200 on success, 401 on invalid credentials

### Frontend
1. `authApi.login()` sends `{username, password}` ✅
2. Stores `response.access` and `response.refresh` in localStorage ✅
3. Invalidates `['auth', 'me']` query ✅
4. Redirects to `/dashboard` ✅
5. On error: displays error message based on status code ✅

### 🟡 Issue: Login Response Type
Frontend `LoginResponse` type is `{access, refresh}` but backend actually returns `{access, refresh, user}`. The `user` field is ignored. This means:
- After login, the frontend must make an additional `/auth/me/` request to get user data
- The user data is available in the login response but thrown away
- Not a bug, but wastes one network request

## Session Restoration

### Flow
1. On app mount, `useAuth` hook checks `localStorage.getItem('access_token')`
2. If token exists, `useQuery` for `/auth/me/` is enabled
3. While loading, `AuthGuard` shows `FullPageLoader`
4. If query succeeds, user is authenticated
5. If query fails (401), tokens are cleared by interceptor, AuthGuard redirects

### 🔴 Critical Issue: /auth/me/ Response Shape
- Backend returns `{id, username, email, first_name, last_name, role, groups: [{id, name}]}`
- Frontend expects `{id, username, email, first_name, last_name, is_active, is_staff, is_superuser, groups: string[]}`
- The `useAuth` hook's `useQuery<User>` will receive an object that doesn't match the `User` type
- React Query won't throw — it will store the raw response
- Components accessing `user.is_active` will get `undefined`
- Components accessing `user.groups` will get `[{id: 1, name: "Admin"}]` not `["Admin"]`

### Impact
- Header component: `user?.first_name` — ✅ works (field exists in both)
- Header initials: uses `user.first_name?.[0]` — ✅ works
- Dashboard greeting: `user?.first_name || user?.username` — ✅ works
- No current component checks `user.is_active` or iterates `user.groups` as strings

**Conclusion: The mismatch exists but currently has no visible runtime impact because no component depends on the mismatched fields. However, it's a latent bug.**

## Logout Flow

### Backend
- `POST /auth/logout/` with `{refresh}` — blacklists the refresh token

### Frontend
1. Calls `authApi.logout(refresh)` with try/catch (ignores errors) ✅
2. Clears `access_token` and `refresh_token` from localStorage ✅
3. Calls `queryClient.clear()` ✅
4. Redirects to `/login` ✅

✅ No issues.

## Refresh Flow

### Backend
- `POST /auth/refresh/` with `{refresh}` returns `{access}` (and possibly new refresh per ROTATE_REFRESH_TOKENS=True)

### Frontend
- Axios interceptor sends `{refresh}` and stores `data.access` ✅
- **Note**: Backend has `ROTATE_REFRESH_TOKENS: True` which means the response also includes a new `refresh` token, but the frontend only stores the new `access` token. This means after a refresh, the old refresh token is blacklisted (BLACKLIST_AFTER_ROTATION=True) and the new one is NOT saved.

### 🔴 Critical Issue: Refresh Token Rotation Not Handled
- Backend settings: `ROTATE_REFRESH_TOKENS: True`, `BLACKLIST_AFTER_ROTATION: True`
- After a successful refresh, the backend returns a NEW refresh token and blacklists the old one
- Frontend interceptor only stores `data.access` — it does NOT store `data.refresh`
- On the next 401, the frontend will try to use the OLD (now blacklisted) refresh token → will fail → user logged out

**Root cause**: Line in axios.ts: `localStorage.setItem('access_token', data.access)` — missing `localStorage.setItem('refresh_token', data.refresh)`

## Route Protection

- `/login` → if authenticated, redirect to `/dashboard` ✅
- `/(dashboard)/*` → if not authenticated, redirect to `/login` ✅
- `AuthGuard` shows loader during session check ✅

✅ No issues.
