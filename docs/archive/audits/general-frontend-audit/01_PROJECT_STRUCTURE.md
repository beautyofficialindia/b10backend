# 01 — Project Structure Audit

**Framework:** Next.js 16.2.10 (App Router)
**Language:** TypeScript 5.x
**Runtime:** React 19.2.4
**Date:** 2026-07-08

---

## App Directory Structure

```
adminfrontend/
├── app/
│   ├── layout.tsx                      # Root layout (providers)
│   ├── page.tsx                        # Redirects / → /dashboard (server-side)
│   ├── globals.css
│   ├── login/
│   │   └── page.tsx
│   ├── showcase/
│   └── (dashboard)/                   # Route group — protected by AuthGuard
│       ├── layout.tsx                  # <AuthGuard><AppShell>
│       ├── dashboard/page.tsx
│       ├── users/
│       │   ├── page.tsx
│       │   ├── new/page.tsx
│       │   └── [id]/
│       │       ├── page.tsx
│       │       └── edit/              # ⚠️ Unverified — directory exists, no page.tsx confirmed
│       ├── leads/
│       │   ├── page.tsx
│       │   └── [id]/page.tsx
│       ├── crm/page.tsx
│       ├── analytics/page.tsx
│       ├── knowledge/
│       │   ├── page.tsx
│       │   ├── new/page.tsx
│       │   └── [id]/
│       │       ├── page.tsx
│       │       └── edit/              # ⚠️ Unverified
│       ├── roles/
│       │   ├── page.tsx
│       │   ├── new/                   # ⚠️ Unverified
│       │   └── [id]/
│       │       ├── page.tsx
│       │       └── edit/             # ⚠️ Unverified
│       └── settings/page.tsx
```

---

## Features Folder Structure

| Feature | api | hooks | components | types | utils |
|---|---|---|---|---|---|
| auth | ✅ | ✅ | ✅ (auth-guard, login-form) | ✅ | ✅ (schemas) |
| dashboard | ✅ | ✅ | ✅ (activity-timeline) | ✅ | — |
| users | ✅ | ✅ | — | ✅ | — |
| leads | ✅ | ✅ | — | ✅ | ✅ |
| crm | — | ✅ (uses leadsApi) | ✅ (pipeline-card, pipeline-column) | ✅ | — |
| analytics | ✅ | ✅ | — | ✅ | — |
| knowledge | ✅ | ✅ | — | ✅ | — |
| roles | ✅ | ✅ | — | ✅ | — |
| settings | ✅ | ✅ | — | ✅ | — |

---

## Components Structure

```
components/
├── layout/     app-shell, header, sidebar, mobile-sidebar, page-container, page-header, theme-toggle
├── ui/         button, dialog, dropdown-menu, sheet, tooltip, card, badge, input, avatar,
│               tabs, select, checkbox, switch, textarea, table, skeleton, scroll-area,
│               separator, breadcrumb, alert (all backed by @base-ui/react)
├── common/     alerts, badges, cards, copy-button, dialogs, empty-state, error-state,
│               loading-screen, skeletons
├── charts/     chart-cards.tsx (LineChartCard, BarChartCard — NO actual chart library!)
├── tables/     data-table, table-pagination, table-toolbar
└── forms/      form-fields (TextField, PasswordField, TextAreaField, CheckboxField, etc.)
```

---

## Providers

| Provider | File | Purpose |
|---|---|---|
| ThemeProvider | providers/theme-provider.tsx | next-themes dark/light mode |
| QueryProvider | providers/query-provider.tsx | React Query with global defaults |
| TooltipProvider | components/ui/tooltip.tsx | @base-ui Tooltip context |

Provider nesting (root layout):
`ThemeProvider → QueryProvider → TooltipProvider → {children}`

---

## Hooks (Global)

| File | Hook |
|---|---|
| hooks/use-debounce.ts | `useDebounce` |

All other hooks live inside feature folders.

---

## Services

> **⚠️ EMPTY**: `services/` directory exists at root but contains only `.gitkeep`.
> All API calls are implemented directly inside `features/*/api/index.ts`.

---

## API Layer

Single Axios instance: `lib/axios.ts`
- Base URL: `NEXT_PUBLIC_API_URL || http://localhost:8000/api/v1`
- Auth: Bearer token from `localStorage.access_token`
- Token refresh: interceptor-based (failedQueue pattern)

---

## Route Structure Summary

| Route | Protected | Dynamic Param |
|---|---|---|
| `/` | No | — |
| `/login` | No | — |
| `/dashboard` | Yes | — |
| `/users` | Yes | — |
| `/users/new` | Yes | — |
| `/users/[id]` | Yes | id (number) |
| `/leads` | Yes | — |
| `/leads/[id]` | Yes | id (UUID string) |
| `/crm` | Yes | — |
| `/analytics` | Yes | — |
| `/knowledge` | Yes | — |
| `/knowledge/new` | Yes | — |
| `/knowledge/[id]` | Yes | id (UUID string) |
| `/roles` | Yes | — |
| `/roles/[id]` | Yes | id (number) |
| `/settings` | Yes | — |

---

## Missing Routes / Issues

| Issue | Severity |
|---|---|
| No `app/not-found.tsx` | Medium |
| No `app/error.tsx` boundary | High |
| `app/page.tsx` server-redirects to `/dashboard` before AuthGuard runs — causes redirect loop when unauthenticated | High |
| `/users/[id]/edit`, `/roles/new`, `/roles/[id]/edit`, `/knowledge/[id]/edit` — directories exist, pages unverified | High |
| `dashboard/mock/` directory is empty | Low |
| `store/` directory contains only `.gitkeep` — no state management beyond React Query | Low |
