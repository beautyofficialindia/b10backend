# 09 — Build Report

**Date:** 2026-07-08

---

## Lint Results

**Command:** `npm run lint` (which runs `eslint`)

### Output

```
C:\workflow\b10backend\adminfrontend\app\(dashboard)\users\new\page.tsx
  68:88  warning  Compilation Skipped: Use of incompatible library

This API returns functions which cannot be memoized without leading to stale UI.
To prevent this, by default React Compiler will skip memoizing this component/hook.
However, you may see issues if values from this API are passed to other components/hooks
that are memoized.

C:\workflow\b10backend\adminfrontend\app\(dashboard)\users\new\page.tsx:68:88
> 68 |  <CheckboxField ... checked={watch('is_staff')} onCheckedChange={(v) => setValue('is_staff', v)} />
     |                                                                          ^^^^^ React Hook Form's
     |                                                                          useForm() watch() function
     |                                                                          cannot be memoized safely.

✖ 1 problem (0 errors, 1 warning)
```

### Lint Summary

| Category | Count |
|---|---|
| Errors | 0 |
| Warnings | 1 |
| Files with issues | 1 |

**Affected File:** `app/(dashboard)/users/new/page.tsx`  
**Rule:** `react-hooks/incompatible-library`  
**Cause:** React Compiler (enabled in Next.js 16) detects that `watch()` from `react-hook-form` returns
an unstable function reference that cannot be safely memoized, so the compiler skips memoizing the
entire `NewUserPage` component.

**Impact:** The `NewUserPage` component will not be automatically memoized by React Compiler.
This could lead to unnecessary re-renders but is not a functional bug.

---

## Build Results

> **NOTE**: A full production build (`npm run build`) was NOT run to avoid side effects.
> The following analysis is based on static code inspection.

### Estimated Build Characteristics

| Item | Assessment |
|---|---|
| Framework | Next.js 16.2.10 App Router |
| Output mode | Default (Node.js server) |
| SSR pages | None — all pages are `'use client'` |
| SSG pages | None detected |
| Dynamic routes | `/users/[id]`, `/leads/[id]`, `/knowledge/[id]`, `/roles/[id]` |
| Static routes | `/`, `/login`, `/dashboard`, `/users`, `/leads`, `/crm`, `/analytics`, `/knowledge`, `/roles`, `/settings`, `/knowledge/new`, `/users/new`, `/roles/new` |

### Client-Side Only Pages

All protected dashboard pages use `'use client'` directive. This means:
- **No SSR** — all content rendered client-side
- **First paint** shows loading skeleton
- **SEO** — not applicable for admin panel ✅

### Potential Build Warnings (Predicted)

| Warning | Cause |
|---|---|
| React Compiler incompatible library | `react-hook-form` watch() in users/new page |
| Large bundle | `framer-motion` (sidebar animations), `@dnd-kit` (CRM), `@base-ui/react` |
| `@base-ui/react` version `^1.6.0` | Relatively new library — may have breaking changes |

### Dependencies Risk Assessment

| Package | Version | Risk |
|---|---|---|
| `next` | 16.2.10 | ✅ Stable (though non-standard v16) |
| `react` | 19.2.4 | ⚠️ React 19 is recent — some libraries may not be fully compatible |
| `@tanstack/react-query` | ^5.101.2 | ✅ v5 stable |
| `@base-ui/react` | ^1.6.0 | ⚠️ Pre-1.0 API — breaking changes possible |
| `framer-motion` | ^12.42.2 | ✅ Stable |
| `@dnd-kit/core` | ^6.3.1 | ✅ Stable |
| `lucide-react` | ^1.23.0 | ⚠️ v1.x — verify icon availability |
| `zod` | ^4.4.3 | ⚠️ Zod v4 is new — API changes from v3 |
| `shadcn` | ^4.13.0 | ✅ CLI tool (dev) |

### Static vs Dynamic Routes

| Type | Routes |
|---|---|
| Static | `/login`, `/dashboard`, `/users`, `/leads`, `/crm`, `/analytics`, `/knowledge`, `/roles`, `/settings`, `/users/new`, `/knowledge/new` |
| Dynamic | `/users/[id]`, `/leads/[id]`, `/knowledge/[id]`, `/roles/[id]`, `/users/[id]/edit`, `/knowledge/[id]/edit`, `/roles/[id]/edit` |

---

## ESLint Config

**File:** `eslint.config.mjs`

Standard Next.js ESLint config with React Compiler plugin (based on warning output showing `react-hooks` rules).
