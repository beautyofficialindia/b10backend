# Implementation Plan: Roles Management

## Overview

REST API module for managing Roles (Django Groups), permissions, and user memberships. New app `apps/role_management/` with no models (reuses existing). Mounted at `api/v1/admin/roles/`.

## Tasks

- [ ] 1. Set up app structure and URL mount
  - [ ] 1.1 Create `apps/role_management/` app (no models, no migrations needed)
    - `__init__.py`, `apps.py`, `views.py`, `urls.py`, `serializers.py`
    - `services/__init__.py`, `services/role_service.py`
    - `tests/__init__.py`, `tests/conftest.py`
    - Register in INSTALLED_APPS, mount URL in core/urls.py
    - _Requirements: 13.1, 13.2_

- [ ] 2. Implement serializers
  - [ ] 2.1 Implement all serializers
    - RoleListSerializer, RoleDetailSerializer, RoleCreateSerializer, RoleUpdateSerializer
    - PermissionSerializer, RoleUserSerializer, UserIdsSerializer, PermissionCodenamesSerializer
    - _Requirements: 1.4, 3.1, 9.2, 11.1_

- [ ] 3. Implement the RoleService
  - [ ] 3.1 list_roles, get_role, create_role, update_role, delete_role
  - [ ] 3.2 set_permissions, _validate_permissions
  - [ ] 3.3 list_role_users, add_users, remove_users
  - [ ] 3.4 list_available_permissions, _create_audit_log
  - _Requirements: 1-9, 12_

- [ ] 4. Implement the RoleViewSet
  - [ ] 4.1 CRUD actions + custom @action endpoints
    - list, create, retrieve, partial_update, destroy
    - available_permissions, set_permissions, role_users, add_users, remove_users
    - _Requirements: 1-11_

- [ ] 5. Implement tests
  - [ ] 5.1 Permission tests (401, 403, success)
  - [ ] 5.2 CRUD tests (list, create, retrieve, update, delete, protected roles)
  - [ ] 5.3 Permission management tests
  - [ ] 5.4 User membership tests
  - [ ] 5.5 Audit log tests
  - _Requirements: 10, 12, 16_

- [ ] 6. Final checkpoint
  - Verify all tests pass, no regressions, clean working tree

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["1.1"] },
    { "id": 1, "tasks": ["2.1"] },
    { "id": 2, "tasks": ["3.1", "3.2", "3.3", "3.4"] },
    { "id": 3, "tasks": ["4.1"] },
    { "id": 4, "tasks": ["5.1", "5.2", "5.3", "5.4", "5.5"] },
    { "id": 5, "tasks": ["6"] }
  ]
}
```
