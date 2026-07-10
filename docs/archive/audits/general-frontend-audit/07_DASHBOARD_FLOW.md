# 07 — Dashboard Flow Audit

**Date:** 2026-07-08

---

## Dashboard Page: app/(dashboard)/dashboard/page.tsx

### All API Calls Made

| Hook | Endpoint | Method | Query Key | Purpose |
|---|---|---|---|---|
| `useDashboardStats()` | GET `/admin/analytics/` | GET | `['dashboard', 'stats']` | KPI cards (total leads, qualified, converted, rate) |
| `useLeadSummary()` | GET `/admin/dashboard/` | GET | `['dashboard', 'lead-summary']` | Lead status breakdown chart |
| `useFunnel()` | GET `/admin/analytics/funnel/` | GET | `['dashboard', 'funnel']` | Funnel/bar chart |
| `useRecentLeads()` | GET `/admin/leads/?page_size=5&ordering=-created_at` | GET | `['dashboard', 'recent-leads']` | Recent leads table |
| `useAuth()` | GET `/auth/me/` (cached) | GET | `['auth', 'me']` | Username for greeting |

### Execution Order

```
1. AuthGuard checks isLoading → shows FullPageLoader
2. AuthGuard checks isAuthenticated → redirects to /login if false
3. Dashboard page renders
4. All 4 dashboard queries fire SIMULTANEOUSLY (parallel)
5. Each query independently manages its own loading/error state
6. useAuth() likely already resolved (cached from AuthGuard)
```

### Dependency Map

```
DashboardPage
├── useAuth()              → /auth/me/    [Pre-cached by AuthGuard, no extra request]
├── useDashboardStats()    → /admin/analytics/    [Independent]
├── useLeadSummary()       → /admin/dashboard/    [Independent]
├── useFunnel()            → /admin/analytics/funnel/  [Independent]
└── useRecentLeads()       → /admin/leads/?page_size=5  [Independent]
```

No sequential dependencies — all queries run in parallel.

### Failure Points

| Failure | Effect |
|---|---|
| `/admin/analytics/` fails | KPI cards show `<ErrorState>` with retry button |
| `/admin/dashboard/` fails | Lead status chart shows `<ErrorState>` with retry |
| `/admin/analytics/funnel/` fails | Funnel chart shows `<ErrorState>` with retry |
| `/admin/leads/` fails | Recent leads shows `<ErrorState>` with retry |
| All fail simultaneously | All sections show individual error states — page is still usable |

### Expected Response Formats

#### GET /admin/analytics/ → useDashboardStats

```json
{
  "total_chats": 100,
  "total_messages": 500,
  "total_leads": 50,
  "qualified_leads": 30,
  "converted_leads": 10,
  "lost_leads": 5,
  "qualification_rate": 60.0,
  "conversion_rate": 33.33
}
```

Dashboard page accesses: `stats.data.total_leads`, `stats.data.qualified_leads`,
`stats.data.converted_leads`, `stats.data.conversion_rate`

> **⚠️ MISSING FIELDS**: Dashboard page does NOT display `total_chats`, `total_messages`,
> `lost_leads`, `qualification_rate` — these are only shown on the Analytics page.

#### GET /admin/dashboard/ → useLeadSummary

```json
{
  "total_leads": 50,
  "gathering": 5,
  "qualified": 20,
  "converted": 10,
  "lost": 8,
  "escalated": 7
}
```

Dashboard page iterates `Object.entries(leadSummary.data).filter(([key]) => key !== 'total_leads')`.
This correctly excludes `total_leads` and renders each status as a progress bar.

> **⚠️ ASSUMPTION**: Page assumes backend returns EXACTLY these keys. If a new status
> is added to the backend (e.g., `disqualified`), it will appear automatically — which is
> fine. But if ANY key is renamed or the format changes, the entire chart breaks silently
> (shows no bars instead of an error).

#### GET /admin/analytics/funnel/ → useFunnel

```json
[
  {"stage": "Chats Started", "value": 100},
  {"stage": "Leads Captured", "value": 50},
  {"stage": "Leads Qualified", "value": 30},
  {"stage": "Leads Converted", "value": 10}
]
```

Page maps over `funnel.data` array. ✅

#### GET /admin/leads/?page_size=5&ordering=-created_at → useRecentLeads

```json
{
  "count": 50,
  "next": "...",
  "previous": null,
  "results": [
    {
      "id": "uuid",
      "full_name": "...",
      "email": "...",
      "company_name": "...",
      "project_type": "...",
      "status": "gathering",
      "created_at": "..."
    }
  ]
}
```

Page reads `recentLeads.data?.results`. ✅

---

## Charts Rendering Issue

> **⚠️ CRITICAL**: `components/charts/chart-cards.tsx` exports `LineChartCard` and `BarChartCard`
> but these are NOT actual charts — they are simple card wrapper components with title/description slots.
> The actual "charts" on the dashboard are **plain HTML div bars** built inline in the page component
> (percentage-width divs with `bg-primary/70`).
>
> There is **no charting library** (recharts, chart.js, victory, nivo) installed.
> All "charts" are custom-built bar progressions. This is functional but misleading naming.

---

## Quick Actions Navigation Issues

| Button | href | Issue |
|---|---|---|
| "New Lead" | `/leads` | Links to list, not to a creation form — leads come from chatbot |
| "Knowledge" | `/knowledge` | ✅ Correct |
| "Users" | `/users` | ✅ Correct |
| "Settings" | `/settings` | ✅ Correct |
