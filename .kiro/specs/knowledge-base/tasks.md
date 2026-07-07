# Implementation Plan: Knowledge Base Module

## Overview

This plan implements a database-backed Knowledge Base Django app (`apps.knowledge_base`) with full CRUD, a three-state lifecycle (draft/published/archived), soft-delete with recovery, public read endpoints, admin management endpoints, Django Admin integration, and a seed management command. All changes are additive — existing chatbot services remain untouched.

## Tasks

- [ ] 1. Set up app structure and core model
  - [ ] 1.1 Create the `apps/knowledge_base` app skeleton
    - Create directory structure: `__init__.py`, `apps.py`, `models.py`, `serializers.py`, `views.py`, `urls.py`, `admin.py`, `tests.py`
    - Create `services/__init__.py` and `services/knowledge_service.py` (empty class placeholder)
    - Create `migrations/__init__.py`
    - Create `management/__init__.py`, `management/commands/__init__.py`
    - Implement `KnowledgeBaseConfig` in `apps.py` with `name = 'apps.knowledge_base'` and `default_auto_field = 'django.db.models.BigAutoField'`
    - _Requirements: 1.1, 1.4_

  - [ ] 1.2 Implement the `KnowledgeEntry` model
    - Define all 17 fields (id, category, title, slug, content, structured_data, status, sort_order, created_by, updated_by, published_at, is_deleted, deleted_at, source, created_at, updated_at) with choices for category, status, and source
    - Implement `save()` override: auto-generate slug from title using `slugify`, handle slug collisions with UUID suffix, auto-set `published_at` on first publish, auto-set `deleted_at` on soft-delete
    - Implement `Meta` class with `ordering = ['category', 'sort_order', 'created_at']` and `verbose_name_plural = 'Knowledge Entries'`
    - Implement `__str__` returning `f"[{self.category}] {self.title}"`
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7_

  - [ ] 1.3 Create the initial migration and register app
    - Run `makemigrations knowledge_base` to generate `0001_initial.py`
    - Verify migration dependencies reference only `auth` app
    - Add `'apps.knowledge_base'` to `INSTALLED_APPS` in `core/settings.py`
    - Add `KNOWLEDGE_BASE_SOURCE = env.str('KNOWLEDGE_BASE_SOURCE', default='json')` to `core/settings.py`
    - _Requirements: 3.1, 3.2, 3.3, 12.7_

  - [ ]* 1.4 Write model unit tests
    - Test auto-slug generation from title
    - Test slug collision handling (appends UUID suffix)
    - Test `published_at` auto-stamped on first publish via save
    - Test `deleted_at` auto-stamped on soft-delete via save
    - Test `__str__` format
    - Test Meta ordering
    - _Requirements: 2.2, 2.3, 2.6, 2.7, 2.4, 2.5_

- [ ] 2. Implement KnowledgeService
  - [ ] 2.1 Implement `KnowledgeService` CRUD methods
    - Implement `list_entries(category, search, status, include_deleted, ordering)` with filter semantics: category filter, case-insensitive icontains search on title/content, status filter, is_deleted exclusion by default, ordering validation against allowed values
    - Implement `get_entry(pk, include_deleted)` raising `KnowledgeEntry.DoesNotExist` if not found
    - Implement `create_entry(data, user)` validating required `category` and `title`, setting `created_by`, defaulting `status='draft'`; raise `ValueError` for missing fields
    - Implement `update_entry(entry, data, user)` applying allowed writable fields, setting `updated_by`; raise `ValueError` for unrecognized fields
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.6, 4.8_

  - [ ] 2.2 Implement `KnowledgeService` lifecycle methods
    - Implement `delete_entry(entry, user)` — soft-delete with `is_deleted=True`, `deleted_at=now()`, `updated_by=user`
    - Implement `restore_entry(entry, user)` — clear `is_deleted`, clear `deleted_at`, set `updated_by`
    - Implement `publish_entry(entry, user)` — set `status='published'`, `published_at` only if None, `updated_by`
    - Implement `unpublish_entry(entry, user)` — set `status='draft'`, preserve `published_at`, set `updated_by`
    - Implement `archive_entry(entry, user)` — set `status='archived'`, preserve `published_at`, set `updated_by`
    - _Requirements: 4.1, 4.5_

  - [ ] 2.3 Implement `KnowledgeService` text output methods
    - Implement `get_category_as_text(category)` — return `"\n\n".join(f"{e.title}\n{e.content}")` for published non-deleted entries; empty string if none
    - Implement `get_scoped_knowledge_as_text(company, services, industries, faq, contact)` — produce format-identical output to `KnowledgeLoader.get_scoped_knowledge_as_text` using SECTION_MAP, `json.dumps(data, indent=2)`, omitting empty categories
    - _Requirements: 4.7, 12.3, 12.4, 12.5_

  - [ ]* 2.4 Write property test for Status Visibility Invariant
    - **Property 1: Status Visibility Invariant**
    - For any entry, it should be visible to public queries if and only if `status == 'published' AND is_deleted == False`
    - **Validates: Requirements 6.1, 6.4, 6.5**

  - [ ]* 2.5 Write property test for Published Timestamp Monotonicity
    - **Property 2: Published Timestamp Monotonicity**
    - Once `published_at` is set, no subsequent operation (unpublish, archive, re-publish, soft-delete, restore) clears or overwrites it
    - **Validates: Requirements 2.6, 8.1, 8.2, 8.3**

  - [ ]* 2.6 Write property test for Soft-Delete Recoverability
    - **Property 3: Soft-Delete Recoverability**
    - After soft-delete and restore, all content fields (title, content, status, category, published_at) are preserved unchanged
    - **Validates: Requirements 7.5, 7.6**

  - [ ]* 2.7 Write unit tests for KnowledgeService
    - Test `list_entries` with no filters, category filter, search filter, status filter, include_deleted
    - Test `create_entry` with valid data and with missing required fields
    - Test `update_entry` with valid and invalid fields
    - Test `delete_entry`, `restore_entry`, and all status transitions
    - Test `get_category_as_text` and `get_scoped_knowledge_as_text` output format
    - _Requirements: 4.1–4.8, 15.1_

- [ ] 3. Implement serializers
  - [ ] 3.1 Implement all three serializers
    - Implement `KnowledgeEntryListSerializer` with read-only fields: id, category, title, slug, status, source, sort_order, published_at, created_at, updated_at
    - Implement `KnowledgeEntryDetailSerializer` extending list fields plus content, structured_data, created_by (username string or null), updated_by (username string or null); exclude is_deleted and deleted_at
    - Implement `KnowledgeEntryWriteSerializer` accepting category, title, content (optional), structured_data (optional), sort_order (optional), source (optional default 'manual'); validate category against choices, validate source against choices; support partial=True for PATCH
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

- [ ] 4. Checkpoint - Ensure model, service, and serializers are correct
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 5. Implement public read endpoints
  - [ ] 5.1 Implement public views and URL routing
    - Implement `PublicKnowledgeListView` with `authentication_classes = []`, `permission_classes = []`, `throttle_classes = [AnonRateThrottle]`; accept category, search, page, page_size query params; delegate to `KnowledgeService.list_entries(status='published')` and paginate with `StandardPageNumberPagination`
    - Implement `PublicKnowledgeDetailView` with same auth/permission/throttle config; lookup by slug where `status='published'` and `is_deleted=False`; return 404 with `NOT_FOUND_RESOURCE` for missing/unpublished/deleted
    - Add public URL patterns in `urls.py`: `entries/` and `entries/<slug:slug>/`
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7_

  - [ ]* 5.2 Write integration tests for public endpoints
    - Test GET list returns only published non-deleted entries
    - Test category filter and search filter on list
    - Test detail by slug (published → 200, draft → 404, deleted → 404, non-existent → 404)
    - Test pagination metadata present in response
    - _Requirements: 15.2_

- [ ] 6. Implement admin management endpoints
  - [ ] 6.1 Implement admin CRUD views
    - Implement `AdminKnowledgeListCreateView` with `permission_classes = [IsAdminUser]`; GET returns all non-deleted entries (any status) with category, status, search, ordering filters; POST validates via `KnowledgeEntryWriteSerializer`, delegates to `KnowledgeService.create_entry`, returns 201
    - Implement `AdminKnowledgeDetailView` with GET (by UUID, exclude soft-deleted), PATCH (partial update via `KnowledgeEntryWriteSerializer`), DELETE (soft-delete, return 204)
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.7, 7.8, 7.9, 7.10, 7.11_

  - [ ] 6.2 Implement admin status transition and restore views
    - Implement `AdminKnowledgePublishView` — POST delegates to `KnowledgeService.publish_entry`, returns 200
    - Implement `AdminKnowledgeUnpublishView` — POST delegates to `KnowledgeService.unpublish_entry`, returns 200
    - Implement `AdminKnowledgeArchiveView` — POST delegates to `KnowledgeService.archive_entry`, returns 200
    - Implement `AdminKnowledgeRestoreView` — POST looks up entry with `is_deleted=True`, delegates to `KnowledgeService.restore_entry`, returns 200; 404 if not soft-deleted
    - Add admin URL patterns: `entries/`, `entries/<uuid:pk>/`, `entries/<uuid:pk>/publish/`, `entries/<uuid:pk>/unpublish/`, `entries/<uuid:pk>/archive/`, `entries/<uuid:pk>/restore/`
    - _Requirements: 7.6, 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7_

  - [ ] 6.3 Mount URLs in `core/urls.py`
    - Add `path('api/v1/kb/', include('apps.knowledge_base.urls'))` for public endpoints
    - Add `path('api/v1/admin/kb/', include('apps.knowledge_base.urls'))` for admin endpoints
    - _Requirements: 1.3_

  - [ ]* 6.4 Write integration tests for admin endpoints
    - Test unauthenticated access → 401, non-Admin → 403
    - Test CRUD operations: list (200), create valid (201), create invalid (400), retrieve (200), partial update (200), soft-delete (204)
    - Test status transitions: publish (200), unpublish (200), archive (200)
    - Test restore: soft-deleted → 200, non-deleted → 404
    - Test non-existent UUID → 404
    - _Requirements: 15.3_

  - [ ]* 6.5 Write property test for Audit Trail Completeness
    - **Property 4: Audit Trail Completeness**
    - Every mutation (create, update, status transition, soft-delete, restore) stamps `updated_by` (or `created_by` for create) with the acting user
    - **Validates: Requirements 7.9, 7.10, 8.1, 8.2**

  - [ ]* 6.6 Write property test for Idempotent Status Transitions
    - **Property 9: Idempotent Status Transitions**
    - Calling a status transition on an entry already in the target state saves with updated `updated_by` but does not change state or modify `published_at`
    - **Validates: Requirements 8.4**

- [ ] 7. Checkpoint - Ensure all API endpoints work correctly
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 8. Implement Django Admin integration
  - [ ] 8.1 Implement `KnowledgeAdmin`
    - Register `KnowledgeEntry` with `@admin.register`
    - Configure `list_display`: title, category, slug, status, is_deleted, sort_order, created_at, updated_at
    - Configure `list_filter`: category, status, is_deleted
    - Configure `search_fields`: title, content
    - Configure `readonly_fields`: id, slug, created_at, updated_at, published_at, deleted_at, created_by, updated_by
    - Implement bulk actions: `publish_selected`, `unpublish_selected`, `archive_selected`, `restore_selected`
    - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5, 11.6, 11.7, 11.8, 11.9_

- [ ] 9. Implement seed management command
  - [ ] 9.1 Implement `seed_knowledge_from_json` command
    - Create `management/commands/seed_knowledge_from_json.py`
    - Read JSON files from `BASE_DIR.parent / 'knowledge'`: company.json, services.json, industries.json, faq.json, contact.json
    - Implement `_seed_company`: single entry with `category='company'`, `title='Company Info'`, description → content, full object → structured_data
    - Implement `_seed_services`: map name → title, description → content, technologies → structured_data, `category='service'`
    - Implement `_seed_industries`: map name → title, description → content, `category='industry'`
    - Implement `_seed_faq`: map question → title, answer → content, `category='faq'`
    - Implement `_seed_contact`: single entry with `category='contact'`, `title='Contact Info'`, formatted summary → content, full object → structured_data
    - All entries: `source='json_import'`, `status='draft'`, slug-based deduplication (skip if slug exists)
    - Print summary: `"Seeding complete: {created} created, {skipped} skipped, {failed} failed."`
    - Handle missing files and invalid JSON gracefully (log ERROR, continue)
    - _Requirements: 14.1, 14.2, 14.3, 14.4, 14.5, 14.6, 14.7, 14.8, 14.9, 14.10_

  - [ ]* 9.2 Write tests for seed command
    - Test run on empty DB creates entries with `source='json_import'`
    - Test re-run skips duplicates (slug exists)
    - Test missing JSON file logs ERROR and continues
    - Test summary output format
    - _Requirements: 15.1, 14.8, 14.9, 14.10_

  - [ ]* 9.3 Write property test for Source Traceability
    - **Property 7: Source Traceability**
    - All entries created by `seed_knowledge_from_json` have `source == 'json_import'`; entries created via admin API without explicit source have `source == 'manual'`
    - **Validates: Requirements 14.3, 14.4, 14.5, 14.6, 14.7**

- [ ] 10. Implement chatbot compatibility verification
  - [ ] 10.1 Write chatbot compatibility test
    - Seed published entries for company and service categories
    - Call `KnowledgeService.get_scoped_knowledge_as_text(company=True, services=True, industries=False, faq=False, contact=False)`
    - Assert output contains `"Company Information:"` and `"Services Provided:"`
    - Assert output does NOT contain `"Industries Served:"`, `"Frequently Asked Questions (FAQ):"`, or `"Contact Information:"`
    - Assert JSON formatting uses `indent=2`
    - _Requirements: 12.3, 12.4, 12.5, 15.4, 15.5_

  - [ ]* 10.2 Write property test for Format Identity
    - **Property 5: Format Identity (KnowledgeLoader Compatibility)**
    - `KnowledgeService.get_scoped_knowledge_as_text` produces output with same section labels, same JSON formatting, same section ordering, and empty categories omitted identically
    - **Validates: Requirements 12.3, 12.4, 12.5**

  - [ ]* 10.3 Write property test for Slug Uniqueness
    - **Property 8: Slug Uniqueness**
    - For any two distinct entries, their slugs are never equal; the auto-generation algorithm guarantees uniqueness via collision detection and UUID suffix
    - **Validates: Requirements 2.2, 2.3**

- [ ] 11. Final checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties from the design document
- Unit tests validate specific examples and edge cases
- All changes are additive — no existing chatbot, leads, analytics, or CRM code is modified
- The `KnowledgeLoader` and `PromptBuilder` remain untouched (Phase 1 constraint)
- The `KNOWLEDGE_BASE_SOURCE` setting defaults to `'json'` ensuring zero chatbot impact

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["1.1"] },
    { "id": 1, "tasks": ["1.2"] },
    { "id": 2, "tasks": ["1.3", "1.4"] },
    { "id": 3, "tasks": ["2.1", "3.1"] },
    { "id": 4, "tasks": ["2.2", "2.3"] },
    { "id": 5, "tasks": ["2.4", "2.5", "2.6", "2.7"] },
    { "id": 6, "tasks": ["5.1", "6.1"] },
    { "id": 7, "tasks": ["5.2", "6.2", "6.3"] },
    { "id": 8, "tasks": ["6.4", "6.5", "6.6"] },
    { "id": 9, "tasks": ["8.1"] },
    { "id": 10, "tasks": ["9.1"] },
    { "id": 11, "tasks": ["9.2", "9.3", "10.1"] },
    { "id": 12, "tasks": ["10.2", "10.3"] }
  ]
}
```
