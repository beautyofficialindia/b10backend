# API Contract Verification

## Authentication

| Endpoint | Backend Response | Frontend Expectation | Match? |
|----------|-----------------|---------------------|--------|
| POST /auth/login/ | `{access, refresh, user: {id, username, email, role}}` | `{access, refresh}` | 🟡 Partial — frontend ignores `user` field |
| POST /auth/refresh/ | `{access}` | `data.access` stored to localStorage | ✅ VERIFIED |
| POST /auth/logout/ | `{detail: "Successfully logged out."}` | Fire-and-forget (void) | ✅ VERIFIED |
| GET /auth/me/ | `{id, username, email, first_name, last_name, role, groups: [{id, name}]}` | `{id, username, email, first_name, last_name, is_active, is_staff, is_superuser, groups: string[]}` | 🔴 MISMATCH |

### /auth/me/ Mismatch Details
- **Backend returns** `groups` as array of `{id: number, name: string}` objects (via `GroupSerializer`)
- **Frontend expects** `groups` as `string[]`
- **Backend returns** `role` field (string, first group name)
- **Frontend expects** `is_active`, `is_staff`, `is_superuser` — **NOT returned by backend**
- **Root cause**: Backend `UserSerializer` only includes `['id', 'username', 'email', 'first_name', 'last_name', 'role', 'groups']`

## Dashboard / Analytics

| Endpoint | Backend Response | Frontend Expectation | Match? |
|----------|-----------------|---------------------|--------|
| GET /admin/analytics/ | `{total_chats, total_messages, total_leads, qualified_leads, converted_leads, lost_leads, qualification_rate, conversion_rate}` | Same fields | ✅ VERIFIED |
| GET /admin/dashboard/ | `{total_leads, gathering, qualified, converted, lost, escalated}` | Same fields | ✅ VERIFIED |
| GET /admin/analytics/timeline/ | `{date: {event_type: count}}` | `Record<string, Record<string, number>>` | ✅ VERIFIED |
| GET /admin/analytics/funnel/ | `[{stage, value}]` | `FunnelStage[]` | ✅ VERIFIED |
| GET /admin/leads/?page_size=5 | `{count, next, previous, results: Lead[]}` | `{results: Lead[]}` | ✅ VERIFIED (only uses .results) |

## Leads

| Endpoint | Backend Response | Frontend Expectation | Match? |
|----------|-----------------|---------------------|--------|
| GET /admin/leads/ | `{count, next, previous, results}` (DRF PageNumberPagination) | `{count, next, previous, results}` | ✅ VERIFIED |
| GET /admin/leads/{id}/ | Full Lead model fields (not wrapped) | `LeadDetail` (raw object) | ✅ VERIFIED |
| PATCH /admin/leads/{id}/ | Updated Lead object (not wrapped) | `LeadDetail` | ✅ VERIFIED |

## Knowledge Base

| Endpoint | Backend Response | Frontend Expectation | Match? |
|----------|-----------------|---------------------|--------|
| GET /admin/kb/entries/ | `{success, data: [...], meta: {pagination}}` (StandardPageNumberPagination) | `KBListResponse` with same structure | ✅ VERIFIED |
| GET /admin/kb/entries/{id}/ | `{success: true, data: KnowledgeEntryDetail}` | `{data: KnowledgeEntryDetail}` | ✅ VERIFIED |
| POST /admin/kb/entries/ | `{success: true, data: ...}` (status 201) | `{data: KnowledgeEntryDetail}` | ✅ VERIFIED |
| PATCH /admin/kb/entries/{id}/ | `{success: true, data: ...}` | `{data: KnowledgeEntryDetail}` | ✅ VERIFIED |
| DELETE /admin/kb/entries/{id}/ | `{success: true, data: {}}` (status 204) | void | ✅ VERIFIED |

## Users Management

| Endpoint | Backend Response | Frontend Expectation | Match? |
|----------|-----------------|---------------------|--------|
| GET /admin/users/ | `{success, data: [...], meta: {pagination}}` | `UserListResponse` | ✅ VERIFIED |
| GET /admin/users/{id}/ | `{success, data: UserDetail}` | `{data: UserDetail}` | ✅ VERIFIED |
| POST /admin/users/ | `{success, data: UserDetail}` (201) | `{data: UserDetail}` | ✅ VERIFIED |
| PATCH /admin/users/{id}/ | `{success, data: UserDetail}` | `{data: UserDetail}` | ✅ VERIFIED |
| POST /admin/users/{id}/activate/ | `{success, data: UserDetail}` | `{data: UserDetail}` | ✅ VERIFIED |
| POST /admin/users/{id}/deactivate/ | `{success, data: UserDetail}` | `{data: UserDetail}` | ✅ VERIFIED |
| POST /admin/users/{id}/reset-password/ | `{success, message}` | void | ✅ VERIFIED |
| GET /admin/users/{id}/audit-log/ | `{success, data: [...], meta: {pagination}}` | `{data, meta}` | ✅ VERIFIED |
| POST /admin/users/bulk-activate/ | `{success, data: {activated_count, skipped}}` | `{data: BulkResult}` | ✅ VERIFIED |
| POST /admin/users/bulk-deactivate/ | `{success, data: {deactivated_count, skipped}}` | `{data: BulkResult}` | ✅ VERIFIED |

## Roles Management

| Endpoint | Backend Response | Frontend Expectation | Match? |
|----------|-----------------|---------------------|--------|
| GET /admin/roles/ | `{success, data, meta: {pagination}}` | `PaginatedResponse<Role>` | ✅ VERIFIED |
| GET /admin/roles/{id}/ | `{success, data: RoleDetail}` | `{data: RoleDetail}` | ✅ VERIFIED |
| POST /admin/roles/ | `{success, data: RoleDetail}` (201) | `{data: RoleDetail}` | ✅ VERIFIED |
| GET /admin/roles/permissions/ | `{success, data: Permission[]}` | `{data: Permission[]}` | ✅ VERIFIED |
| PUT /admin/roles/{id}/set-permissions/ | `{success, data: RoleDetail}` | `{data: RoleDetail}` | ✅ VERIFIED |
| GET /admin/roles/{id}/users/ | `{success, data, meta: {pagination}}` | `PaginatedResponse<RoleUser>` | ✅ VERIFIED |

## Settings

| Endpoint | Backend Response | Frontend Expectation | Match? |
|----------|-----------------|---------------------|--------|
| GET /admin/settings/{category}/ | `{success, data: Setting[]}` | `{data: Setting[]}` | ✅ VERIFIED |
| PATCH /admin/settings/{category}/ | `{success, data: Setting[]}` | `{data: Setting[]}` | ✅ VERIFIED |
| GET /settings/public/ | `{success, data: [{category, key, value}]}` | `{data: [...]}` | ✅ VERIFIED |
