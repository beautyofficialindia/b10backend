# 06 — Data Fetching Audit (React Query Hooks)

**Date:** 2026-07-08

---

## Global Query Client Defaults

| Setting | Value |
|---|---|
| `staleTime` | 60,000ms (1 minute) |
| `retry` | 1 |
| `refetchOnWindowFocus` | `false` |

---

## Auth Queries

### useAuth() — features/auth/hooks/use-auth.ts

| Property | Value |
|---|---|
| Query Key | `['auth', 'me']` |
| Endpoint | GET `/auth/me/` |
| `enabled` | `hasAccessToken()` — only runs if `localStorage.access_token` exists |
| `staleTime` | 5 minutes |
| `retry` | `false` |
| Cache time | Default (5 min inactive) |
| Error handling | `isError` → `isAuthenticated = false` |
| Loading state | `isLoading && hasAccessToken()` — custom `effectiveLoading` |
| **Potential Bug** | `enabled: hasAccessToken()` is evaluated **at hook call time** (render). On first render after login, token may not yet be in localStorage if stored asynchronously. |
| **Potential Bug** | `isFetched` is returned but not used for auth guard logic — `AuthGuard` only checks `isLoading + isAuthenticated`. If `isFetched=false` and `isLoading=false` and `isAuthenticated=false` (no token), the guard redirects immediately, which is correct. ✅ |

### loginMutation — features/auth/hooks/use-auth.ts

| Property | Value |
|---|---|
| Mutation Fn | POST `/auth/login/` |
| On Success | Store tokens → `invalidateQueries(['auth', 'me'])` → `router.push('/dashboard')` |
| Error Handling | `loginError` exposed via hook |
| **Potential Bug** | `invalidateQueries` fires BEFORE router navigation. Query refetch is async. There may be a brief moment where `isAuthenticated = false` after login. |

---

## Dashboard Queries

### useDashboardStats() — features/dashboard/hooks/use-dashboard.ts

| Property | Value |
|---|---|
| Query Key | `['dashboard', 'stats']` |
| Endpoint | GET `/admin/analytics/` |
| `staleTime` | 60,000ms |
| `retry` | 1 |
| Error handling | `isError` in page → `<ErrorState>` |
| Loading state | `isLoading` → `<SkeletonCard>` |
| **Issue** | Same endpoint also called by `useAnalyticsStats()` under key `['analytics', 'stats']` — **2 separate cache entries, 2 separate requests** |

### useLeadSummary() (dashboard) — features/dashboard/hooks/use-dashboard.ts

| Property | Value |
|---|---|
| Query Key | `['dashboard', 'lead-summary']` |
| Endpoint | GET `/admin/dashboard/` |
| `staleTime` | 60,000ms |
| **Issue** | Same endpoint also called by analytics `useLeadSummary()` under key `['analytics', 'lead-summary']` — duplicate requests |

### useAnalyticsTimeline() (dashboard) — features/dashboard/hooks/use-dashboard.ts

| Property | Value |
|---|---|
| Query Key | `['dashboard', 'timeline']` |
| Endpoint | GET `/admin/analytics/timeline/` |
| `staleTime` | 120,000ms |
| **Issue** | Duplicated in analytics feature under key `['analytics', 'timeline']` |

### useFunnel() — features/dashboard/hooks/use-dashboard.ts

| Property | Value |
|---|---|
| Query Key | `['dashboard', 'funnel']` |
| Endpoint | GET `/admin/analytics/funnel/` |
| `staleTime` | 120,000ms |
| **Issue** | Duplicated in analytics feature under key `['analytics', 'funnel']` |

### useRecentLeads() — features/dashboard/hooks/use-dashboard.ts

| Property | Value |
|---|---|
| Query Key | `['dashboard', 'recent-leads']` |
| Endpoint | GET `/admin/leads/?page_size=5&ordering=-created_at` |
| `staleTime` | 30,000ms |
| Error handling | `isError` → `<ErrorState>` alongside table |
| **Potential Bug** | Uses `data?.results` but the TypeScript return type is `{ results: Lead[] }` — if backend returns standard DRF pagination, this is `{ count, next, previous, results }` and `results` should be safe. However the hook returns `Promise<{ results: Lead[] }>` — discards `count`. |

---

## Users Queries

### useUsersList(filters) — features/users/hooks/use-users.ts

| Property | Value |
|---|---|
| Query Key | `['users', filters]` (full filters object) |
| Endpoint | GET `/admin/users/?{params}` |
| `staleTime` | 30,000ms |
| `placeholderData` | `keepPreviousData` |
| `retry` | 1 |
| **Potential Bug** | `filters` object used as query key — new object reference on each render causes unnecessary refetches unless memoized. Page DOES memoize via `useMemo`. ✅ |

### useUserDetail(id) — features/users/hooks/use-users.ts

| Property | Value |
|---|---|
| Query Key | `['users', id]` |
| Endpoint | GET `/admin/users/{id}/` |
| `enabled` | `!!id` |
| **Type Issue** | `usersApi.getById` returns `res.data` (raw axios data), typed as `{ data: UserDetail }`. The page reads `data?.data.username`. This assumes backend wraps in `{ success, data, meta }`. If response is not wrapped, this breaks. |

---

## Leads Queries

### useLeads(filters) — features/leads/hooks/use-leads.ts

| Property | Value |
|---|---|
| Query Key | `['leads', filters]` |
| Endpoint | GET `/admin/leads/?{params}` |
| `staleTime` | 30,000ms |
| `placeholderData` | `keepPreviousData` |
| **Response Format** | `LeadListResponse = { count, next, previous, results }` — standard DRF. Page reads `data.count` and `data.results` directly ✅ |
| **Different from users** | Leads uses raw DRF pagination; Users uses custom `success_response` envelope |

### useLeadDetail(id) — features/leads/hooks/use-leads.ts

| Property | Value |
|---|---|
| Query Key | `['leads', id]` |
| Endpoint | GET `/admin/leads/{id}/` |
| **Response Format** | Returns `LeadDetail` directly (no envelope wrapper) — backend `LeadDetailSerializer` returns flat |

---

## CRM Queries

### usePipelineLeads(search?) — features/crm/hooks/use-pipeline.ts

| Property | Value |
|---|---|
| Query Key | `['crm', 'pipeline', search]` |
| Endpoint | GET `/admin/leads/?page_size=100` (reuses leadsApi) |
| `staleTime` | 30,000ms |
| `retry` | 1 |
| **Potential Bug** | `page_size: 100` — hard limit. If there are more than 100 leads, pipeline will be incomplete with no user warning. |
| **Potential Bug** | `res.results` accessed directly — but `leadsApi.list` returns `LeadListResponse = { count, next, previous, results }`. So `res.results` ✅ |

### useMoveLeadStatus() — features/crm/hooks/use-pipeline.ts

| Property | Value |
|---|---|
| Optimistic Update | ✅ Implemented with rollback |
| On Settled | Invalidates `['crm', 'pipeline']` AND `['leads']` |
| **Potential Bug** | Optimistic update reads `queryClient.getQueryData<Lead[]>(['crm', 'pipeline', undefined])` — only works when search is `undefined`. If user has searched, rollback will fail silently. |

---

## Analytics Queries

> **⚠️ ALL FOUR analytics hooks call identical endpoints as dashboard hooks but with different cache keys.**
> This results in duplicate HTTP requests when both `/dashboard` and `/analytics` pages are visited in the same session.

| Hook | Key | Endpoint | Duplicates Dashboard Key |
|---|---|---|---|
| `useAnalyticsStats` | `['analytics', 'stats']` | GET `/admin/analytics/` | `['dashboard', 'stats']` |
| `useAnalyticsTimeline` | `['analytics', 'timeline']` | GET `/admin/analytics/timeline/` | `['dashboard', 'timeline']` |
| `useAnalyticsFunnel` | `['analytics', 'funnel']` | GET `/admin/analytics/funnel/` | `['dashboard', 'funnel']` |
| `useLeadSummary` | `['analytics', 'lead-summary']` | GET `/admin/dashboard/` | `['dashboard', 'lead-summary']` |

---

## Knowledge Queries

### useKnowledgeList(filters) — features/knowledge/hooks/use-knowledge.ts

| Property | Value |
|---|---|
| Query Key | `['knowledge', filters]` |
| Endpoint | GET `/admin/kb/entries/?{params}` |
| Response | `KBListResponse = { success, data: KnowledgeEntry[], meta: { pagination } }` |
| **Usage** | Page reads `data?.data` and `data?.meta?.pagination` ✅ |

### useKnowledgeDetail(id)

| Property | Value |
|---|---|
| Query Key | `['knowledge', id]` |
| Return Type | `{ data: KnowledgeEntryDetail }` |
| **Potential Bug** | `knowledgeApi.getById` returns `res.data` typed as `{ data: KnowledgeEntryDetail }` — assumes backend wraps response |

---

## Settings Queries

### useSettingsCategory(category) — features/settings/hooks/use-settings.ts

| Property | Value |
|---|---|
| Query Key | `['settings', category]` |
| Endpoint | GET `/admin/settings/{category}/` |
| `staleTime` | 60,000ms |
| **Note** | Each tab mount triggers a separate query. With 8 categories, switching tabs fires 8 requests. `staleTime` prevents re-fetching. |
| Response | `{ data: Setting[] }` — page reads `data?.data` ✅ |

---

## Summary of Data Fetching Issues

| Severity | Issue |
|---|---|
| 🔴 HIGH | Dashboard and Analytics features call identical endpoints with different cache keys — 2x requests |
| 🔴 HIGH | `useUserDetail` response typing assumes `{ data: UserDetail }` wrapper — breaks if backend returns flat |
| 🟡 MEDIUM | CRM pipeline hard limit: 100 leads max, no pagination, no warning |
| 🟡 MEDIUM | CRM optimistic rollback only works when `search` is `undefined` |
| 🟡 MEDIUM | `useAuth` `enabled` depends on localStorage at render time — potential SSR race |
| 🟢 LOW | Login mutation invalidates query then navigates — brief unauthenticated flash possible |
| 🟢 LOW | Settings: 8 separate requests on settings page (one per category tab) |
