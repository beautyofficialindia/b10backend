# Requirements Document

## Introduction

This module provides administrative management of Roles (Django Groups) and their associated Permissions within the B10 IT Solution platform. It enables Admin group members to list, create, update, delete roles, manage permission assignments, and manage user-role memberships. The module operates exclusively through REST API endpoints mounted at `api/v1/admin/roles/`, reuses Django's built-in Group and Permission models, and follows the existing service layer architecture. It does NOT introduce a custom Role model — a "Role" is simply a Django Group.

## Glossary

- **Role**: A Django `auth.Group` instance representing a named set of permissions
- **Permission**: A Django `auth.Permission` instance (content_type + codename)
- **Role_Management_API**: The set of REST API endpoints under `api/v1/admin/roles/`
- **Admin_User**: An authenticated user belonging to the Django 'Admin' group
- **Protected_Role**: A system-critical role (Admin, Sales, Support) that cannot be deleted
- **RoleService**: The service layer component encapsulating business logic for role management
- **RoleAuditLog**: Audit entries recorded in the existing `UserAuditLog` model with role-specific action types

## Requirements

### Requirement 1: List Roles

**User Story:** As an Admin_User, I want to retrieve a paginated list of Roles, so that I can view all available roles in the system.

#### Acceptance Criteria

1. WHEN a GET request is made to `api/v1/admin/roles/`, THE Role_Management_API SHALL return a paginated list of Roles using the StandardPageNumberPagination
2. WHEN a `search` query parameter is provided, THE Role_Management_API SHALL filter Roles where name matches the search term using case-insensitive partial matching
3. WHEN an `ordering` query parameter is provided, THE Role_Management_API SHALL sort results by the specified field chosen from: name, id (prefixed with `-` for descending)
4. THE Role_Management_API SHALL return each Role with fields: id, name, permissions_count (integer count of assigned permissions), users_count (integer count of users in the role)

### Requirement 2: Create Role

**User Story:** As an Admin_User, I want to create new Roles, so that I can define new permission sets for staff members.

#### Acceptance Criteria

1. WHEN a POST request is made to `api/v1/admin/roles/` with a valid name, THE Role_Management_API SHALL create a new Group and return the role detail
2. WHEN a POST request is made with a name that already exists (case-insensitive check), THE Role_Management_API SHALL return a 400 error
3. WHEN a `permissions` field is provided as a list of permission codenames (format: `app_label.codename`), THE Role_Management_API SHALL assign those permissions to the role
4. WHEN an invalid permission codename is provided, THE Role_Management_API SHALL return a 400 error listing all invalid codenames
5. THE Role_Management_API SHALL create an audit log entry for role creation

### Requirement 3: Retrieve Role Detail

**User Story:** As an Admin_User, I want to view the full details of a specific Role, so that I can inspect its permissions and membership.

#### Acceptance Criteria

1. WHEN a GET request is made to `api/v1/admin/roles/{id}/`, THE Role_Management_API SHALL return the role with fields: id, name, permissions (list of permission objects with id, codename, name, content_type), users_count
2. WHEN a GET request is made with a non-existent id, THE Role_Management_API SHALL return a 404 error

### Requirement 4: Update Role

**User Story:** As an Admin_User, I want to update Role names, so that I can maintain clear role descriptions.

#### Acceptance Criteria

1. WHEN a PATCH request is made to `api/v1/admin/roles/{id}/` with a valid name, THE Role_Management_API SHALL update the role name and return the updated detail
2. WHEN a PATCH request provides a name that already belongs to another Role (case-insensitive), THE Role_Management_API SHALL return a 400 error
3. WHEN a PATCH request is made with a non-existent id, THE Role_Management_API SHALL return a 404 error
4. THE Role_Management_API SHALL create an audit log entry for role update

### Requirement 5: Delete Role

**User Story:** As an Admin_User, I want to delete Roles that are no longer needed, so that I can keep the system clean.

#### Acceptance Criteria

1. WHEN a DELETE request is made to `api/v1/admin/roles/{id}/`, THE Role_Management_API SHALL delete the Group and return a 204 response
2. WHEN a DELETE request targets a Protected_Role (Admin, Sales, Support), THE Role_Management_API SHALL return a 400 error indicating the role is protected
3. WHEN a DELETE request is made with a non-existent id, THE Role_Management_API SHALL return a 404 error
4. THE Role_Management_API SHALL create an audit log entry for role deletion

### Requirement 6: Manage Role Permissions

**User Story:** As an Admin_User, I want to assign and remove permissions from a Role, so that I can control what each role can do.

#### Acceptance Criteria

1. WHEN a PUT request is made to `api/v1/admin/roles/{id}/permissions/` with a list of permission codenames, THE RoleService SHALL replace all permissions on the role with the specified set
2. WHEN an invalid permission codename is provided, THE Role_Management_API SHALL return a 400 error listing all invalid codenames
3. WHEN an empty list is provided, THE RoleService SHALL remove all permissions from the role
4. WHEN a non-existent role id is provided, THE Role_Management_API SHALL return a 404 error
5. THE Role_Management_API SHALL create an audit log entry for permission changes

### Requirement 7: List Users in a Role

**User Story:** As an Admin_User, I want to see which users belong to a specific Role, so that I can understand role membership.

#### Acceptance Criteria

1. WHEN a GET request is made to `api/v1/admin/roles/{id}/users/`, THE Role_Management_API SHALL return a paginated list of users in the role
2. WHEN a `search` query parameter is provided, THE Role_Management_API SHALL filter users by username, email, first_name, or last_name using case-insensitive partial matching
3. THE Role_Management_API SHALL return each user with fields: id, username, email, first_name, last_name, is_active
4. WHEN a non-existent role id is provided, THE Role_Management_API SHALL return a 404 error

### Requirement 8: Manage Role Membership

**User Story:** As an Admin_User, I want to assign and remove users from a Role, so that I can control access.

#### Acceptance Criteria

1. WHEN a POST request is made to `api/v1/admin/roles/{id}/users/` with a list of user IDs, THE RoleService SHALL add those users to the role and return a summary
2. WHEN a DELETE request is made to `api/v1/admin/roles/{id}/users/` with a list of user IDs, THE RoleService SHALL remove those users from the role and return a summary
3. WHEN a user ID does not exist, THE RoleService SHALL skip it and include it in the skipped list with reason "user not found"
4. WHEN removing the last Admin_User from the 'Admin' role where that user is the last active superuser, THE RoleService SHALL reject the operation with a 400 error
5. WHEN a non-existent role id is provided, THE Role_Management_API SHALL return a 404 error
6. THE Role_Management_API SHALL create an audit log entry for membership changes

### Requirement 9: List Available Permissions

**User Story:** As an Admin_User, I want to see all available permissions, so that I can choose which ones to assign to roles.

#### Acceptance Criteria

1. WHEN a GET request is made to `api/v1/admin/roles/permissions/`, THE Role_Management_API SHALL return a list of all available Django permissions grouped by content_type app_label
2. THE Role_Management_API SHALL return each permission with fields: id, codename, name, content_type (app_label + model)

### Requirement 10: Authentication and Authorization

**User Story:** As a system operator, I want role management endpoints protected by authentication and role checks.

#### Acceptance Criteria

1. THE Role_Management_API SHALL require a valid JWT access token for all endpoints
2. THE Role_Management_API SHALL require the requesting user to be a member of the 'Admin' group
3. WHEN a request is made without a valid JWT token, THE Role_Management_API SHALL return a 401 error
4. WHEN a request is made by a non-Admin user, THE Role_Management_API SHALL return a 403 error

### Requirement 11: API Response Format

**User Story:** As a frontend developer, I want consistent API response formatting.

#### Acceptance Criteria

1. THE Role_Management_API SHALL wrap all successful responses using `success_response()` from `common/responses.py`
2. THE Role_Management_API SHALL wrap all error responses using `error_response()` from `common/responses.py`
3. THE Role_Management_API SHALL use `StandardPageNumberPagination` from `common/pagination.py` for paginated responses
4. THE Role_Management_API SHALL include Swagger/OpenAPI documentation for all endpoints

### Requirement 12: Audit Logging

**User Story:** As an Admin_User, I want all state-changing operations on Roles to be logged.

#### Acceptance Criteria

1. WHEN a state-changing operation (create, update, delete, permissions change, membership change) is performed, THE RoleService SHALL create a UserAuditLog record
2. THE audit record SHALL capture: action type, target info (role name/id), acting admin user ID, timestamp, and description
3. Action types: `role_created`, `role_updated`, `role_deleted`, `role_permissions_changed`, `role_users_added`, `role_users_removed`

### Requirement 13: Backward Compatibility

**User Story:** As a system operator, I want the role management module to be fully additive.

#### Acceptance Criteria

1. THE Role_Management_API SHALL NOT modify existing apps or endpoints
2. THE Role_Management_API SHALL mount exclusively under `api/v1/admin/roles/`
3. THE Role_Management_API SHALL NOT introduce new models (reuses UserAuditLog from user_management)
4. THE Role_Management_API SHALL NOT modify any existing migration files
