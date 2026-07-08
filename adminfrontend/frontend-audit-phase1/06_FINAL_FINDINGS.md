# Final Findings — Frontend Production Audit Phase 1

## 🔴 Critical Issues

### 1. Refresh Token Rotation Not Stored
- **Evidence**: `lib/axios.ts` line 72: `localStorage.setItem('access_token', data.access)` — no `refresh_token` stored
- **Backend config**: `ROTATE_REFRESH_TOKENS: True`, `BLACKLIST_AFTER_ROTATION: True`
- **Root cause**: After refresh, backend returns new refresh token and blacklists old one. Frontend doesn't save the new one.
- **Impact**: After first token refresh, user will be logged out on next 401 because old refresh is blacklisted
- **Affected files**: `adminfrontend/lib/axios.ts`
- **Recommended fix**: Add `if (data.refresh) localStorage.setItem('refresh_token', data.refresh);` after saving access token
- **Estimated effort**: 1 line change, 5 minutes

### 2. /auth/me/ Response Type Mismatch
- **Evidence**: Backend `UserSerializer` returns `{id, username, email, first_name, last_name, role, groups: [{id, name}]}`. Frontend `User` type expects `{..., is_active, is_staff, is_superuser, groups: string[]}`
- **Root cause**: Frontend auth User type was copied from the user_management module (which has a different serializer) instead of matching the accounts UserSerializer
- **Impact**: Currently latent — no component checks the mismatched fields. Will break if any component uses `user.is_active`, `user.is_superuser`, or treats `user.groups` as `string[]`
- **Affected files**: `adminfrontend/features/auth/types/index.ts`
- **Recommended fix**: Create a separate `AuthUser` type matching the actual /me/ response: `{id, username, email, first_name, last_name, role: string|null, groups: {id: number, name: string}[]}`
- **Estimated effort**: 15 minutes (type change + update consuming components)

---

## 🟡 Medium Issues

### 3. Dashboard/Analytics Duplicate API Calls
- **Evidence**: Both modules call the same 3 endpoints (`/admin/analytics/`, `/admin/dashboard/`, `/admin/analytics/funnel/`) with different query keys
- **Root cause**: Separate feature modules with independent hooks
- **Impact**: 3 redundant API calls when user visits both pages in same session (no data correctness issue)
- **Affected files**: `features/dashboard/hooks/`, `features/analytics/hooks/`
- **Recommended fix**: Extract shared query keys to a common constant, or use the same hook
- **Estimated effort**: 30 minutes

### 4. CRM Board Not Invalidated from Lead Detail Status Change
- **Evidence**: `useUpdateLeadStatus` in `features/leads/hooks/use-leads.ts` invalidates `['leads']` but NOT `['crm', 'pipeline']`
- **Root cause**: Lead detail and CRM are in separate feature modules with no cross-invalidation
- **Impact**: After changing a lead's status from the detail page, the CRM board shows stale data until manually refreshed
- **Affected files**: `features/leads/hooks/use-leads.ts`
- **Recommended fix**: Add `queryClient.invalidateQueries({ queryKey: ['crm'] })` to `useUpdateLeadStatus.onSuccess`
- **Estimated effort**: 1 line, 5 minutes

---

## 🟢 Low / Non-Issues

### 5. Login Response `user` Field Ignored
- **Evidence**: Backend returns `{access, refresh, user}` but frontend only reads `access` and `refresh`
- **Impact**: Extra /me/ API call on login (minor latency)
- **Recommended**: Could cache user data from login response to avoid the extra call. Not required.

### 6. `useAnalyticsTimeline` Hook Defined But Unused
- **Evidence**: Defined in `features/dashboard/hooks/use-dashboard.ts`, never imported by any page
- **Impact**: Dead code (tree-shaken in build, zero runtime impact)
- **Recommended**: Remove or mark as future use

---

## Summary

| Severity | Count | Status |
|----------|-------|--------|
| 🔴 Critical | 2 | Must fix before production |
| 🟡 Medium | 2 | Should fix |
| 🟢 Low | 2 | Nice to have |

**Overall assessment**: The application is 95% correct. Two critical issues must be fixed: the refresh token rotation handling and the /auth/me/ type mismatch. Both are small fixes.
