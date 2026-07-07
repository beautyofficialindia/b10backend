# Technical Design: Roles Management

## Overview

REST API module for managing Roles (Django Groups), their permissions, and user memberships. Mounted at `api/v1/admin/roles/`. Fully additive — no new models, reuses `auth.Group`, `auth.Permission`, and `UserAuditLog` from `apps.user_management`.

Key decisions:
- **No custom Role model** — a Role IS a Django Group
- **New Django app `apps/role_management/`** (no models, no migrations)
- **Service layer pattern** (`RoleService`) for all business logic
- **Single `RoleViewSet`** with @action decorators
- **Reuses `UserAuditLog`** from user_management for audit entries
- **Protected roles** (Admin, Sales, Support) cannot be deleted

## Architecture

```
Client → JWT → core/urls.py → apps/role_management/urls.py → RoleViewSet
    → IsAdminUser permission
    → RoleService (business logic)
        → Group ORM
        → Permission ORM
        → UserAuditLog ORM
    → success_response / error_response
    → StandardPageNumberPagination
```

## URL Routing

| Method | Path | Action | Description |
|--------|------|--------|-------------|
| GET | `/api/v1/admin/roles/` | list | List roles (paginated) |
| POST | `/api/v1/admin/roles/` | create | Create role |
| GET | `/api/v1/admin/roles/{id}/` | retrieve | Role detail |
| PATCH | `/api/v1/admin/roles/{id}/` | partial_update | Update role name |
| DELETE | `/api/v1/admin/roles/{id}/` | destroy | Delete role |
| GET | `/api/v1/admin/roles/permissions/` | available_permissions | List all permissions |
| PUT | `/api/v1/admin/roles/{id}/permissions/` | set_permissions | Replace role permissions |
| GET | `/api/v1/admin/roles/{id}/users/` | role_users | List users in role |
| POST | `/api/v1/admin/roles/{id}/users/` | add_users | Add users to role |
| DELETE | `/api/v1/admin/roles/{id}/users/` | remove_users | Remove users from role |

## Serializers

### RoleListSerializer
- id, name, permissions_count (annotated), users_count (annotated)

### RoleDetailSerializer
- id, name, permissions (list of {id, codename, name, content_type}), users_count

### RoleCreateSerializer
- name (required, max_length=150)
- permissions (optional, list of "app_label.codename" strings)

### RoleUpdateSerializer
- name (required, max_length=150)

### PermissionSerializer
- id, codename, name, content_type (string: "app_label.model")

### RoleUserSerializer
- id, username, email, first_name, last_name, is_active

### UserIdsSerializer
- user_ids (list of integers, non-empty)

### PermissionCodenamesSerializer
- permissions (list of "app_label.codename" strings)

## Service Layer — RoleService

```python
class RoleService:
    PROTECTED_ROLES = {'Admin', 'Sales', 'Support'}

    @staticmethod
    def list_roles(search=None, ordering=None) -> QuerySet[Group]

    @staticmethod
    def get_role(role_id: int) -> Group

    @staticmethod
    def create_role(name: str, permissions: list[str], actor: User) -> Group

    @staticmethod
    def update_role(role: Group, name: str, actor: User) -> Group

    @staticmethod
    def delete_role(role: Group, actor: User) -> None

    @staticmethod
    def set_permissions(role: Group, codenames: list[str], actor: User) -> Group

    @staticmethod
    def list_role_users(role: Group, search=None) -> QuerySet[User]

    @staticmethod
    def add_users(role: Group, user_ids: list[int], actor: User) -> dict

    @staticmethod
    def remove_users(role: Group, user_ids: list[int], actor: User) -> dict

    @staticmethod
    def list_available_permissions() -> QuerySet[Permission]

    @staticmethod
    def _validate_permissions(codenames: list[str]) -> list[Permission]

    @staticmethod
    def _create_audit_log(actor, action, description, metadata=None) -> None
```

## Error Handling

| Scenario | Status | Code |
|----------|--------|------|
| Role not found | 404 | `role_not_found` |
| Duplicate name | 400 | `role_name_exists` |
| Protected role deletion | 400 | `role_protected` |
| Invalid permissions | 400 | `invalid_permissions` |
| User not found (in membership) | skip | reason in summary |
| Last superuser protection | 400 | `last_superuser_protection` |

## Audit Actions

| Action Value | Triggered By |
|-------------|-------------|
| `role_created` | POST /roles/ |
| `role_updated` | PATCH /roles/{id}/ |
| `role_deleted` | DELETE /roles/{id}/ |
| `role_permissions_changed` | PUT /roles/{id}/permissions/ |
| `role_users_added` | POST /roles/{id}/users/ |
| `role_users_removed` | DELETE /roles/{id}/users/ |
