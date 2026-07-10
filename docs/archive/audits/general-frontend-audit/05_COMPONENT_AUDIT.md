# 05 — Component Audit

**Date:** 2026-07-08

---

## Header (components/layout/header.tsx)

| Check | Finding |
|---|---|
| Renders inside AppShell | ✅ |
| Uses `useAuth()` hook | ✅ |
| Logout triggers `useCallback` | ✅ |
| Notifications button is decorative (no API) | ⚠️ Hardcoded notification dot — not connected to backend |
| Search input is non-functional | ⚠️ `<Input type="search">` renders but does nothing — no handler, no state |
| **Nested button issue** | ⚠️ `DropdownMenuTrigger` wraps a `<Button>` which itself renders as a `<button>` element. The `@base-ui/react/menu` Trigger renders as its child — this creates `<button type="button"><button>` nesting = **invalid HTML / React warning** |
| User info fallback | If `user` is null, initials = `'U'` — safe |
| `user?.email` display | Could show `undefined` if email is empty string |

---

## Sidebar (components/layout/sidebar.tsx)

| Check | Finding |
|---|---|
| Collapse state | Managed in `AppShell` via `useState` — correct |
| Animation | `framer-motion` — `motion.aside` with `animate={{ width }}` |
| Tooltip wraps entire Link | ✅ — when collapsed, `<Tooltip><TooltipTrigger>{linkContent}</TooltipTrigger>` |
| **Nested interactive issue** | When expanded, `linkContent` is wrapped in `<div>`. When collapsed, `<TooltipTrigger>` wraps `linkContent`. `TooltipTrigger` from @base-ui renders as a span/div, so the Link (`<a>`) inside is fine — no nesting issue |
| Active state detection | `pathname.startsWith(item.href)` — can cause false positives (see route audit) |
| Icon class `h-4.5 w-4.5` | ⚠️ Non-standard Tailwind value — valid with Tailwind v4 arbitrary values but may not render correctly in all environments |

---

## MobileSidebar (components/layout/mobile-sidebar.tsx)

| Check | Finding |
|---|---|
| Uses Sheet (from @base-ui/react/dialog) | ✅ |
| **Nested button issue** | ⚠️ `<SheetTrigger>` (renders as `dialog.Trigger`, a button-like element) wraps `<Button>` — creates button-in-button nesting |
| Closes on link click | ✅ `onClick={() => setOpen(false)}` |
| Icon class `h-4.5 w-4.5` | ⚠️ Same non-standard value as Sidebar |

---

## AppShell (components/layout/app-shell.tsx)

| Check | Finding |
|---|---|
| Inline `<style>` tag inside JSX | ⚠️ Uses `<style>` tag with `!important` rules inside component body — causes a React hydration mismatch warning since CSS is injected after SSR |
| Sidebar margin managed via data-attribute + CSS | Creative approach but fragile — margin is hardcoded as 64px/256px, not synced with motion.aside animation |
| `style={{ marginLeft: undefined }}` | ⚠️ Explicit `undefined` assigned to style — while harmless, it's unnecessary and confusing |

---

## Button (components/ui/button.tsx)

| Check | Finding |
|---|---|
| Backed by `@base-ui/react/button` | Yes — renders as an actual `<button>` element |
| Used as wrapper for DropdownMenuTrigger | ⚠️ **CRITICAL**: In `header.tsx`, `<DropdownMenuTrigger><Button>` creates button-in-button. @base-ui MenuTrigger renders as a `<button>` by default — nested buttons is invalid HTML |
| Used inside Link elements | Many places: `<Link href=...><Button>` — valid, Link renders as `<a>`, Button as `<button>` inside — ok |
| Used inside `<a href=...>` | In `leads/[id]/page.tsx`: `<a href="mailto:..."><Button>` — `<button>` inside `<a>` is **invalid HTML** |

---

## Dialog (components/ui/dialog.tsx)

| Check | Finding |
|---|---|
| Backed by `@base-ui/react/dialog` | ✅ |
| Used in `ConfirmDialog`, `DeleteDialog` | ✅ |
| Accessibility | `@base-ui` handles ARIA attributes |
| `ConfirmDialog` accepts `isLoading` prop | ✅ shows loader state |

---

## Sheet (components/ui/sheet.tsx)

| Check | Finding |
|---|---|
| Backed by `@base-ui/react/dialog` (same primitive as Dialog!) | ⚠️ Both Sheet and Dialog use `Dialog as SheetPrimitive from @base-ui/react/dialog` — they are literally the same primitive. This could cause conflicts if both are open simultaneously |
| Close button inside SheetContent | ✅ auto-rendered |
| MobileSidebar SheetTrigger + Button nesting | ⚠️ See MobileSidebar section |

---

## Dropdown (components/ui/dropdown-menu.tsx)

| Check | Finding |
|---|---|
| Backed by `@base-ui/react/menu` | ✅ |
| `DropdownMenuTrigger` wraps Button in Header | ⚠️ Creates button-in-button |
| Renders via Portal | ✅ |

---

## Tooltip (components/ui/tooltip.tsx)

| Check | Finding |
|---|---|
| Backed by `@base-ui/react/tooltip` | ✅ |
| `TooltipProvider` in root layout | ✅ |
| `TooltipTrigger` in Sidebar wraps Link | ✅ — Link is an `<a>`, Trigger renders as `<span>` — valid |
| Analytics page: `<TooltipTrigger><Button disabled>` | ⚠️ Disabled buttons don't fire mouse events — tooltip may not show on hover |

---

## Summary of Component Issues

### Critical (Invalid HTML / React Warnings)

| Issue | Location | Detail |
|---|---|---|
| Button-in-button | `header.tsx` L54 | `<DropdownMenuTrigger><Button>` — @base-ui Trigger renders as `<button>` |
| Button-in-button | `mobile-sidebar.tsx` L19-23 | `<SheetTrigger><Button>` — same issue |
| Button inside anchor | `leads/[id]/page.tsx` L292-303 | `<a href="mailto:..."><Button>` — invalid HTML |

### High (Hydration Risks)

| Issue | Location | Detail |
|---|---|---|
| Inline `<style>` tag | `app-shell.tsx` L23-28 | Injected post-SSR — hydration mismatch |
| `localStorage` access in render | `use-auth.ts` L34 | `enabled: hasAccessToken()` — `hasAccessToken()` called during render, SSR-safe only because it checks `typeof window` |

### Medium (Accessibility)

| Issue | Location | Detail |
|---|---|---|
| Non-functional search input | `header.tsx` | `<Input type="search">` with no handler |
| Decorative notification dot | `header.tsx` | Bell icon + red dot with no data |
| Disabled button tooltip | `analytics/page.tsx` | Disabled elements don't receive hover events |
| Non-standard icon size class | `sidebar.tsx`, `mobile-sidebar.tsx` | `h-4.5 w-4.5` — may not render |

### Low

| Issue | Location | Detail |
|---|---|---|
| `style={{ marginLeft: undefined }}` | `app-shell.tsx` | Unnecessary |
| Sheet and Dialog share primitive | `sheet.tsx`, `dialog.tsx` | Potential conflict |
