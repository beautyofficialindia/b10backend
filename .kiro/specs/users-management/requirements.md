# Requirements Document

## Introduction

This module provides administrative management of backend/internal users (administrators, staff members) within the B10 IT Solution platform. It enables Admin group members to list, create, update, activate, deactivate, bulk-activate/deactivate, reset passwords, and view audit logs for internal users. The module operates exclusively through REST API endpoints mounted at `api/v1/admin/users/`, uses Django's built-in User, Group, and Permission models (integer primary key), and follows the existing service layer architecture. It does NOT manage customer portal users or chatbot end users.

## Glossary

- **User_Management_API**: The set of REST API endpoints under `api/v1/admin/users/` that provide CRUD, bulk operations, and administrative operations for backend users
- **Admin_User**: An authenticated user who belongs to the Django 'Admin' group and has permission to manage other backend users
- **Backend_User**: A Django User model instance (integer PK) representing an internal staff member (administrator, sales, support, or other internal role)
- **User_Service**: The service layer component responsible for encapsulating business logic for user management operations
- **Pagination_System**: The `StandardPageNumberPagination` class from `common/pagination.py` providing page-based result sets with page_size=20, max=100, and standard pagination meta (page, page_size, total_count, total_pages)
- **Response_Wrapper**: The `success_response()` and `error_response()` helper functions from `common/responses.py` used to standardize API response format
- **Active_Superuser**: A Backend_User with `is_superuser=True` and `is_active=True`
- **UserAuditLog**: A database model in the user management app that records all state-changing operations on Backend_Users, capturing action type, target user ID, acting admin user ID, timestamp, and description
- **List_Serializer**: The serializer used for list responses containing fields: id, username, email, first_name, last_name, is_active, is_staff, is_superuser, groups (list of group name strings), date_joined, last_login
- **Detail_Serializer**: The serializer used for detail/create/update responses containing all List_Serializer fields PLUS permissions (list of permission codename strings)

## Requirements

### Requirement 1: List Backend Users

**User Story:** As an Admin_User, I want to retrieve a paginated list of Backend_Users, so that I can view and manage all internal staff accounts.

#### Acceptance Criteria

1. WHEN a GET request is made to `api/v1/admin/users/`, THE User_Management_API SHALL return a paginated list of Backend_Users using the Pagination_System
2. WHEN a `search` query parameter is provided, THE User_Management_API SHALL filter Backend_Users where username, email, first_name, or last_name matches the search term using case-insensitive partial matching with OR logic
3. WHEN an `ordering` query parameter is provided, THE User_Management_API SHALL sort results by the specified field chosen from: username, email, date_joined, last_login, first_name, last_name (prefixed with `-` for descending)
4. WHEN an `is_active` filter parameter is provided, THE User_Management_API SHALL return only Backend_Users whose is_active field matches the provided boolean value
5. WHEN an `is_staff` filter parameter is provided, THE User_Management_API SHALL return only Backend_Users whose is_staff field matches the provided boolean value
6. WHEN an `is_superuser` filter parameter is provided, THE User_Management_API SHALL return only Backend_Users whose is_superuser field matches the provided boolean value
7. WHEN a `group` filter parameter is provided, THE User_Management_API SHALL return only Backend_Users who belong to the group with the specified name
8. WHEN `date_joined_after` and/or `date_joined_before` filter parameters are provided, THE User_Management_API SHALL return only Backend_Users whose date_joined falls within the specified date range
9. WHEN `last_login_after` and/or `last_login_before` filter parameters are provided, THE User_Management_API SHALL return only Backend_Users whose last_login falls within the specified date range
10. THE User_Management_API SHALL return each Backend_User in the list using the List_Serializer fields: id, username, email, first_name, last_name, is_active, is_staff, is_superuser, groups (list of group name strings), date_joined, last_login

### Requirement 2: Retrieve Backend User Detail

**User Story:** As an Admin_User, I want to view the full details of a specific Backend_User, so that I can inspect their account configuration and group memberships.

#### Acceptance Criteria

1. WHEN a GET request is made to `api/v1/admin/users/{id}/`, THE User_Management_API SHALL return the Backend_User using the Detail_Serializer fields: id, username, email, first_name, last_name, groups (list of group name strings), permissions (list of permission codename strings), is_active, is_staff, is_superuser, last_login, date_joined
2. WHEN a GET request is made to `api/v1/admin/users/{id}/` with a non-existent id, THE User_Management_API SHALL return a 404 error using the Response_Wrapper

### Requirement 3: Retrieve Current Admin Profile

**User Story:** As an Admin_User, I want to retrieve my own profile through the admin users API, so that I can view my account details in the admin context.

#### Acceptance Criteria

1. WHEN a GET request is made to `api/v1/admin/users/me/`, THE User_Management_API SHALL return the requesting Admin_User's profile using the Detail_Serializer fields
2. THE User_Management_API SHALL return the same response structure as the user detail endpoint (Requirement 2)
3. THE User_Management_API SHALL NOT modify the existing `api/v1/auth/me/` endpoint in any way

### Requirement 4: Create Backend User

**User Story:** As an Admin_User, I want to create new Backend_User accounts, so that I can onboard new internal staff members to the platform.

#### Acceptance Criteria

1. WHEN a POST request is made to `api/v1/admin/users/` with valid user data (username, email, first_name, last_name, password, groups), THE User_Management_API SHALL create a new Backend_User and return the created user data using the Detail_Serializer
2. THE User_Service SHALL hash the provided password using Django's `set_password()` method before persisting the Backend_User
3. THE User_Service SHALL validate the password against Django's AUTH_PASSWORD_VALIDATORS (minimum length, common password check, numeric-only check, user attribute similarity check) before creating the Backend_User
4. WHEN the `groups` field is provided as a list of group names, THE User_Service SHALL assign the Backend_User to each specified group
5. WHEN the `is_active` field is not provided, THE User_Service SHALL default the value to True
6. WHEN a POST request is made with a username that already exists (case-insensitive check), THE User_Management_API SHALL return a 400 error using the Response_Wrapper with a descriptive message
7. WHEN a POST request is made with an email that already exists (case-insensitive check), THE User_Management_API SHALL return a 400 error using the Response_Wrapper with a descriptive message
8. WHEN a POST request is made with a group name that does not exist in the database, THE User_Management_API SHALL return a 400 error using the Response_Wrapper listing all invalid group names
9. WHEN the groups list contains any invalid group name, THE User_Management_API SHALL reject the entire request with a 400 error (no partial creation)
10. WHEN an empty groups list is provided, THE User_Service SHALL create the Backend_User with no group memberships
11. THE User_Management_API SHALL exclude the password field from all response payloads
12. THE User_Service SHALL normalize the email to lowercase before storing

### Requirement 5: Update Backend User

**User Story:** As an Admin_User, I want to update Backend_User account details, so that I can maintain accurate staff information and adjust group memberships.

#### Acceptance Criteria

1. WHEN a PATCH request is made to `api/v1/admin/users/{id}/` with valid data, THE User_Management_API SHALL update the specified Backend_User fields and return the updated user data using the Detail_Serializer
2. THE User_Management_API SHALL allow updates only to the fields: first_name, last_name, email, groups, is_active, is_staff, is_superuser
3. WHEN a PATCH request attempts to modify the username field, THE User_Management_API SHALL return a 400 error using the Response_Wrapper indicating username is not editable
4. WHEN the `groups` field is provided in the update, THE User_Service SHALL replace the Backend_User group memberships with the specified list of group names
5. WHEN the groups list in an update contains any group name that does not exist in the database, THE User_Management_API SHALL return a 400 error using the Response_Wrapper listing all invalid group names and reject the entire update
6. WHEN an empty groups list is provided in an update, THE User_Service SHALL remove all group memberships from the Backend_User
7. WHEN a PATCH request attempts to set `is_superuser=False` on the last Active_Superuser, THE User_Management_API SHALL return a 400 error using the Response_Wrapper indicating the last active superuser status cannot be removed
8. WHEN a PATCH request attempts to remove the last Active_Superuser from the 'Admin' group (leaving the superuser unable to manage users), THE User_Management_API SHALL return a 400 error using the Response_Wrapper indicating the last active superuser cannot be removed from the Admin group
9. WHEN a PATCH request is made to `api/v1/admin/users/{id}/` with a non-existent id, THE User_Management_API SHALL return a 404 error using the Response_Wrapper
10. WHEN the `email` field is provided in the update, THE User_Service SHALL normalize the email to lowercase before storing
11. WHEN a PATCH request provides an email that already belongs to another Backend_User (case-insensitive check), THE User_Management_API SHALL return a 400 error using the Response_Wrapper

### Requirement 6: Activate Backend User

**User Story:** As an Admin_User, I want to activate a previously deactivated Backend_User, so that the staff member can regain access to the platform.

#### Acceptance Criteria

1. WHEN a POST request is made to `api/v1/admin/users/{id}/activate/`, THE User_Service SHALL set the Backend_User is_active field to True and return the updated user data using the Detail_Serializer
2. WHEN a POST request is made to `api/v1/admin/users/{id}/activate/` with a non-existent id, THE User_Management_API SHALL return a 404 error using the Response_Wrapper

### Requirement 7: Deactivate Backend User

**User Story:** As an Admin_User, I want to deactivate a Backend_User account, so that the staff member loses platform access without permanently deleting their data.

#### Acceptance Criteria

1. WHEN a POST request is made to `api/v1/admin/users/{id}/deactivate/`, THE User_Service SHALL set the Backend_User is_active field to False and return the updated user data using the Detail_Serializer
2. WHEN a POST request is made to `api/v1/admin/users/{id}/deactivate/` where the target user is the requesting Admin_User, THE User_Management_API SHALL return a 400 error using the Response_Wrapper indicating an admin cannot deactivate themselves
3. WHEN a POST request is made to `api/v1/admin/users/{id}/deactivate/` where the target user is the last Active_Superuser, THE User_Management_API SHALL return a 400 error using the Response_Wrapper indicating the last active superuser cannot be deactivated
4. WHEN a POST request is made to `api/v1/admin/users/{id}/deactivate/` with a non-existent id, THE User_Management_API SHALL return a 404 error using the Response_Wrapper
5. THE User_Management_API SHALL use soft deactivation (is_active=False) and SHALL NOT hard-delete any Backend_User record

### Requirement 8: Bulk Activate Backend Users

**User Story:** As an Admin_User, I want to activate multiple Backend_Users at once, so that I can efficiently re-enable access for groups of staff members.

#### Acceptance Criteria

1. WHEN a POST request is made to `api/v1/admin/users/bulk-activate/` with a list of user IDs, THE User_Service SHALL set is_active to True for each valid Backend_User and return a summary response
2. THE User_Management_API SHALL return a summary containing the count of successfully activated users and a list of skipped users with their IDs and skip reasons
3. WHEN a user ID in the list does not exist, THE User_Service SHALL skip that ID and include it in the skipped list with reason "user not found"
4. WHEN a user in the list is already active, THE User_Service SHALL skip that user and include them in the skipped list with reason "already active"

### Requirement 9: Bulk Deactivate Backend Users

**User Story:** As an Admin_User, I want to deactivate multiple Backend_Users at once, so that I can efficiently revoke access for groups of staff members.

#### Acceptance Criteria

1. WHEN a POST request is made to `api/v1/admin/users/bulk-deactivate/` with a list of user IDs, THE User_Service SHALL set is_active to False for each valid Backend_User and return a summary response
2. THE User_Management_API SHALL return a summary containing the count of successfully deactivated users and a list of skipped users with their IDs and skip reasons
3. WHEN a user ID in the list is the requesting Admin_User, THE User_Service SHALL skip that ID and include it in the skipped list with reason "cannot deactivate yourself"
4. WHEN a user ID in the list refers to the last Active_Superuser, THE User_Service SHALL skip that ID and include it in the skipped list with reason "cannot deactivate last active superuser"
5. WHEN a user ID in the list does not exist, THE User_Service SHALL skip that ID and include it in the skipped list with reason "user not found"
6. WHEN a user in the list is already inactive, THE User_Service SHALL skip that user and include them in the skipped list with reason "already inactive"

### Requirement 10: Reset Backend User Password

**User Story:** As an Admin_User, I want to reset a Backend_User password, so that staff members who have lost access can regain entry with a new password.

#### Acceptance Criteria

1. WHEN a POST request is made to `api/v1/admin/users/{id}/reset-password/` with a new password, THE User_Service SHALL validate the password against Django's AUTH_PASSWORD_VALIDATORS and hash it using Django's `set_password()` method and persist the change
2. THE User_Management_API SHALL exclude the password from the response payload after a successful reset
3. WHEN a POST request is made to `api/v1/admin/users/{id}/reset-password/` with a non-existent id, THE User_Management_API SHALL return a 404 error using the Response_Wrapper
4. WHEN a POST request is made to `api/v1/admin/users/{id}/reset-password/` with an invalid password (fails Django AUTH_PASSWORD_VALIDATORS: minimum length, common password, numeric-only, or user attribute similarity), THE User_Management_API SHALL return a 400 error using the Response_Wrapper with validation details

### Requirement 11: Username and Email Validation

**User Story:** As an Admin_User, I want strict validation on usernames and emails, so that user accounts maintain data integrity and uniqueness.

#### Acceptance Criteria

1. THE User_Management_API SHALL require the username field on user creation
2. THE User_Management_API SHALL enforce username uniqueness using a case-insensitive comparison
3. THE User_Management_API SHALL enforce username length between 1 and 150 characters
4. THE User_Management_API SHALL enforce username characters to alphanumeric plus @, ., +, -, and _ only (Django default username validators)
5. THE User_Management_API SHALL require the email field on user creation
6. THE User_Management_API SHALL enforce email uniqueness using a case-insensitive comparison
7. THE User_Management_API SHALL validate email format before accepting the value
8. THE User_Service SHALL normalize email addresses to lowercase before storage on both create and update operations

### Requirement 12: Audit Logging

**User Story:** As an Admin_User, I want all state-changing operations on Backend_Users to be logged, so that I can review who made what changes and when.

#### Acceptance Criteria

1. WHEN a state-changing operation (create, update, activate, deactivate, bulk-activate, bulk-deactivate, password reset, group change) is performed, THE User_Service SHALL create a UserAuditLog record
2. THE UserAuditLog record SHALL capture: action type (string), target user ID (integer), acting admin user ID (integer), timestamp (auto-set to current UTC time), and a brief description of the change
3. THE UserAuditLog model SHALL be stored in the user management app database table
4. WHEN a GET request is made to `api/v1/admin/users/{id}/audit-log/`, THE User_Management_API SHALL return a paginated list of UserAuditLog records for the specified Backend_User ordered by timestamp descending
5. WHEN a GET request is made to `api/v1/admin/users/{id}/audit-log/` with a non-existent user id, THE User_Management_API SHALL return a 404 error using the Response_Wrapper

### Requirement 13: Authentication and Authorization

**User Story:** As a system operator, I want user management endpoints protected by authentication and role checks, so that only authorized administrators can manage backend users.

#### Acceptance Criteria

1. THE User_Management_API SHALL require a valid JWT access token for all endpoints
2. THE User_Management_API SHALL require the requesting user to be a member of the 'Admin' group using the IsAdminUser permission class from `apps/accounts/permissions.py`
3. WHEN a request is made without a valid JWT token, THE User_Management_API SHALL return a 401 Unauthorized error
4. WHEN a request is made by an authenticated user who is not in the 'Admin' group, THE User_Management_API SHALL return a 403 Forbidden error

### Requirement 14: API Response Format

**User Story:** As a frontend developer, I want consistent API response formatting, so that I can reliably parse and display user management data.

#### Acceptance Criteria

1. THE User_Management_API SHALL wrap all successful responses using the `success_response()` function from `common/responses.py`
2. THE User_Management_API SHALL wrap all error responses using the `error_response()` function from `common/responses.py`
3. THE User_Management_API SHALL wrap all paginated list responses using the `StandardPageNumberPagination` class from `common/pagination.py` which provides page_size=20, max_page_size=100, and meta format with page, page_size, total_count, total_pages
4. THE User_Management_API SHALL include Swagger/OpenAPI documentation for all endpoints via drf-spectacular decorators
5. THE User_Management_API SHALL use the Detail_Serializer for create and update response payloads
6. THE User_Management_API SHALL NEVER include the password field in any response payload

### Requirement 15: Last Active Superuser Protection

**User Story:** As a system operator, I want the system to prevent accidental lockout of all superuser accounts, so that there is always at least one active superuser capable of managing the platform.

#### Acceptance Criteria

1. WHEN a deactivation request targets the last Active_Superuser, THE User_Management_API SHALL reject the request with a 400 error
2. WHEN an update request attempts to set `is_superuser=False` on the last Active_Superuser, THE User_Management_API SHALL reject the request with a 400 error indicating the last active superuser status cannot be removed
3. WHEN an update request attempts to remove the last Active_Superuser from the 'Admin' group (via groups field update that excludes 'Admin'), THE User_Management_API SHALL reject the request with a 400 error indicating the last active superuser cannot be removed from the Admin group
4. WHEN a bulk-deactivate request includes the last Active_Superuser, THE User_Service SHALL skip that user and include them in the skipped list with reason "cannot deactivate last active superuser"
5. THE User_Service SHALL determine the last Active_Superuser by counting Backend_Users where is_superuser=True AND is_active=True; protection applies when the count equals 1 and the target is that user

### Requirement 16: Testing Requirements

**User Story:** As a developer, I want comprehensive test coverage for the user management module, so that I can confidently verify correctness and prevent regressions.

#### Acceptance Criteria

1. THE User_Management_API test suite SHALL include authorization tests verifying 401 for unauthenticated requests and 403 for authenticated non-Admin users
2. THE User_Management_API test suite SHALL include pagination tests verifying page, page_size, total_count, and total_pages in response meta
3. THE User_Management_API test suite SHALL include search tests verifying case-insensitive partial match across username, email, first_name, and last_name with OR logic
4. THE User_Management_API test suite SHALL include filter tests for is_active, is_staff, is_superuser, group, date_joined_after, date_joined_before, last_login_after, and last_login_before
5. THE User_Management_API test suite SHALL include ordering tests for each allowed field (username, email, date_joined, last_login, first_name, last_name) in both ascending and descending order
6. THE User_Management_API test suite SHALL include CRUD tests covering: create with valid data, create with duplicate username, create with invalid group name, update with valid data, update rejecting username modification, retrieve existing user, and 404 for non-existent user
7. THE User_Management_API test suite SHALL include self-protection tests verifying an admin cannot deactivate themselves and cannot remove their own Admin group membership
8. THE User_Management_API test suite SHALL include last-superuser protection tests verifying: cannot deactivate last active superuser, cannot remove superuser status from last active superuser, and cannot remove Admin group from last active superuser
9. THE User_Management_API test suite SHALL include bulk activate/deactivate tests covering: successful bulk operation, partial skip with reasons, and self-protection applied within bulk operations
10. THE User_Management_API test suite SHALL include password reset tests covering: valid password reset, invalid password failing validators, and user not found
11. THE User_Management_API test suite SHALL include audit log tests verifying: actions are logged correctly with all required fields, and audit logs are retrievable via the audit-log endpoint

### Requirement 17: Backward Compatibility

**User Story:** As a system operator, I want the user management module to be fully additive, so that existing functionality remains unaffected.

#### Acceptance Criteria

1. THE User_Management_API SHALL NOT modify existing authentication endpoints (login, logout, refresh, `api/v1/auth/me/`)
2. THE User_Management_API SHALL NOT modify existing apps (accounts views/serializers/URLs, chatbot, leads, CRM, analytics, knowledge_base)
3. THE User_Management_API SHALL NOT modify any existing migration files
4. THE User_Management_API SHALL mount exclusively under the `api/v1/admin/users/` URL prefix
5. THE User_Management_API SHALL use Django's built-in User, Group, and Permission models without introducing a custom user model
6. THE User_Management_API SHALL NOT modify the JWT authentication flow or token configuration
7. THE User_Management_API SHALL introduce only new files, new migrations in its own app, and a URL include in the root URL configuration
