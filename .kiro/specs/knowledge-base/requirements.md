# Requirements Document

## Introduction

This document defines the requirements for a database-backed Knowledge Base (KB) module for the B10 IT Solution Django backend. The module introduces a new `apps/knowledge_base` Django app that provides full CRUD management, a three-state content lifecycle (Draft → Published → Archived), soft-delete with recovery, full-text search, filtering, and pagination across an extensible set of knowledge categories.

The chatbot's existing `KnowledgeLoader` service currently reads from JSON files located at `knowledge/`. The integration strategy is **additive and non-destructive**: the JSON source remains the active chatbot data source during the initial rollout. The new DB-backed module runs in parallel, and a future phase will add a feature flag to switch the chatbot to the DB source.

All migrations are additive only — no existing tables, columns, or data are modified or dropped.

---

## Glossary

- **KB_App**: The new `apps.knowledge_base` Django application.
- **KnowledgeEntry**: The single polymorphic-style database model that stores all knowledge content, discriminated by `category`.
- **Category**: An enumerated type on `KnowledgeEntry`. Valid values: `company`, `service`, `industry`, `faq`, `contact`, `technology`, `general`. New values may be added via a future migration without modifying existing entries.
- **Status**: A three-state lifecycle field on `KnowledgeEntry`. Valid values: `draft` (default, not publicly visible), `published` (publicly visible, eligible for chatbot injection), `archived` (hidden from public and chatbot but retained for audit purposes).
- **Soft-Delete**: Entries marked with `is_deleted=True` are excluded from all queryset results by default but remain in the database and are recoverable by an Admin user.
- **Source**: An enumerated field on `KnowledgeEntry` recording how the entry was created. Valid values: `manual` (created via API or Admin UI), `json_import` (created by the seed management command from JSON files), `api` (created via an external API integration). Supports migration traceability — the seed command sets `source='json_import'` on all entries it creates.
- **KnowledgeLoader**: The existing service at `apps/chatbot/services/knowledge_loader.py` that currently reads JSON files. It is not modified in Phase 1.
- **KnowledgeService**: A new service class in `apps/knowledge_base/services/knowledge_service.py` that performs all DB reads and writes for knowledge entries.
- **KnowledgeAdmin**: The Django Admin registration for `KnowledgeEntry` inside `apps/knowledge_base/admin.py`.
- **Slug**: A URL-safe, human-readable unique string identifier for a knowledge entry derived from its title.
- **Published**: An entry whose `status` is `'published'` and `is_deleted` is `False`. Only published entries are visible via public-facing endpoints and to the chatbot when DB mode is active.
- **Admin_User**: An authenticated user whose Django Group is `Admin`.
- **Public_Endpoint**: An API endpoint with no authentication requirement, accessible by anonymous users.
- **Internal_Endpoint**: An API endpoint requiring `Admin` group authentication via JWT Bearer token.
- **StandardPageNumberPagination**: The existing paginator in `common/pagination.py` (page size 20, max 100).
- **success_response / error_response**: The existing response helpers in `common/responses.py`.

---

## Requirements

---

### Requirement 1: Knowledge Base App Structure

**User Story:** As a backend developer, I want a self-contained Django app for the Knowledge Base, so that it is isolated from existing apps and can be maintained independently.

#### Acceptance Criteria

1. THE KB_App SHALL exist at `backend/apps/knowledge_base/` with the standard Django app structure: `__init__.py`, `apps.py`, `models.py`, `serializers.py`, `views.py`, `urls.py`, `admin.py`, a `services/` sub-package containing `__init__.py` and `knowledge_service.py`, and a `migrations/` sub-package.
2. THE KB_App SHALL be registered in `INSTALLED_APPS` in `core/settings.py` as `apps.knowledge_base`.
3. THE KB_App SHALL have its URLs mounted in `core/urls.py` at two prefixes sourced from the KB_App's single `urls.py` file: `api/v1/kb/` for public read endpoints, and `api/v1/admin/kb/` for internal management endpoints.
4. THE KB_App SHALL include an `apps.py` `AppConfig` with `name = 'apps.knowledge_base'` and `default_auto_field = 'django.db.models.BigAutoField'`.

---

### Requirement 2: KnowledgeEntry Model

**User Story:** As a backend developer, I want a single, well-structured database model for all knowledge entries, so that all current and future knowledge categories are stored, lifecycle-managed, and safely recoverable from one table.

#### Acceptance Criteria

1. THE KB_App SHALL define a `KnowledgeEntry` model in `models.py` with the following fields:
   - `id`: `UUIDField`, primary key, non-editable, default `uuid.uuid4`.
   - `category`: `CharField`, max_length 20, choices limited to `('company', 'Company Info')`, `('service', 'Service')`, `('industry', 'Industry')`, `('faq', 'FAQ')`, `('contact', 'Contact Info')`, `('technology', 'Technology')`, `('general', 'General')`. New category values MAY be added via future migrations without altering existing rows.
   - `title`: `CharField`, max_length 255, `blank=False`, `null=False`. For FAQ entries this holds the question. For company/contact it holds the section name.
   - `slug`: `SlugField`, max_length 255, unique, `blank=True` (auto-generated before save).
   - `content`: `TextField`, `blank=False`, `null=False`. For FAQ entries this holds the answer. For structured entries this holds a human-readable summary.
   - `structured_data`: `JSONField`, default `dict`, `blank=True`. Stores the full structured payload (e.g., technologies list, address, booking URL).
   - `status`: `CharField`, max_length 20, choices `('draft', 'Draft')`, `('published', 'Published')`, `('archived', 'Archived')`, default `'draft'`.
   - `sort_order`: `PositiveIntegerField`, default 0. Controls display ordering within a category.
   - `created_by`: `ForeignKey` to `auth.User`, `on_delete=SET_NULL`, null, blank, `related_name='kb_entries_created'`.
   - `updated_by`: `ForeignKey` to `auth.User`, `on_delete=SET_NULL`, null, blank, `related_name='kb_entries_updated'`.
   - `published_at`: `DateTimeField`, null, blank. Set when status first transitions to `'published'`.
   - `is_deleted`: `BooleanField`, default `False`.
   - `deleted_at`: `DateTimeField`, null, blank. Set when `is_deleted` is set to `True`.
   - `source`: `CharField`, max_length 20, choices `('manual', 'Manual')`, `('json_import', 'JSON Import')`, `('api', 'API')`, default `'manual'`. Records the origin of the entry for migration traceability.
   - `created_at`: `DateTimeField`, `auto_now_add=True`.
   - `updated_at`: `DateTimeField`, `auto_now=True`.
2. WHEN a `KnowledgeEntry` is saved and `slug` is empty, THE `KnowledgeEntry` model SHALL auto-generate `slug` from `title` using `django.utils.text.slugify` in an overridden `save()` method before writing to the database.
3. IF the slugified value from the `title` collides with an existing `slug` in the database, THEN THE `KnowledgeEntry` model SHALL append a hyphen followed by the first 8 characters of a new `uuid.uuid4()` hex string to produce a unique slug.
4. THE `KnowledgeEntry` model SHALL define a `Meta` class with `ordering = ['category', 'sort_order', 'created_at']` and `verbose_name_plural = 'Knowledge Entries'`.
5. THE `KnowledgeEntry` model SHALL define `__str__` returning `f"[{self.category}] {self.title}"`.
6. WHEN a `KnowledgeEntry` is saved with `status='published'` and `published_at` is `None`, THE `KnowledgeEntry` model SHALL set `published_at` to the current UTC time in the `save()` method before writing to the database.
7. WHEN a `KnowledgeEntry` is saved with `is_deleted=True` and `deleted_at` is `None`, THE `KnowledgeEntry` model SHALL set `deleted_at` to the current UTC time in the `save()` method before writing to the database.

---

### Requirement 3: Initial Database Migration

**User Story:** As a backend developer, I want an initial additive migration for the Knowledge Base, so that the new table is created without touching any existing tables.

#### Acceptance Criteria

1. THE KB_App SHALL include a migration file `migrations/0001_initial.py` that creates only the `knowledge_base_knowledgeentry` table using Django ORM `CreateModel` operations with no raw SQL or database-specific column types.
2. THE migration SHALL NOT modify, rename, or delete any table outside `apps/knowledge_base`.
3. THE migration's `dependencies` list SHALL reference only `django.contrib.auth` migrations and no migrations from other project apps (chatbot, leads, analytics, crm, accounts).
4. WHEN `python manage.py migrate` is executed against a clean database, THE migration SHALL apply with exit code 0 and no `MigrationError` or `OperationalError` on both the SQLite test database and the production PostgreSQL database.
5. WHEN `python manage.py migrate` is executed against a database where the migration has already been applied, THE command SHALL exit with code 0 and report the migration as already applied without re-running the operation.

---

### Requirement 4: KnowledgeService

**User Story:** As a backend developer, I want a dedicated service class for all Knowledge Base data operations, so that business logic is decoupled from views and is independently testable.

#### Acceptance Criteria

1. THE KB_App SHALL include a `KnowledgeService` class at `apps/knowledge_base/services/knowledge_service.py` with the following methods:
   - `list_entries(category=None, search=None, status=None, include_deleted=False)` — returns a filtered `QuerySet`; by default excludes soft-deleted entries (`is_deleted=False`).
   - `get_entry(pk, include_deleted=False)` — returns a single `KnowledgeEntry` or raises `KnowledgeEntry.DoesNotExist` if no matching entry exists; by default excludes soft-deleted entries.
   - `create_entry(data, user)` — validates `data` against required fields (`category`, `title`); if valid, creates and returns a `KnowledgeEntry` with `created_by` set to `user` and `status` defaulting to `'draft'`; if invalid, raises `ValueError` with a message indicating the missing or invalid fields.
   - `update_entry(entry, data, user)` — validates `data` fields against allowed writable fields (`category`, `title`, `content`, `structured_data`, `sort_order`); if valid, applies the provided fields to `entry`, sets `updated_by` to `user`, saves, and returns the entry; if `data` contains unrecognized or invalid field values, raises `ValueError`.
   - `delete_entry(entry, user)` — soft-deletes the entry by setting `is_deleted=True`, `deleted_at` to the current UTC time, and `updated_by` to `user`; does NOT remove the database row.
   - `restore_entry(entry, user)` — clears `is_deleted=False`, clears `deleted_at` to `None`, sets `updated_by` to `user`, saves, and returns the entry.
   - `publish_entry(entry, user)` — sets `status='published'`, sets `updated_by` to `user`, saves, and returns the entry; `published_at` is set to the current UTC time only if it is currently `None`.
   - `unpublish_entry(entry, user)` — sets `status='draft'`, sets `updated_by` to `user`, saves, and returns the entry; `published_at` SHALL NOT be cleared.
   - `archive_entry(entry, user)` — sets `status='archived'`, sets `updated_by` to `user`, saves, and returns the entry; `published_at` SHALL NOT be cleared.
   - `get_category_as_text(category)` — returns a plain-text string of all published (non-deleted) entries for the given category, where each entry is rendered as `"{title}\n{content}"` and entries are separated by `"\n\n"`; returns an empty string if no published entries exist for that category.
   - `get_scoped_knowledge_as_text(company=True, services=True, industries=True, faq=True, contact=True)` — returns a single concatenated plain-text string of published (non-deleted) entries for all requested categories, formatted to match `KnowledgeLoader.get_scoped_knowledge_as_text` exactly (see Criterion 5 below).
2. WHEN `list_entries` is called with `status='published'`, THE `KnowledgeService` SHALL return only entries where `status='published'` and `is_deleted=False`.
3. WHEN `list_entries` is called with a `search` string that contains at least one non-whitespace character, THE `KnowledgeService` SHALL filter entries where `title` or `content` contains the search string (case-insensitive); IF `search` is `None`, empty, or contains only whitespace characters, THE `KnowledgeService` SHALL apply no search filter.
4. WHEN `list_entries` is called with a `category` value, THE `KnowledgeService` SHALL filter entries to that category only.
5. WHEN `publish_entry` is called on an entry where `status` is already `'published'`, THE `KnowledgeService` SHALL update `updated_by` to `user`, save, and return the entry without modifying `published_at`.
6. IF `create_entry` is called with `data` missing the `category` field or the `title` field, THEN THE `KnowledgeService` SHALL raise a `ValueError` indicating which required field is absent, and no `KnowledgeEntry` record SHALL be created in the database.
7. WHEN `get_scoped_knowledge_as_text` is called, THE `KnowledgeService` SHALL produce output in the following exact format for each requested category that has at least one published (non-deleted) entry, joined in the order: company, services, industries, faq, contact:
   - Company: `"Company Information:\n{json.dumps(entries_as_list_of_dicts, indent=2)}\n\n"`
   - Services: `"Services Provided:\n{json.dumps(entries_as_list_of_dicts, indent=2)}\n\n"`
   - Industries: `"Industries Served:\n{json.dumps(entries_as_list_of_dicts, indent=2)}\n\n"`
   - FAQ: `"Frequently Asked Questions (FAQ):\n{json.dumps(entries_as_list_of_dicts, indent=2)}\n\n"`
   - Contact: `"Contact Information:\n{json.dumps(entries_as_list_of_dicts, indent=2)}\n\n"`
   Where `entries_as_list_of_dicts` is the list of dicts produced by serializing each published entry as `{"title": entry.title, "content": entry.content, **entry.structured_data}`; IF no published entries exist for a requested category, THEN that section SHALL be omitted entirely (no empty-string block added).
8. WHEN `list_entries` is called with `include_deleted=False` (the default), THE `KnowledgeService` SHALL exclude all entries where `is_deleted=True` from the returned `QuerySet`.

---

### Requirement 5: Serializers

**User Story:** As a backend developer, I want serializers that validate all input and shape all output for Knowledge Base API responses, so that the API is consistent with the rest of the backend.

#### Acceptance Criteria

1. THE KB_App SHALL define a `KnowledgeEntryListSerializer` in `serializers.py` exposing: `id`, `category`, `title`, `slug`, `status`, `source`, `sort_order`, `published_at`, `created_at`, `updated_at`. All fields SHALL be read-only.
2. THE KB_App SHALL define a `KnowledgeEntryDetailSerializer` in `serializers.py` exposing all fields of `KnowledgeEntryListSerializer` plus `content`, `structured_data`, `created_by` (serialized as a plain string of the username, or `null` if unset), `updated_by` (serialized as a plain string of the username, or `null` if unset). All fields SHALL be read-only. The `is_deleted` and `deleted_at` fields SHALL NOT be included in this serializer (they are admin-only context).
3. THE KB_App SHALL define a `KnowledgeEntryWriteSerializer` in `serializers.py` accepting: `category`, `title`, `content` (optional), `structured_data` (optional), `sort_order` (optional), `source` (optional, defaults to `'manual'`). The `category` field SHALL validate against the allowed choices and return a field-level validation error with code `invalid_choice` for unrecognized values. The `source` field SHALL validate against `('manual', 'json_import', 'api')` and return a field-level validation error for unrecognized values. The fields `id`, `slug`, `status`, `published_at`, `created_at`, `updated_at`, `created_by`, `updated_by`, `is_deleted`, `deleted_at` SHALL NOT be accepted as input (status transitions are performed via dedicated endpoints only).
4. WHEN `KnowledgeEntryWriteSerializer` is used for creation, THE Serializer SHALL require `category` and `title` as mandatory fields; `content` is optional and defaults to an empty string.
5. WHEN `KnowledgeEntryWriteSerializer` is used for partial update (PATCH), THE Serializer SHALL accept any subset of `category`, `title`, `content`, `structured_data`, `sort_order` without requiring all of them.

---

### Requirement 6: Public Read Endpoints

**User Story:** As an anonymous API consumer or chatbot client, I want to read published knowledge entries without authentication, so that the knowledge base is accessible to public-facing features.

#### Acceptance Criteria

1. THE KB_App SHALL expose a `GET /api/v1/kb/entries/` endpoint that returns a paginated list of entries where `status='published'` and `is_deleted=False`, serialized with `KnowledgeEntryListSerializer` using `StandardPageNumberPagination`.
2. WHEN `GET /api/v1/kb/entries/` is called with a `category` query parameter, THE endpoint SHALL return only published (non-deleted) entries matching that category.
3. WHEN `GET /api/v1/kb/entries/` is called with a `search` query parameter, THE endpoint SHALL return only published (non-deleted) entries where `title` or `content` contains the search string (case-insensitive).
4. WHEN `GET /api/v1/kb/entries/{slug}/` is called for an entry where `status='published'` and `is_deleted=False`, THE endpoint SHALL return HTTP 200 with the entry serialized using `KnowledgeEntryDetailSerializer`.
5. IF a `GET /api/v1/kb/entries/{slug}/` request is made for a non-existent entry, a soft-deleted entry, or an entry whose `status` is not `'published'`, THEN THE endpoint SHALL return an `error_response` with HTTP 404 and code `NOT_FOUND_RESOURCE`.
6. THE public endpoints SHALL have `authentication_classes = []` and `permission_classes = []`, consistent with existing public chatbot endpoints.
7. THE public endpoints SHALL apply `AnonRateThrottle` throttling.

---

### Requirement 7: Admin Management Endpoints (CRUD)

**User Story:** As an Admin user, I want full CRUD API access to all knowledge entries regardless of status, so that I can manage the knowledge base content from any frontend admin panel.

#### Acceptance Criteria

1. THE KB_App SHALL expose a `GET /api/v1/admin/kb/entries/` endpoint that returns a paginated list of all non-deleted `KnowledgeEntry` records (all statuses) serialized with `KnowledgeEntryListSerializer` to `Admin_User` only.
2. THE KB_App SHALL expose a `POST /api/v1/admin/kb/entries/` endpoint that creates a new `KnowledgeEntry` with `status='draft'` and returns HTTP 201 with the created entry serialized using `KnowledgeEntryDetailSerializer`.
3. THE KB_App SHALL expose a `GET /api/v1/admin/kb/entries/{id}/` endpoint that returns the full detail of any non-deleted entry by UUID serialized using `KnowledgeEntryDetailSerializer` to `Admin_User`.
4. THE KB_App SHALL expose a `PATCH /api/v1/admin/kb/entries/{id}/` endpoint that partially updates an existing non-deleted entry and returns the updated entry serialized using `KnowledgeEntryDetailSerializer`.
5. THE KB_App SHALL expose a `DELETE /api/v1/admin/kb/entries/{id}/` endpoint that soft-deletes the entry (sets `is_deleted=True`, `deleted_at` to current UTC, `updated_by` to `request.user`) and returns HTTP 204. The database row SHALL NOT be removed.
6. THE KB_App SHALL expose a `POST /api/v1/admin/kb/entries/{id}/restore/` endpoint that restores a soft-deleted entry (sets `is_deleted=False`, clears `deleted_at`, sets `updated_by` to `request.user`) and returns HTTP 200 with the restored entry serialized using `KnowledgeEntryDetailSerializer`.
7. IF a management endpoint receives a request with no JWT token or with an expired/malformed JWT token, THEN THE endpoint SHALL return HTTP 401.
8. IF a management endpoint receives a request with a valid JWT token belonging to a non-Admin group (e.g., Sales, Support), THEN THE endpoint SHALL return HTTP 403.
9. IF a `GET`, `PATCH`, or `DELETE` request targets a non-existent or already-soft-deleted entry UUID (except the restore endpoint), THEN THE endpoint SHALL return an `error_response` with HTTP 404 and code `NOT_FOUND_RESOURCE`.
10. WHEN creating or updating an entry, THE endpoint SHALL set `created_by` or `updated_by` from `request.user`.
11. WHEN a `POST` or `PATCH` request contains invalid field values that fail `KnowledgeEntryWriteSerializer` validation, THE endpoint SHALL return HTTP 400 with a field-level error map.

---

### Requirement 8: Status Transition Endpoints (Publish / Unpublish / Archive)

**User Story:** As an Admin user, I want dedicated status transition actions on knowledge entries, so that content approval and archival are controlled, auditable steps separate from content editing.

#### Acceptance Criteria

1. WHEN a `POST /api/v1/admin/kb/entries/{id}/publish/` request is received for an existing non-deleted entry, THE endpoint SHALL set `status='published'`, update `updated_by` to `request.user`, set `published_at` to the current UTC time if it was previously `None`, save the entry, and return HTTP 200 with the updated entry serialized using `KnowledgeEntryDetailSerializer`.
2. WHEN a `POST /api/v1/admin/kb/entries/{id}/unpublish/` request is received for an existing non-deleted entry, THE endpoint SHALL set `status='draft'`, update `updated_by` to `request.user`, save the entry, and return HTTP 200 with the updated entry serialized using `KnowledgeEntryDetailSerializer`. The `published_at` field SHALL NOT be cleared.
3. WHEN a `POST /api/v1/admin/kb/entries/{id}/archive/` request is received for an existing non-deleted entry, THE endpoint SHALL set `status='archived'`, update `updated_by` to `request.user`, save the entry, and return HTTP 200 with the updated entry serialized using `KnowledgeEntryDetailSerializer`. The `published_at` field SHALL NOT be cleared.
4. WHEN a status transition endpoint is called on an entry already in the target status, THE endpoint SHALL update `updated_by` to `request.user`, save the entry, and return HTTP 200 without error (idempotent).
5. IF a status transition endpoint is called on a non-existent or soft-deleted entry, THEN THE endpoint SHALL return HTTP 404 with code `NOT_FOUND_RESOURCE`.
6. IF status transition endpoints receive a request with no JWT token or an expired/malformed JWT, THEN THE endpoints SHALL return HTTP 401.
7. IF status transition endpoints receive a request with a valid JWT belonging to a non-Admin group, THEN THE endpoints SHALL return HTTP 403.

---

### Requirement 9: Search and Filtering

**User Story:** As an Admin user or public consumer, I want to filter and search knowledge entries by category, status, and keyword, so that I can quickly locate relevant content.

#### Acceptance Criteria

1. THE KB_App SHALL support a `category` query parameter on both public and admin list endpoints, filtering entries to the specified category value.
2. THE KB_App SHALL support a `search` query parameter on both public and admin list endpoints, performing a case-insensitive `icontains` search across the `title` and `content` fields.
3. THE KB_App SHALL support a `status` query parameter on admin list endpoints accepting `draft`, `published`, `archived`; when provided, THE endpoint SHALL filter entries to those matching the specified status.
4. THE KB_App SHALL support an `ordering` query parameter on admin list endpoints accepting `created_at`, `-created_at`, `sort_order`, `-sort_order`, `title`, `-title`.
5. WHEN an unrecognized `category` filter value is provided, THE endpoint SHALL return an empty result set rather than an error.
6. WHEN a `search` query parameter is provided with only whitespace or is an empty string, THE endpoint SHALL ignore the search filter and return the full (category/status-filtered if applicable) result set.
7. WHEN both `category` and `search` query parameters are provided, THE endpoint SHALL apply both filters using AND semantics, returning only entries that match both the category and the search string.
8. WHEN `ordering` is provided with an unrecognized value on admin list endpoints, THE endpoint SHALL ignore the ordering parameter and return results in the default ordering (`category`, `sort_order`, `created_at`).

---

### Requirement 10: Pagination

**User Story:** As an API consumer, I want paginated responses for list endpoints, so that large knowledge bases do not overwhelm clients with unbounded data.

#### Acceptance Criteria

1. THE KB_App list endpoints SHALL use `StandardPageNumberPagination` from `common/pagination.py` with a default page size of 20 and a maximum page size of 100.
2. WHEN a list endpoint is called, THE response SHALL include a `meta.pagination` object with `page`, `page_size`, `total_count`, and `total_pages` fields, consistent with the existing paginator format.
3. THE KB_App SHALL support a `page` query parameter and a `page_size` query parameter on all list endpoints.
4. WHEN a `page` query parameter exceeds the total number of available pages, THE endpoint SHALL return HTTP 404 with code `NOT_FOUND_RESOURCE`.
5. WHEN a `page_size` query parameter exceeds 100, THE endpoint SHALL cap the page size at 100 and return results accordingly without raising an error.

---

### Requirement 11: Django Admin Integration

**User Story:** As an Admin user, I want Knowledge Base entries visible and manageable in the Django Admin panel, so that non-technical staff can edit content directly via the existing admin interface.

#### Acceptance Criteria

1. THE KB_App SHALL register `KnowledgeEntry` with `KnowledgeAdmin` in `admin.py` using `@admin.register`.
2. THE `KnowledgeAdmin` SHALL display `title`, `category`, `slug`, `status`, `is_deleted`, `sort_order`, `created_at`, `updated_at` in `list_display`.
3. THE `KnowledgeAdmin` SHALL support filtering by `category`, `status`, and `is_deleted` via `list_filter`.
4. THE `KnowledgeAdmin` SHALL support searching by `title` and `content` via `search_fields`.
5. THE `KnowledgeAdmin` SHALL declare `id`, `slug`, `created_at`, `updated_at`, `published_at`, `deleted_at`, `created_by`, `updated_by` as `readonly_fields`.
6. THE `KnowledgeAdmin` SHALL provide a custom `publish_selected` admin action that sets `status='published'` and `published_at` to the current UTC time (if `None`) on all selected non-deleted entries using a bulk queryset update.
7. THE `KnowledgeAdmin` SHALL provide a custom `unpublish_selected` admin action that sets `status='draft'` on all selected non-deleted entries using a bulk queryset update; `published_at` SHALL NOT be cleared.
8. THE `KnowledgeAdmin` SHALL provide a custom `archive_selected` admin action that sets `status='archived'` on all selected non-deleted entries using a bulk queryset update; `published_at` SHALL NOT be cleared.
9. THE `KnowledgeAdmin` SHALL provide a custom `restore_selected` admin action that sets `is_deleted=False` and `deleted_at=None` on all selected soft-deleted entries using a bulk queryset update.

---

### Requirement 12: Chatbot Integration (JSON Active, DB Standby)

**User Story:** As a developer, I want the chatbot to remain unaffected during the initial KB module rollout, so that the existing chatbot behavior is preserved while the new DB module is validated.

#### Acceptance Criteria

1. THE `KnowledgeLoader` (at `apps/chatbot/services/knowledge_loader.py`) SHALL NOT be modified during Phase 1 of the KB module implementation.
2. THE `PromptBuilder` (at `apps/chatbot/services/prompt_builder.py`) SHALL NOT be modified during Phase 1.
3. THE KB_App's `KnowledgeService` SHALL implement `get_scoped_knowledge_as_text(company=True, services=True, industries=True, faq=True, contact=True) -> str` accepting the same five boolean keyword arguments as `KnowledgeLoader.get_scoped_knowledge_as_text` with the same defaults.
4. WHEN `KnowledgeService.get_scoped_knowledge_as_text` is called, THE method SHALL produce output in the identical section format as `KnowledgeLoader.get_scoped_knowledge_as_text`: each enabled category whose published (non-deleted) entries are non-empty SHALL be rendered as `"{Section Label}:\n{json.dumps(data, indent=2)}\n\n"` where the section labels and order are: `"Company Information"` (company), `"Services Provided"` (services), `"Industries Served"` (industries), `"Frequently Asked Questions (FAQ)"` (faq), `"Contact Information"` (contact). IF a requested category has no published entries, THEN that section SHALL be omitted entirely (no placeholder added).
5. WHEN `KnowledgeService.get_scoped_knowledge_as_text` is used in DB mode, THE data for each section SHALL be derived from published (non-deleted, `status='published'`) `KnowledgeEntry` records for that category, serialized as a JSON-dumpable list of dicts where each dict is built as `{"title": entry.title, "content": entry.content, **entry.structured_data}`.
6. WHERE a `KNOWLEDGE_BASE_SOURCE` Django setting is configured to `'database'`, THE `PromptBuilder` SHALL use `KnowledgeService.get_scoped_knowledge_as_text` instead of `KnowledgeLoader.get_scoped_knowledge_as_text` in Phase 2 (future work, not implemented in Phase 1).
7. THE `KNOWLEDGE_BASE_SOURCE` setting SHALL default to `'json'` in `core/settings.py`, ensuring Phase 1 does not alter chatbot behavior.

---

### Requirement 13: Permissions Model

**User Story:** As a security-conscious developer, I want all Knowledge Base endpoints to enforce appropriate role-based permissions, so that content management is restricted to authorized users.

#### Acceptance Criteria

1. THE public read endpoints (`GET /api/v1/kb/entries/` and `GET /api/v1/kb/entries/{slug}/`) SHALL require no authentication, consistent with existing public chatbot endpoints.
2. THE admin management endpoints (`/api/v1/admin/kb/entries/` and sub-paths) SHALL require the `IsAdminUser` permission class from `apps/accounts/permissions.py`.
3. IF an admin endpoint receives a request with a valid JWT that belongs to a non-Admin group (Sales, Support), THEN THE endpoint SHALL return HTTP 403.
4. IF an admin endpoint receives a request with no JWT, an expired JWT, or a malformed JWT, THEN THE endpoint SHALL return HTTP 401.
5. IF an admin endpoint receives a valid JWT for an authenticated user who belongs to no group, THEN THE endpoint SHALL return HTTP 403.

---

### Requirement 14: Data Seeding from JSON

**User Story:** As an operator, I want a management command to seed the database from the existing JSON knowledge files, so that the DB module starts populated with current content.

#### Acceptance Criteria

1. THE KB_App SHALL include a Django management command at `apps/knowledge_base/management/commands/seed_knowledge_from_json.py`.
2. WHEN the command is executed, THE command SHALL read all five JSON files (`company.json`, `services.json`, `industries.json`, `faq.json`, `contact.json`) from the `knowledge/` directory (resolved as `BASE_DIR.parent / 'knowledge'`) and create corresponding `KnowledgeEntry` records in the database.
3. WHEN the command creates entries from `services.json`, THE command SHALL map each service object's `description` to `content`, `technologies` list to `structured_data['technologies']`, and `name` to `title`, with `category='service'` and `source='json_import'`.
4. WHEN the command creates entries from `faq.json`, THE command SHALL map `question` to `title`, `answer` to `content`, `category='faq'`, and `source='json_import'`.
5. WHEN the command creates entries from `company.json`, THE command SHALL create a single entry with `category='company'`, `title='Company Info'`, `description` to `content`, the full JSON object to `structured_data`, and `source='json_import'`.
6. WHEN the command creates entries from `industries.json`, THE command SHALL map each industry's `name` to `title`, `description` to `content`, `category='industry'`, and `source='json_import'`.
7. WHEN the command creates entries from `contact.json`, THE command SHALL create a single entry with `category='contact'`, `title='Contact Info'`, `content` set to a human-readable summary constructed as `f"Email: {email}. Phone: {phone}. Address: {address}."` using top-level keys from the JSON, the full JSON object to `structured_data`, and `source='json_import'`.
8. WHEN an entry whose slug (derived from `title` using `slugify`) already exists in the database, THE command SHALL skip that entry, log a `WARNING`-level message identifying the skipped title, and continue processing remaining entries without raising an exception.
9. WHEN the command completes, THE command SHALL print a summary line in the format `"Seeding complete: {created} created, {skipped} skipped, {failed} failed."`.
10. IF a JSON file is missing from the `knowledge/` directory or contains invalid JSON, THEN THE command SHALL log an `ERROR`-level message for that file, increment the `failed` counter, and continue processing the remaining files without raising an unhandled exception.

---

### Requirement 15: Testing Plan

**User Story:** As a developer, I want a comprehensive test suite for the Knowledge Base module, so that regressions are caught automatically and the module's correctness is verifiable.

#### Acceptance Criteria

1. THE KB_App SHALL include a `tests.py` file (or a `tests/` package) containing unit tests for `KnowledgeService` covering: `list_entries` with no filters (returns all non-deleted entries), with `category` filter, with `search` filter, with `status='published'` (returns only published non-deleted entries), with `status='draft'`, with `include_deleted=True` (returns all entries including soft-deleted), soft-delete via `delete_entry`, restore via `restore_entry`, and each status transition (`publish_entry`, `unpublish_entry`, `archive_entry`).
2. THE KB_App SHALL include integration tests for all public endpoints covering: list with no filters (returns only published non-deleted entries), list with `category` filter, list with `search` filter, detail by slug (published non-deleted, expects HTTP 200), detail by slug (not found, expects HTTP 404), detail for a draft entry (expects HTTP 404), and detail for a soft-deleted entry (expects HTTP 404).
3. THE KB_App SHALL include integration tests for all admin CRUD endpoints covering: unauthenticated access (expects HTTP 401), non-Admin authenticated access (expects HTTP 403), list (expects HTTP 200 with all non-deleted entries), create with valid data (expects HTTP 201 with `status='draft'`), create with missing required fields (expects HTTP 400), retrieve by UUID (expects HTTP 200), partial update (expects HTTP 200), soft-delete (expects HTTP 204 with row retained), restore (expects HTTP 200), publish (expects HTTP 200 with `status='published'`), unpublish (expects HTTP 200 with `status='draft'`), and archive (expects HTTP 200 with `status='archived'`).
4. THE KB_App SHALL include a round-trip test that creates a published non-deleted `KnowledgeEntry` with `category='service'`, then calls `KnowledgeService.get_category_as_text('service')`, and asserts the returned string is non-empty and contains the entry's `title`.
5. THE KB_App SHALL include a test that calls `KnowledgeService.get_scoped_knowledge_as_text(company=True, services=True, industries=False, faq=False, contact=False)` with seeded published entries and asserts the output contains the section label `"Company Information:"` and `"Services Provided:"` and does NOT contain `"Industries Served:"`.
6. WHEN `python manage.py test apps.knowledge_base` is executed, THE test runner SHALL complete with 0 failures and 0 errors.

---

### Requirement 16: Backward Compatibility and Rollback

**User Story:** As a project lead, I want the Knowledge Base rollout to be fully reversible, so that any deployment issue can be resolved without data loss or downtime to existing features.

#### Acceptance Criteria

1. THE KB_App migration SHALL be reversible: `python manage.py migrate knowledge_base zero` SHALL remove only the `knowledge_base_knowledgeentry` table without affecting any other table.
2. IF the `apps.knowledge_base` entry is removed from `INSTALLED_APPS` and the URL includes are removed from `core/urls.py`, THEN all existing apps (chatbot, leads, analytics, crm, accounts) SHALL continue to function without errors.
3. THE `KnowledgeLoader` JSON source SHALL remain functional throughout Phase 1. No JSON file SHALL be deleted or modified as part of the KB module implementation.
4. THE KB_App SHALL NOT introduce any new foreign keys pointing from `KnowledgeEntry` to tables in other apps (chatbot, leads, analytics, crm), ensuring zero cross-app migration dependencies.

---

## File-by-File Impact Analysis

The following files are **created** (new files, no existing code touched):

| File | Purpose |
|------|---------|
| `backend/apps/knowledge_base/__init__.py` | App package marker |
| `backend/apps/knowledge_base/apps.py` | AppConfig |
| `backend/apps/knowledge_base/models.py` | `KnowledgeEntry` model |
| `backend/apps/knowledge_base/serializers.py` | List / Detail / Write serializers |
| `backend/apps/knowledge_base/views.py` | Public and admin API views |
| `backend/apps/knowledge_base/urls.py` | URL routing |
| `backend/apps/knowledge_base/admin.py` | Django Admin |
| `backend/apps/knowledge_base/tests.py` | Test suite |
| `backend/apps/knowledge_base/services/__init__.py` | Services package marker |
| `backend/apps/knowledge_base/services/knowledge_service.py` | `KnowledgeService` |
| `backend/apps/knowledge_base/migrations/__init__.py` | Migrations package marker |
| `backend/apps/knowledge_base/migrations/0001_initial.py` | Additive migration |
| `backend/apps/knowledge_base/management/__init__.py` | Management package |
| `backend/apps/knowledge_base/management/commands/__init__.py` | Commands package |
| `backend/apps/knowledge_base/management/commands/seed_knowledge_from_json.py` | Seed command |

The following files are **modified** (minimal, additive changes only):

| File | Change |
|------|--------|
| `backend/core/settings.py` | Add `'apps.knowledge_base'` to `INSTALLED_APPS`; add `KNOWLEDGE_BASE_SOURCE = 'json'` setting |
| `backend/core/urls.py` | Add two `include()` entries for KB public and admin URL prefixes |

The following files are **NOT modified**:

- `apps/chatbot/services/knowledge_loader.py` — untouched
- `apps/chatbot/services/prompt_builder.py` — untouched
- `apps/chatbot/views.py` — untouched
- All existing migration files — untouched
- All JSON knowledge files in `knowledge/` — untouched
