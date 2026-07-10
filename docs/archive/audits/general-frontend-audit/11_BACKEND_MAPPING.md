# 11 — Backend Mapping Audit

**Date:** 2026-07-08

---

## Mapping Table: Frontend Feature ↔ Backend Endpoint

| Frontend Feature | Backend Endpoint | HTTP Method | Status | Notes |
|---|---|---|---|---|
| **AUTH** | | | | |
| Login | `api/v1/auth/login/` | POST | ✅ Integrated | |
| Logout | `api/v1/auth/logout/` | POST | ✅ Integrated | |
| Get Me (current user) | `api/v1/auth/me/` | GET | ✅ Integrated | |
| Token Refresh | `api/v1/auth/refresh/` | POST | ✅ Integrated | Called by interceptor |
| **DASHBOARD** | | | | |
| KPI Stats | `api/v1/admin/analytics/` | GET | ✅ Integrated | Also duplicated in analytics feature |
| Lead Status Summary | `api/v1/admin/dashboard/` | GET | ✅ Integrated | Also duplicated in analytics feature |
| Analytics Timeline | `api/v1/admin/analytics/timeline/` | GET | ✅ Integrated | Duplicated |
| Funnel Stages | `api/v1/admin/analytics/funnel/` | GET | ✅ Integrated | Duplicated |
| Recent Leads | `api/v1/admin/leads/?page_size=5` | GET | ✅ Integrated | |
| **USERS** | | | | |
| List Users | `api/v1/admin/users/` | GET | ✅ Integrated | |
| Get User | `api/v1/admin/users/{id}/` | GET | ✅ Integrated | |
| Create User | `api/v1/admin/users/` | POST | ✅ Integrated | |
| Update User | `api/v1/admin/users/{id}/` | PATCH | ✅ Integrated | |
| Activate User | `api/v1/admin/users/{id}/activate/` | POST | ✅ Integrated | |
| Deactivate User | `api/v1/admin/users/{id}/deactivate/` | POST | ✅ Integrated | |
| Reset Password | `api/v1/admin/users/{id}/reset-password/` | POST | ✅ Integrated | |
| Bulk Activate | `api/v1/admin/users/bulk-activate/` | POST | ✅ Integrated | |
| Bulk Deactivate | `api/v1/admin/users/bulk-deactivate/` | POST | ✅ Integrated | |
| User Audit Log | `api/v1/admin/users/{id}/audit-log/` | GET | ✅ Integrated | |
| **LEADS** | | | | |
| List Leads | `api/v1/admin/leads/` | GET | ✅ Integrated | |
| Get Lead Detail | `api/v1/admin/leads/{uuid}/` | GET | ✅ Integrated | |
| Update Lead Status | `api/v1/admin/leads/{uuid}/` | PATCH | ✅ Integrated | |
| Create Lead | N/A | — | ❌ Missing | Leads created by chatbot only |
| Delete Lead | N/A | — | ❌ Missing | No delete in backend URLs |
| Assign Lead | N/A | — | ❌ Missing | `assigned_admin_id` field exists in model but no assignment endpoint |
| **CRM PIPELINE** | | | | |
| Load Pipeline Leads | `api/v1/admin/leads/?page_size=100` | GET | ✅ Integrated | Reuses leadsApi |
| Move Lead Status | `api/v1/admin/leads/{uuid}/` | PATCH | ✅ Integrated | Optimistic update |
| **ANALYTICS** | | | | |
| Analytics Stats | `api/v1/admin/analytics/` | GET | ⚠️ Duplicate | Same as dashboard stats |
| Timeline | `api/v1/admin/analytics/timeline/` | GET | ⚠️ Duplicate | Different cache key |
| Funnel | `api/v1/admin/analytics/funnel/` | GET | ⚠️ Duplicate | Different cache key |
| Lead Summary | `api/v1/admin/dashboard/` | GET | ⚠️ Duplicate | Different cache key |
| Export Analytics | N/A | — | ❌ Missing | Button exists but disabled (backend TODO) |
| Date range filter | N/A | — | ❌ Missing | Frontend note says "coming soon" |
| **KNOWLEDGE BASE** | | | | |
| List Entries | `api/v1/admin/kb/entries/` | GET | ✅ Integrated | |
| Get Entry | `api/v1/admin/kb/entries/{uuid}/` | GET | ✅ Integrated | |
| Create Entry | `api/v1/admin/kb/entries/` | POST | ✅ Integrated | |
| Update Entry | `api/v1/admin/kb/entries/{uuid}/` | PATCH | ✅ Integrated | |
| Delete Entry | `api/v1/admin/kb/entries/{uuid}/` | DELETE | ✅ Integrated | |
| Publish Entry | `api/v1/admin/kb/entries/{uuid}/publish/` | POST | ✅ Integrated | |
| Unpublish Entry | `api/v1/admin/kb/entries/{uuid}/unpublish/` | POST | ✅ Integrated | |
| Archive Entry | `api/v1/admin/kb/entries/{uuid}/archive/` | POST | ✅ Integrated | |
| Restore Entry | `api/v1/admin/kb/entries/{uuid}/restore/` | POST | ❌ Backend exists, no frontend | Backend URL defined, no frontend call |
| Public KB List | `api/v1/kb/entries/` | GET | ❌ Unused | Only for public chatbot, not admin |
| **ROLES** | | | | |
| List Roles | `api/v1/admin/roles/` | GET | ✅ Integrated | |
| Get Role | `api/v1/admin/roles/{id}/` | GET | ✅ Integrated | |
| Create Role | `api/v1/admin/roles/` | POST | ✅ Integrated | |
| Update Role | `api/v1/admin/roles/{id}/` | PATCH | ✅ Integrated | |
| Delete Role | `api/v1/admin/roles/{id}/` | DELETE | ✅ Integrated | |
| Get Permissions | `api/v1/admin/roles/permissions/` | GET | ✅ Integrated | |
| Set Permissions | `api/v1/admin/roles/{id}/set-permissions/` | PUT | ✅ Integrated | |
| Get Role Users | `api/v1/admin/roles/{id}/users/` | GET | ✅ Integrated | |
| Assign Users | `api/v1/admin/roles/{id}/assign-users/` | POST | ✅ Integrated | |
| Remove Users | `api/v1/admin/roles/{id}/remove-users/` | POST | ✅ Integrated | |
| **SETTINGS** | | | | |
| List All Settings | `api/v1/admin/settings/` | GET | ✅ Integrated | Unused in UI (only category-based used) |
| Get Category | `api/v1/admin/settings/{category}/` | GET | ✅ Integrated | |
| Update Category | `api/v1/admin/settings/{category}/` | PATCH | ✅ Integrated | |
| Public Settings | `api/v1/settings/public/` | GET | ✅ Integrated (hook) | `usePublicSettings` exists but not used in any page |
| **CHATBOT** | | | | |
| Chatbot webhook | `api/v1/` (chatbot app URLs) | — | ❌ Not in admin frontend | Chatbot is external/public facing |

---

## Status Legend

| Status | Meaning |
|---|---|
| ✅ Integrated | Frontend calls this endpoint and uses the response |
| ⚠️ Duplicate | Called by two separate frontend features with different cache keys |
| ❌ Missing | Backend endpoint exists but frontend doesn't call it |
| ❌ Unused | Frontend code exists but is never called from any page |

---

## Backend Endpoints With No Frontend Integration

| Endpoint | Why Missing |
|---|---|
| `api/v1/admin/kb/entries/{uuid}/restore/` | Backend defines it; `knowledgeApi` has no `restore()` method |
| `api/v1/kb/entries/` (public list) | Admin panel doesn't need public knowledge list |
| `api/v1/kb/entries/{slug}/` (public detail) | Same |
| All chatbot app endpoints | These are for the chatbot widget, not the admin panel |

---

## Frontend Hooks With No Page Usage

| Hook | Exported From | Used In Pages? |
|---|---|---|
| `usePublicSettings` | features/settings | ❌ Not used in any page |
| `usersApi` (direct API object) | features/users | ❌ Exported but hooks are used instead |
| `leadsApi` (direct API object) | features/leads | Used by CRM `use-pipeline.ts` ✅ |
