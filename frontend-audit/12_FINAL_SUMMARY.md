# 12 — Final Summary: Frontend Integration Issues

**Date:** 2026-07-08

---

## Executive Summary

This audit covers the `adminfrontend` Next.js 16 App Router project integrated with a
Django REST Framework backend. The backend is confirmed working.

**Overall Health:** ⚠️ Functional but with several integration bugs, invalid HTML patterns,
and architectural duplication that will cause intermittent issues in production.

---

## Critical Issues (Must Fix)

### 1. API Response Format Inconsistency

**Severity:** 🔴 CRITICAL  
**Files:** `features/users/hooks/use-users.ts`, `features/knowledge/hooks/use-knowledge.ts`, `features/leads/hooks/use-leads.ts`

The backend uses TWO different response envelope formats:
- **Custom wrapper**: `{ success: true, data: {...}, meta: {...} }` — used by Users, Knowledge, Roles, Settings
- **DRF standard**: `{ count, next, previous, results: [...] }` — used by Leads list

The frontend code correctly handles BOTH, but this inconsistency is fragile:
- If any backend endpoint switches format (e.g., leads moves to custom wrapper),
  the frontend silently breaks and renders blank/error states.
- `useRecentLeads` in dashboard reads `data?.results` (DRF format)
- Users pages read `data?.data` (custom wrapper)
- Any regression in this area will cause data to silently not render

**What to verify:**  
Run each endpoint manually and confirm:
- `GET /api/v1/admin/leads/` → must return `{ count, results: [...] }`
- `GET /api/v1/admin/users/` → must return `{ success, data: [...], meta: {...} }`
- `GET /api/v1/admin/analytics/` → must return FLAT object (no wrapper)
- `GET /api/v1/admin/dashboard/` → must return FLAT object (no wrapper)

---

### 2. Token Refresh Endpoint Response Key Mismatch Risk

**Severity:** 🔴 CRITICAL  
**File:** `lib/axios.ts` (lines 56-63)

```ts
const { data } = await axios.post(refreshUrl, { refresh: refreshToken });
localStorage.setItem('access_token', data.access);
```

If the backend `RefreshAPIView` response is `{ access: "..." }` → ✅  
If the backend returns `{ access_token: "..." }` or `{ token: "..." }` → ❌ User is silently logged out on next 401.

**What to verify:**  
`POST /api/v1/auth/refresh/` with `{ "refresh": "..." }` → confirm response contains `{ "access": "..." }` key.

---

### 3. Button-in-Button Invalid HTML

**Severity:** 🔴 HIGH  
**Files:** `components/layout/header.tsx`, `components/layout/mobile-sidebar.tsx`

`@base-ui/react` `DropdownMenu.Trigger` and `Dialog.Trigger` render as `<button>` elements.
Wrapping a `<Button>` component (which renders another `<button>`) inside creates:
```html
<button> <!-- DropdownMenuTrigger -->
  <button> <!-- Button component -->
    Icon
  </button>
</button>
```
This is **invalid HTML** per the HTML5 spec and causes:
- `Warning: validateDOMNesting` in React dev console
- Unpredictable click event behavior in some browsers
- Accessibility failures

---

### 4. Redirect Loop: Unauthenticated Root Visit

**Severity:** 🔴 HIGH  
**File:** `app/page.tsx`

```ts
// Server-side redirect — fires BEFORE AuthGuard
redirect('/dashboard')
```

When an unauthenticated user visits `/`:
1. Server redirects → `/dashboard`
2. AuthGuard detects no token → redirects → `/login`

This is 2 unnecessary redirects. More importantly, if `redirect('/dashboard')` is a permanent
redirect and the browser caches it, the user can get stuck.

**Fix approach:** `app/page.tsx` should redirect directly to `/login` or defer routing to client-side AuthGuard.

---

### 5. Dashboard and Analytics Duplicate API Requests

**Severity:** 🔴 HIGH  
**Files:** `features/dashboard/api/index.ts`, `features/analytics/api/index.ts`

Both features call **identical backend endpoints** with **different React Query cache keys**.
This results in:
- 2x requests to `/admin/analytics/`, `/admin/analytics/timeline/`, `/admin/analytics/funnel/`, `/admin/dashboard/`
- No cache sharing between dashboard and analytics pages
- Double backend load when both pages are visited in a session

---

### 6. Button Inside `<a>` Tag

**Severity:** 🔴 HIGH  
**File:** `app/(dashboard)/leads/[id]/page.tsx` (lines 292-303)

```tsx
<a href={`mailto:${lead.email}`} className="block">
  <Button variant="outline" size="sm" ...>Send Email</Button>
</a>
```

`<button>` inside `<a>` is invalid HTML. Use `<button onClick>` with `window.location.href = 'mailto:...'` instead.

---

## High Issues

### 7. Hydration Mismatch — Inline Style Tag

**File:** `components/layout/app-shell.tsx`  
Inline `<style>` inside a client component creates a server/client DOM mismatch.

### 8. CRM Pipeline Hard Limit

**File:** `features/crm/hooks/use-pipeline.ts`  
`page_size: 100` — pipeline silently shows at most 100 leads. No user warning.

### 9. CRM Optimistic Rollback Broken for Search

**File:** `features/crm/hooks/use-pipeline.ts`  
```ts
queryClient.getQueryData<Lead[]>(['crm', 'pipeline', undefined])
```
Only reads the unfiltered cache. If search is active, rollback fails silently.

---

## Medium Issues

### 10. Non-Functional UI Elements

| Element | Location | Impact |
|---|---|---|
| Search input in header | `header.tsx` | Shows input, does nothing |
| Notifications bell | `header.tsx` | Always shows red dot, no backend data |
| "Export" button on Analytics | `analytics/page.tsx` | Disabled, tooltip says "coming soon" |
| "Activity" and "Notes" tabs on Lead detail | `leads/[id]/page.tsx` | "Coming soon" placeholders |

### 11. React Compiler Memoization Warning

**File:** `users/new/page.tsx`  
React Hook Form's `watch()` function prevents React Compiler from memoizing the component.
Warning: `Compilation Skipped: Use of incompatible library` (already in lint output).

### 12. Missing Pages (Unverified Routes)

| Route | Navigation Source |
|---|---|
| `/users/[id]/edit` | User detail "Edit" button |
| `/roles/new` | Roles list "New Role" button |
| `/roles/[id]/edit` | Role detail (likely) |
| `/knowledge/[id]/edit` | Knowledge detail (likely) |

If these `page.tsx` files are missing, navigation to these routes will show a Next.js 404.

---

## Low Issues

### 13. `usePublicSettings` Hook Unused

Exported from `features/settings` but never consumed in any page.

### 14. `services/` and `store/` Directories Empty

Both contain only `.gitkeep`. Can be removed or documented.

### 15. Duplicate `useLeadSummary` Export Name

`features/dashboard` and `features/analytics` both export a `useLeadSummary` hook.
Consuming code that imports from both would need aliasing.

### 16. `icon-size h-4.5 w-4.5`

Non-standard Tailwind value in sidebar. Valid with Tailwind v4 but should be confirmed.

### 17. No 404 Page, No Error Boundary

No `app/not-found.tsx` or `app/error.tsx`. Default Next.js pages are shown.

---

## What Is Working Correctly

| Feature | Status |
|---|---|
| Login / Logout / Token refresh | ✅ Functional |
| AuthGuard route protection | ✅ Functional |
| All 8 sidebar navigation links | ✅ Functional |
| Lead list + filtering + pagination | ✅ Functional |
| Lead detail + status change | ✅ Functional |
| CRM kanban (drag and drop) | ✅ Functional |
| Users CRUD + activate/deactivate | ✅ Functional |
| Knowledge Base CRUD + publish/archive | ✅ Functional |
| Roles CRUD + permissions management | ✅ Functional |
| Settings per-category management | ✅ Functional |
| Analytics stats + funnel + timeline | ✅ Functional |
| Dark/light mode | ✅ Functional |
| Responsive layout | ✅ Functional |
| Debounced search on all list pages | ✅ Functional |
| Optimistic status updates in CRM | ✅ Functional (with caveats) |
| Skeleton loading states everywhere | ✅ Functional |
| Per-section error states with retry | ✅ Functional |

---

## Recommended Immediate Fixes (Ordered by Priority)

| # | Fix | File | Time Est. |
|---|---|---|---|
| 1 | Verify `/auth/refresh/` response returns `data.access` key | Backend | 5 min |
| 2 | Verify all endpoint response formats are consistent with frontend types | Backend + Postman | 30 min |
| 3 | Fix button-in-button in header and mobile-sidebar | header.tsx, mobile-sidebar.tsx | 20 min |
| 4 | Fix `<a><Button>` in lead detail | leads/[id]/page.tsx | 5 min |
| 5 | Remove or externalize inline `<style>` in AppShell | app-shell.tsx | 15 min |
| 6 | Merge dashboard and analytics API modules to share cache | features/ | 30 min |
| 7 | Fix `app/page.tsx` redirect logic | app/page.tsx | 5 min |
| 8 | Add CRM pipeline lead count warning | crm/page.tsx | 10 min |
| 9 | Create missing edit/new pages or remove broken navigation | Various | 1-2 hours |
| 10 | Add `app/not-found.tsx` and `app/error.tsx` | app/ | 15 min |
