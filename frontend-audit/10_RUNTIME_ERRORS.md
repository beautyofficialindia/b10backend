# 10 — Runtime Errors Audit

**Date:** 2026-07-08

---

> **NOTE**: This report is based on static code analysis. A live browser session was not
> available for capturing real-time console output. All items are predicted from the code.

---

## Hydration Warnings

### 1. Inline `<style>` in AppShell (HIGH)

**File:** `components/layout/app-shell.tsx` (lines 23-28)

```tsx
<style>{`
  @media (min-width: 1024px) {
    [data-collapsed="true"] { margin-left: 64px !important; }
    [data-collapsed="false"] { margin-left: 256px !important; }
  }
`}</style>
```

**Issue:** Inline `<style>` tags injected inside a `'use client'` component are rendered
after SSR. The server renders without this style. React will warn about a hydration mismatch
because the DOM differs between server and client.

**Expected Console Warning:**
```
Warning: Prop `style` did not match. Server: "" Client: "..."
```
or
```
Hydration failed because the server rendered HTML didn't match the client.
```

---

### 2. localStorage Access Pattern (MEDIUM)

**File:** `features/auth/hooks/use-auth.ts` (line 34)

```ts
enabled: hasAccessToken(),
```

`hasAccessToken()` checks `typeof window !== 'undefined'`. On the server, it returns `false`.
On the client, it may return `true`. This causes a React Query `enabled` state difference
between SSR and first client render.

**Expected Behavior:** Since all dashboard pages are `'use client'`, SSR doesn't run them.
This is safe in this codebase but could cause issues if any component is server-rendered.

---

### 3. `suppressHydrationWarning` on `<html>` (Low)

**File:** `app/layout.tsx` (line 29)

```tsx
<html lang="en" suppressHydrationWarning ...>
```

This suppresses hydration warnings on the `<html>` element — used for `next-themes` to
set `class="dark"` without causing hydration mismatch. This is the correct pattern. ✅

---

## Console Warnings (Predicted)

### 1. Button-in-Button Warning

**Files:** `header.tsx`, `mobile-sidebar.tsx`

When `@base-ui/react/menu` `Trigger` component renders as `<button>` and wraps another
`<Button>` (also a `<button>`), React will log:

```
Warning: validateDOMNesting(...): <button> cannot appear as a descendant of <button>.
```

This is a known React DOM validation warning.

### 2. React Compiler Warning (from lint)

**File:** `users/new/page.tsx`

The React Compiler skips memoizing `NewUserPage`. This may produce a development-mode
console note, but not a warning visible in the browser console.

### 3. `aria-label` Missing on Icon Buttons

Multiple places use icon-only buttons without `aria-label`. While `<span className="sr-only">` is used in some places, others may be missing it:

- Notifications bell: `<span className="sr-only">Notifications</span>` ✅ Present
- Theme toggle: Verify
- Table row action buttons: Most use `Eye` icon without accessible labels

---

## 404 Predictions

| URL | Condition | Result |
|---|---|---|
| `/users/[non-numeric-id]` | `Number('abc') = NaN` → API GET `/admin/users/NaN/` | Backend 404 → `<ErrorState>` |
| `/leads/[invalid-uuid]` | API GET `/admin/leads/invalid/` | Backend 400/404 → `<ErrorState>` |
| `/knowledge/[bad-id]` | API GET `/admin/kb/entries/bad/` | Backend 404 → `<ErrorState>` |
| `/roles/999` | Non-existent role | Backend 404 → `<ErrorState>` |
| Any unlisted path | Next.js | Default Next.js 404 page (no custom not-found.tsx) |

---

## Failed API Requests (Predicted)

### 1. Analytics Duplicate Requests

When navigating Dashboard → Analytics in same session, all 4 analytics endpoints are called
twice (once per feature's cache key). This results in:
- 8 total API calls for what should be 4
- Double backend load
- No user-visible error, just wasted requests

### 2. Settings: Missing Category Endpoint

Settings page calls `GET /admin/settings/{category}/` for each tab visited.
If the backend settings don't have data for a category (e.g., `INTEGRATIONS`), it returns
an empty array `{ data: [] }` → page shows "No settings in this category." Graceful. ✅

### 3. CRM Pipeline: >100 Leads

If the backend has >100 leads, `page_size=100` truncates the pipeline silently.
The user sees an incomplete kanban board with no warning.

---

## Network Issues

### CORS

If the backend is not running at `http://localhost:8000`, ALL API calls fail with:
```
Access to XMLHttpRequest blocked by CORS policy
```
or simply `Network Error` from Axios. The interceptor passes these through to the UI
which shows `<ErrorState>`.

### Missing CSRF Protection

The frontend sends `Authorization: Bearer` tokens. No CSRF tokens are used.
This is appropriate for JWT-based auth — CSRF only applies to cookie-based sessions.

---

## Component Stack Traces (Predicted)

### TypeError: Cannot read properties of undefined (reading 'data')

**Likely Location:** `users/[id]/page.tsx`

```ts
const user = data?.data;
```

If `usersApi.getById` returns a flat object instead of `{ data: UserDetail }`, `data?.data`
is `undefined` and the component renders `isError` state instead.

The conditional `if (isError || !user)` catches this gracefully. ✅

### TypeError: Cannot read properties of null

**Likely Location:** Various places accessing optional user fields.

`user?.first_name?.[0]` — safe chaining used throughout. ✅

---

## Summary of Runtime Issues

| Severity | Issue | File |
|---|---|---|
| 🔴 HIGH | Hydration mismatch from inline `<style>` tag | app-shell.tsx |
| 🔴 HIGH | Button-in-button: `<button> cannot appear as descendant of <button>` | header.tsx, mobile-sidebar.tsx |
| 🟡 MEDIUM | 2x API requests for identical analytics data | dashboard/analytics features |
| 🟡 MEDIUM | CRM pipeline silent truncation at 100 leads | crm/page.tsx |
| 🟡 MEDIUM | Disabled tooltip trigger won't show on hover | analytics/page.tsx |
| 🟢 LOW | Non-existent route pages (edit routes unverified) | Various |
| 🟢 LOW | No custom 404 or error boundary page | app/ root |
