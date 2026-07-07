# Implementation Plan: Users Management

## Overview

Implement a REST API module for managing backend/internal users (CRUD, activation/deactivation, bulk operations, password reset, audit logging) mounted at `api/v1/admin/users/`. The module is a new Django app `apps/user_management/` that reuses Django's built-in User, Group, and Permission models. It follows the existing service layer pattern with a single `UserViewSet` (ModelViewSet + @action decorators) and a `UserService` class encapsulating business logic.

## Tasks

- [ ] 1. Set up app structure and data model
  - [ ] 1.1 Create the `apps/user_management/` Django app with package structure
    - Create `apps/user_management/__init__.py`, `apps.py`, `admin.py`, `models.py`, `serializers.py`, `views.py`, `urls.py`
    - Create `apps/user_management/services/__init__.py` and `services/user_service.py`
    - Create `apps/user_management/migrations/__init__.py`
    - Create `apps/user_management/tests/__init__.py` and `tests/conftest.py`
    - Configure `apps.py` with `name = 'apps.user_management'` and `verbose_name = 'User Management'`
    - _Requirements: 17.7_

  - [ ] 1.2 Implement the `UserAuditLog` model and generate migration
    - Define `UserAuditLog` model with fields: id (BigAutoField), actor (FK to User, SET_NULL, nullable), target_user (FK to User, SET_NULL, nullable), action (CharField max_length=50), description (TextField), metadata (JSONField default=dict), created_at (DateTimeField auto_now_add)
    - Add Meta: `app_label = 'user_management'`, `ordering = ['-created_at']`
    - Add indexes on (target_user, -created_at), (actor, -created_at), (action), (-created_at)
    - Register `UserAuditLog` in `admin.py`
    - Run `makemigrations` to generate `0001_initial.py`
    - _Requirements: 12.1, 12.2, 12.3_

  - [ ] 1.3 Register the app and mount URL configuration
    - Add `'apps.user_management'` to `INSTALLED_APPS` in settings
    - Add `path('api/v1/admin/users/', include('apps.user_management.urls'))` to `core/urls.py`
    - Configure `urls.py` with DRF `DefaultRouter` registering `UserViewSet` with basename `'user'`
    - _Requirements: 17.4, 17.7_

- [ ] 2. Implement serializers
  - [ ] 2.1 Implement all DRF serializers
    - `UserListSerializer`: id, username, email, first_name, last_name, is_active, is_staff, is_superuser, groups (SerializerMethodField → list of group name strings), date_joined, last_login
    - `UserDetailSerializer` (extends UserListSerializer): adds permissions field (SerializerMethodField → `user.get_all_permissions()` as list of strings)
    - `UserCreateSerializer`: username (max=150), email (required), first_name, last_name, password (write_only), groups (ListField of CharField, default=[]), is_active (default=True), is_staff (default=True), is_superuser (default=False)
    - `UserUpdateSerializer`: first_name, last_name, email, groups (ListField of CharField), is_active, is_staff, is_superuser. Reject `username` with 400 via validate method
    - `PasswordResetSerializer`: password (write_only, required)
    - `BulkActionSerializer`: user_ids (ListField of IntegerField, required, non-empty)
    - `AuditLogSerializer`: id, actor, actor_username (SerializerMethodField), target_user, action, description, metadata, created_at
    - _Requirements: 1.10, 2.1, 4.1, 4.11, 5.2, 5.3, 10.2, 14.5, 14.6_

- [ ] 3. Implement the UserService
  - [ ] 3.1 Implement `UserService.list_users()` with filtering, search, and ordering
    - Accept parameters: search, ordering, is_active, is_staff, is_superuser, group, date_joined_after/before, last_login_after/before
    - Apply case-insensitive partial match search across username, email, first_name, last_name with OR logic using Q objects
    - Apply boolean filters when provided
    - Apply group membership filter via `groups__name`
    - Apply date range filters (gte/lte)
    - Apply ordering with validation against allowed fields: username, email, date_joined, last_login, first_name, last_name
    - Use `.prefetch_related("groups")` on queryset
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9_

  - [ ] 3.2 Implement `UserService.create_user()` with validation
    - Validate password against AUTH_PASSWORD_VALIDATORS using `django.contrib.auth.password_validation.validate_password()`
    - Validate username uniqueness (case-insensitive via `User.objects.filter(username__iexact=...)`)
    - Validate email uniqueness (case-insensitive via `User.objects.filter(email__iexact=...)`)
    - Validate group names exist via `_validate_group_names()` helper
    - Normalize email to lowercase
    - Create user with `set_password()` for hashing
    - Assign groups via `user.groups.set()`
    - Create audit log entry with action `user_created`
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8, 4.9, 4.10, 4.12_

  - [ ] 3.3 Implement `UserService.update_user()` with protections
    - Reject username field if present in data
    - Validate email uniqueness (case-insensitive, excluding current user)
    - Validate group names exist if groups field provided
    - Enforce last-active-superuser protection (cannot set is_superuser=False, cannot remove from Admin group)
    - Normalize email to lowercase
    - Replace group memberships via `user.groups.set()`
    - Create audit log entry with action `user_updated` (include old/new values in metadata)
    - If groups changed, also log `groups_changed`
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 5.8, 5.10, 5.11_

  - [ ] 3.4 Implement `UserService.activate_user()` and `UserService.deactivate_user()`
    - `activate_user`: set is_active=True, save, create audit log with action `user_activated`
    - `deactivate_user`: reject self-deactivation, enforce last-active-superuser protection, set is_active=False, save, create audit log with action `user_deactivated`
    - _Requirements: 6.1, 7.1, 7.2, 7.3, 7.5_

  - [ ] 3.5 Implement `UserService.reset_password()`
    - Validate password against AUTH_PASSWORD_VALIDATORS
    - Set password via `user.set_password(new_password)`
    - Save with `update_fields=["password"]` to avoid race conditions
    - Create audit log with action `password_reset` (no old/new values for security)
    - _Requirements: 10.1, 10.4_

  - [ ] 3.6 Implement `UserService.bulk_activate()` and `UserService.bulk_deactivate()`
    - Wrap in `transaction.atomic()`
    - `bulk_activate`: iterate IDs, skip non-existent ("user not found"), skip already active ("already active"), activate rest, create audit log per activation with action `bulk_activated`
    - `bulk_deactivate`: iterate IDs, skip non-existent ("user not found"), skip already inactive ("already inactive"), skip self ("cannot deactivate yourself"), skip last active superuser ("cannot deactivate last active superuser"), deactivate rest, create audit log per deactivation with action `bulk_deactivated`
    - Return summary dict: `{activated_count/deactivated_count, skipped: [{id, reason}]}`
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 9.1, 9.2, 9.3, 9.4, 9.5, 9.6_

  - [ ] 3.7 Implement `UserService.get_audit_log()` and helper methods
    - `get_audit_log(user_id)`: return `UserAuditLog.objects.filter(target_user_id=user_id).order_by('-created_at')`
    - `get_user(user_id)`: fetch user with prefetch_related or raise DoesNotExist
    - `_is_last_active_superuser(user)`: count users with is_superuser=True AND is_active=True, return True if count==1 and user is that one
    - `_validate_group_names(group_names)`: validate all exist, raise ValidationError listing invalid ones
    - `_create_audit_log(actor, target_user, action, description, metadata)`: create UserAuditLog record
    - _Requirements: 12.1, 12.2, 12.4, 15.5_

- [ ] 4. Implement the UserViewSet
  - [ ] 4.1 Implement `UserViewSet` with CRUD actions and custom endpoints
    - Configure `authentication_classes = [JWTAuthentication]`, `permission_classes = [IsAdminUser]`
    - Configure `pagination_class = StandardPageNumberPagination`
    - Configure `http_method_names = ['get', 'post', 'patch', 'head', 'options']`
    - Implement `get_serializer_class()` returning correct serializer per action
    - Implement `get_queryset()` with `prefetch_related("groups")`
    - Implement `list()`: parse query params, call `UserService.list_users()`, paginate, return `success_response()`
    - Implement `create()`: validate via serializer, call `UserService.create_user()`, return 201 with `success_response()`
    - Implement `retrieve()`: call `UserService.get_user()`, handle DoesNotExist → 404, serialize with Detail, return `success_response()`
    - Implement `partial_update()`: validate via serializer, call `UserService.update_user()`, return `success_response()`
    - Implement `me()` action (detail=False, GET): serialize request.user with DetailSerializer, return `success_response()`
    - Implement `activate()` action (detail=True, POST): fetch user or 404, call service, return `success_response()`
    - Implement `deactivate()` action (detail=True, POST): fetch user or 404, call service, handle ValidationError → 400, return `success_response()`
    - Implement `reset_password()` action (detail=True, POST): validate serializer, fetch user or 404, call service, handle ValidationError → 400, return `success_response()`
    - Implement `audit_log()` action (detail=True, GET): fetch user or 404, call service, paginate, return `success_response()`
    - Implement `bulk_activate()` action (detail=False, POST): validate serializer, call service, return `success_response()`
    - Implement `bulk_deactivate()` action (detail=False, POST): validate serializer, call service, return `success_response()`
    - Use `error_response()` for all error cases with appropriate HTTP status codes and error codes
    - _Requirements: 1.1, 2.1, 2.2, 3.1, 3.2, 4.1, 5.1, 5.9, 6.1, 6.2, 7.1, 7.4, 8.1, 9.1, 10.1, 10.3, 12.4, 12.5, 13.1, 13.2, 13.3, 13.4, 14.1, 14.2, 14.3_

- [ ] 5. Checkpoint - Ensure core implementation works
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 6. Implement test fixtures and permission tests
  - [ ] 6.1 Create test fixtures in `conftest.py`
    - Create fixtures: admin_user (in Admin group), regular_user (authenticated but not Admin), unauthenticated client, sample groups, sample users with various states
    - Set up API client with JWT authentication helper
    - _Requirements: 16.1_

  - [ ] 6.2 Implement authentication and authorization tests
    - Test 401 for requests without JWT token
    - Test 403 for authenticated user not in Admin group
    - Test successful access for Admin group member
    - _Requirements: 13.1, 13.2, 13.3, 13.4, 16.1_

- [ ] 7. Implement list endpoint tests
  - [ ] 7.1 Implement pagination and list tests
    - Test default pagination returns page_size=20
    - Test pagination meta includes page, page_size, total_count, total_pages
    - Test custom page_size parameter
    - Test List_Serializer returns correct fields (id, username, email, first_name, last_name, is_active, is_staff, is_superuser, groups, date_joined, last_login)
    - _Requirements: 1.1, 1.10, 14.3, 16.2_

  - [ ] 7.2 Implement search and filter tests
    - Test search filters by username, email, first_name, last_name with case-insensitive partial matching
    - Test is_active, is_staff, is_superuser boolean filters
    - Test group filter returns only users in specified group
    - Test date_joined_after/before and last_login_after/before filters
    - Test ordering by each allowed field in ascending and descending
    - _Requirements: 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 16.3, 16.4, 16.5_

  - [ ]* 7.3 Write property tests for list filtering (Properties 1-5)
    - **Property 1: Search Filter Correctness** — Generate random users and search terms, assert all results contain term in at least one searchable field
    - **Property 2: Ordering Correctness** — Generate random users and valid ordering fields, assert results are sorted correctly
    - **Property 3: Boolean Filter Correctness** — Generate random users with varied boolean fields, assert all results match filter value
    - **Property 4: Group Filter Correctness** — Generate random users in random groups, assert all results belong to specified group
    - **Property 5: Date Range Filter Correctness** — Generate random users with varied dates, assert all results within range
    - **Validates: Requirements 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9**

- [ ] 8. Implement CRUD and detail tests
  - [ ] 8.1 Implement detail, create, and update tests
    - Test retrieve returns Detail_Serializer fields including permissions
    - Test retrieve returns 404 for non-existent ID
    - Test `/me/` endpoint returns current admin's profile
    - Test create with valid data returns 201 with Detail_Serializer
    - Test create with duplicate username returns 400
    - Test create with duplicate email returns 400
    - Test create with invalid group name returns 400 listing invalid names
    - Test create with empty groups creates user with no groups
    - Test create defaults is_active=True
    - Test update with valid data returns updated user
    - Test update rejects username modification with 400
    - Test update with non-existent ID returns 404
    - Test email normalization on create and update
    - _Requirements: 2.1, 2.2, 3.1, 4.1, 4.5, 4.6, 4.7, 4.8, 4.10, 5.1, 5.3, 5.9, 5.10, 5.11, 16.6_

  - [ ]* 8.2 Write property tests for creation and data integrity (Properties 7-13)
    - **Property 7: User Creation Round-Trip** — Generate valid creation payloads, assert stored data matches input
    - **Property 8: Username Uniqueness Invariant** — Generate usernames with case variations, assert duplicates rejected
    - **Property 9: Email Uniqueness Invariant** — Generate emails with case variations, assert duplicates rejected
    - **Property 10: Email Normalization Invariant** — Generate emails with mixed case, assert stored is lowercase
    - **Property 11: Invalid Group Atomicity** — Generate mix of valid/invalid group names, assert entire request rejected
    - **Property 12: Password Never in Response** — Generate valid operations, assert no password key in any response
    - **Property 13: Group Replacement on Update** — Generate user with groups A, update with groups B, assert final == B
    - **Validates: Requirements 4.1, 4.2, 4.4, 4.6, 4.7, 4.8, 4.9, 4.11, 4.12, 5.4, 5.5, 5.10, 5.11, 10.2, 11.2, 11.6, 11.8, 14.6**

- [ ] 9. Implement activation, deactivation, and protection tests
  - [ ] 9.1 Implement activate/deactivate and protection tests
    - Test activate sets is_active=True
    - Test activate returns 404 for non-existent user
    - Test deactivate sets is_active=False, record persists
    - Test deactivate returns 400 for self-deactivation
    - Test deactivate returns 400 for last active superuser
    - Test deactivate returns 404 for non-existent user
    - Test update rejects is_superuser=False on last active superuser
    - Test update rejects removing Admin group from last active superuser
    - _Requirements: 6.1, 6.2, 7.1, 7.2, 7.3, 7.4, 7.5, 15.1, 15.2, 15.3, 16.7, 16.8_

  - [ ]* 9.2 Write property tests for activation/deactivation (Properties 14-16)
    - **Property 14: Activate/Deactivate State Change** — Generate random users, assert is_active changes correctly and record persists
    - **Property 15: Self-Deactivation Prevention** — Generate admin deactivating self, assert 400 or skipped
    - **Property 16: Last Active Superuser Protection** — Generate single active superuser, assert all protection-triggering ops rejected/skipped
    - **Validates: Requirements 5.7, 5.8, 6.1, 7.1, 7.2, 7.3, 7.5, 9.3, 9.4, 15.1, 15.2, 15.3, 15.4, 15.5**

- [ ] 10. Implement bulk operations and password reset tests
  - [ ] 10.1 Implement bulk activate/deactivate and password reset tests
    - Test bulk activate succeeds for valid IDs
    - Test bulk activate skips non-existent IDs with reason
    - Test bulk activate skips already active users with reason
    - Test bulk deactivate succeeds for valid IDs
    - Test bulk deactivate skips self with reason
    - Test bulk deactivate skips last active superuser with reason
    - Test bulk deactivate skips non-existent and already inactive with reasons
    - Test bulk summary counts are correct (count + skipped == input length)
    - Test password reset with valid password succeeds
    - Test password reset with invalid password returns 400 with details
    - Test password reset returns 404 for non-existent user
    - Test password is not included in any response
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 9.1, 9.2, 9.3, 9.4, 9.5, 9.6, 10.1, 10.2, 10.3, 10.4, 16.9, 16.10_

  - [ ]* 10.2 Write property tests for bulk ops and password (Properties 17, 20)
    - **Property 17: Bulk Operation Summary Correctness** — Generate random ID lists, assert counts add up and all IDs accounted for
    - **Property 20: Password Validation Enforcement** — Generate random invalid passwords, assert rejection with details
    - **Validates: Requirements 4.3, 8.1, 8.2, 9.1, 9.2, 10.4**

- [ ] 11. Implement audit logging tests
  - [ ] 11.1 Implement audit log endpoint and logging tests
    - Test audit log entries are created for all state-changing operations (create, update, activate, deactivate, bulk-activate, bulk-deactivate, password reset)
    - Test audit log entries have all required fields (action, target_user, actor, created_at, description)
    - Test GET audit-log endpoint returns paginated entries ordered by timestamp desc
    - Test GET audit-log endpoint returns 404 for non-existent user
    - _Requirements: 12.1, 12.2, 12.4, 12.5, 16.11_

  - [ ]* 11.2 Write property tests for audit logging (Properties 18, 19)
    - **Property 18: Audit Log Invariant** — Generate random state-changing operations, assert audit record created with all required fields
    - **Property 19: Response Envelope Format** — Generate any API call, assert response structure matches envelope format
    - **Validates: Requirements 12.1, 12.2, 14.1, 14.2**

  - [ ]* 11.3 Write property test for serializer completeness (Property 6)
    - **Property 6: Serializer Field Completeness** — Generate random users, assert Detail and List serializers contain all expected fields
    - **Validates: Requirements 1.10, 2.1, 14.5**

- [ ] 12. Final checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties using Hypothesis library
- Unit tests validate specific examples and edge cases using pytest + Django test client
- The implementation is fully additive — no existing code is modified except adding to INSTALLED_APPS and core/urls.py
- All responses use `success_response()` / `error_response()` from `common/responses.py`
- Pagination uses `StandardPageNumberPagination` from `common/pagination.py`

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["1.1"] },
    { "id": 1, "tasks": ["1.2"] },
    { "id": 2, "tasks": ["1.3", "2.1"] },
    { "id": 3, "tasks": ["3.1", "3.2", "3.5", "3.7"] },
    { "id": 4, "tasks": ["3.3", "3.4", "3.6"] },
    { "id": 5, "tasks": ["4.1"] },
    { "id": 6, "tasks": ["6.1"] },
    { "id": 7, "tasks": ["6.2", "7.1", "7.2", "8.1", "9.1", "10.1", "11.1"] },
    { "id": 8, "tasks": ["7.3", "8.2", "9.2", "10.2", "11.2", "11.3"] }
  ]
}
```
