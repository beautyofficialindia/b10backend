# React Query Audit

## Query Key Analysis

### Authentication
```
['auth', 'me'] — useAuth hook
```
✅ Stable. Used in one hook only.

### Dashboard
```
['dashboard', 'stats']
['dashboard', 'lead-summary']
['dashboard', 'timeline']
['dashboard', 'funnel']
['dashboard', 'recent-leads']
```
✅ All stable and unique.

### Analytics
```
['analytics', 'stats']
['analytics', 'timeline']
['analytics', 'funnel']
['analytics', 'lead-summary']
```

### 🟠 Duplicate Cache Issue: Dashboard and Analytics share data from the same endpoints but use DIFFERENT query keys
- `['dashboard', 'stats']` and `['analytics', 'stats']` both call `GET /admin/analytics/`
- `['dashboard', 'lead-summary']` and `['analytics', 'lead-summary']` both call `GET /admin/dashboard/`
- `['dashboard', 'funnel']` and `['analytics', 'funnel']` both call `GET /admin/analytics/funnel/`
- This means the same API is called twice when both pages are active, and invalidation in one won't refresh the other
- **Severity**: 🟡 Medium — No data correctness issue, just redundant network requests

### Leads
```
['leads', filters] — useLeads (list)
['leads', id]      — useLeadDetail (detail)
['crm', 'pipeline', search] — usePipelineLeads
```
⚠️ **Query key collision risk**: `['leads', id]` where `id` is a string UUID, and `['leads', filters]` where `filters` is an object. These are distinct, but:
- `useMoveLeadStatus` invalidates `['leads']` and `['crm', 'pipeline']` — correct
- `useUpdateLeadStatus` (from lead detail page) only invalidates `['leads', variables.id]` and `['leads']` — it does NOT invalidate `['crm', 'pipeline']`, so the CRM board won't update after a status change from the lead detail page
- **Severity**: 🟡 Medium

### Knowledge Base
```
['knowledge', filters] — list
['knowledge', id]      — detail
```
✅ No issues.

### Users
```
['users', filters] — list
['users', id]      — detail
['users', id, 'audit', page] — audit log
```
✅ No issues.

### Roles
```
['roles', filters]         — list
['roles', id]              — detail
['roles', 'permissions']   — available permissions
['roles', id, 'users', search] — role users
```
✅ No issues.

### Settings
```
['settings', category]  — per-category
['settings', 'public']  — public
['settings']            — wildcard invalidation
```
✅ No issues.

## staleTime Configuration

| Hook | staleTime | Assessment |
|------|-----------|------------|
| Auth /me/ | 5 min | ✅ Good |
| Dashboard stats | 60s | ✅ Good |
| Analytics | 60-120s | ✅ Good |
| Leads list | 30s | ✅ Good |
| Knowledge list | 30s | ✅ Good |
| Users list | 30s | ✅ Good |
| Roles list | 30s | ✅ Good |
| Settings | 60s | ✅ Good |
| Available permissions | 5 min | ✅ Good |

## Retry Configuration
All queries use `retry: 1` — appropriate for admin APIs.

## keepPreviousData
Used correctly on: leads list, knowledge list, users list, roles list. ✅

## Summary of Issues
1. 🟡 Dashboard/Analytics share endpoints but have separate cache keys (3 duplicate API calls)
2. 🟡 CRM board not invalidated when lead status changes from detail page
