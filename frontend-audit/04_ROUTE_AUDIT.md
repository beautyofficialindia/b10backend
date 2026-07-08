# 04 — Route Audit

**Date:** 2026-07-08

---

## Route Inspection Table

| Route | Component File | Exists? | Navigation? | Sidebar Link? | 404 Handled? | Dynamic? | Broken Imports? |
|---|---|---|---|---|---|---|---|
| `/` | `app/page.tsx` | ✅ | N/A (redirect) | No | N/A | No | No |
| `/login` | `app/login/page.tsx` | ✅ | Via AuthGuard redirect | No | — | No | No |
| `/dashboard` | `app/(dashboard)/dashboard/page.tsx` | ✅ | Via sidebar | ✅ Dashboard | No | No | No |
| `/users` | `app/(dashboard)/users/page.tsx` | ✅ | Via sidebar | ✅ Users | No | No | No |
| `/users/new` | `app/(dashboard)/users/new/page.tsx` | ✅ | Via "New User" button | No | No | No | No |
| `/users/[id]` | `app/(dashboard)/users/[id]/page.tsx` | ✅ | Via row action (Eye icon) | No | ⚠️ Uses ErrorState | Yes | No |
| `/users/[id]/edit` | `app/(dashboard)/users/[id]/edit/` | ⚠️ Unverified | Via "Edit" button on detail page | No | Unknown | Yes | Unknown |
| `/leads` | `app/(dashboard)/leads/page.tsx` | ✅ | Via sidebar | ✅ Leads | No | No | No |
| `/leads/[id]` | `app/(dashboard)/leads/[id]/page.tsx` | ✅ | Via row action (Eye icon) | No | ⚠️ Uses ErrorState | Yes | No |
| `/crm` | `app/(dashboard)/crm/page.tsx` | ✅ | Via sidebar | ✅ CRM | No | No | No |
| `/analytics` | `app/(dashboard)/analytics/page.tsx` | ✅ | Via sidebar | ✅ Analytics | No | No | No |
| `/knowledge` | `app/(dashboard)/knowledge/page.tsx` | ✅ | Via sidebar | ✅ Knowledge Base | No | No | No |
| `/knowledge/new` | `app/(dashboard)/knowledge/new/page.tsx` | ✅ | Via "New Entry" button | No | No | No | No |
| `/knowledge/[id]` | `app/(dashboard)/knowledge/[id]/page.tsx` | ✅ | Via row action (Eye icon) | No | ⚠️ Uses ErrorState | Yes | No |
| `/knowledge/[id]/edit` | `app/(dashboard)/knowledge/[id]/edit/` | ⚠️ Unverified | Possibly from detail page | No | Unknown | Yes | Unknown |
| `/roles` | `app/(dashboard)/roles/page.tsx` | ✅ | Via sidebar | ✅ Roles | No | No | No |
| `/roles/new` | `app/(dashboard)/roles/new/` | ⚠️ Unverified | Via "New Role" button | No | Unknown | No | Unknown |
| `/roles/[id]` | `app/(dashboard)/roles/[id]/page.tsx` | ✅ | Via row action (Eye icon) | No | ⚠️ Uses ErrorState | Yes | No |
| `/roles/[id]/edit` | `app/(dashboard)/roles/[id]/edit/` | ⚠️ Unverified | Possibly from detail page | No | Unknown | Yes | Unknown |
| `/settings` | `app/(dashboard)/settings/page.tsx` | ✅ | Via sidebar | ✅ Settings | No | No | No |
| `/showcase` | `app/showcase/` | ⚠️ Unverified | No nav link | No | N/A | No | Unknown |

---

## Sidebar Navigation vs Route Coverage

The sidebar (`constants/navigation.ts`) defines these links:

| Sidebar Title | href | App Route Exists? |
|---|---|---|
| Dashboard | `/dashboard` | ✅ |
| Leads | `/leads` | ✅ |
| CRM | `/crm` | ✅ |
| Analytics | `/analytics` | ✅ |
| Knowledge Base | `/knowledge` | ✅ |
| Users | `/users` | ✅ |
| Roles | `/roles` | ✅ |
| Settings | `/settings` | ✅ |

All 8 sidebar links have corresponding app routes. ✅

---

## Routes Navigated To But Not In Sidebar

| Route | Navigated From |
|---|---|
| `/login` | AuthGuard redirect |
| `/users/new` | Users list "New User" button |
| `/users/[id]` | Users table row |
| `/users/[id]/edit` | User detail "Edit" button |
| `/leads/[id]` | Leads table row |
| `/knowledge/new` | Knowledge list button |
| `/knowledge/[id]` | Knowledge table row |
| `/knowledge/[id]/edit` | Possibly knowledge detail |
| `/roles/new` | Roles list "New Role" button |
| `/roles/[id]` | Roles table row |
| `/roles/[id]/edit` | Possibly roles detail |

---

## Active-State Detection

The sidebar uses `pathname.startsWith(item.href)` for active detection. This means:
- `/dashboard` will match `/dashboard` ✅
- `/leads` will match `/leads/123` (detail pages correctly highlight parent) ✅
- `/users` will match `/users/new` ✅
- **⚠️ RISK**: `/users` also matches `/users/new` — both highlight "Users" in sidebar ✅ (acceptable)

---

## Potential 404 Scenarios

| Scenario | Behavior |
|---|---|
| Navigate to `/users/99999` (non-existent ID) | `useUserDetail` returns isError → renders `<ErrorState>` (not a real 404) |
| Navigate to `/leads/non-uuid` | API call will fail with 404 → `<ErrorState>` |
| Navigate to `/roles/new` if unimplemented | Next.js default 404 or blank page |
| Direct URL to undefined route | Next.js default 404 (no custom not-found.tsx) |

---

## Dashboard Quick Actions — URL Mismatches

In `app/(dashboard)/dashboard/page.tsx` (lines 172-176):
```tsx
{ label: 'New Lead', icon: Plus, href: '/leads' }
```
> **⚠️ BUG**: "New Lead" quick action links to `/leads` (the list), NOT `/leads/new`.
> There is no `/leads/new` route — leads are captured by the chatbot, so this is potentially correct behavior.
> However, this is misleading UX.
