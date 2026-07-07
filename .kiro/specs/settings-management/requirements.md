# Requirements Document

## Introduction

This module provides a flexible, generic settings management system for the B10 IT Solution platform. It uses a key-value store pattern with a `Setting` model backed by a JSONField for values, allowing new settings to be added without migrations. Settings are organized by category and support multiple value types (string, number, boolean, object, array). The module operates through REST API endpoints mounted at `api/v1/admin/settings/` and includes a public endpoint for frontend-consumable settings.

## Glossary

- **Setting**: A database record with category, key, JSON value, description, and visibility flag
- **Category**: A logical grouping of related settings (GENERAL, BRANDING, AI, CHATBOT, NOTIFICATIONS, SECURITY, FEATURE_FLAGS, INTEGRATIONS)
- **SettingsService**: The service layer component encapsulating all business logic
- **Public Setting**: A Setting with `is_public=True`, accessible without authentication
- **Secret Setting**: Integration credentials that must never be exposed in API responses

## Requirements

### Requirement 1: Setting Model

**User Story:** As a developer, I want a flexible settings storage that supports multiple value types without requiring migrations for new settings.

#### Acceptance Criteria

1. THE Setting model SHALL have fields: id (BigAutoField), category (CharField), key (CharField), value (JSONField), description (TextField, nullable), is_public (BooleanField, default=False), created_at (DateTimeField), updated_at (DateTimeField), updated_by (FK to User, nullable)
2. THE Setting model SHALL enforce a unique constraint on (category, key)
3. THE value field SHALL support: string, number, boolean, object, array, null
4. THE Setting model SHALL have indexes on: category, (category, key), is_public
5. THE categories SHALL be: GENERAL, BRANDING, AI, CHATBOT, NOTIFICATIONS, SECURITY, FEATURE_FLAGS, INTEGRATIONS

### Requirement 2: List All Settings

**User Story:** As an Admin_User, I want to list all settings grouped by category.

#### Acceptance Criteria

1. WHEN a GET request is made to `api/v1/admin/settings/`, THE API SHALL return all settings grouped by category
2. WHEN a `search` query parameter is provided, THE API SHALL filter settings by key or description using case-insensitive partial matching
3. WHEN a `category` query parameter is provided, THE API SHALL filter settings to only that category
4. THE response SHALL include: id, category, key, value, description, is_public, updated_at, updated_by (username)

### Requirement 3: Get Settings by Category

**User Story:** As an Admin_User, I want to retrieve all settings for a specific category.

#### Acceptance Criteria

1. WHEN a GET request is made to `api/v1/admin/settings/{category}/`, THE API SHALL return all settings in that category
2. WHEN an invalid category is provided, THE API SHALL return a 400 error listing valid categories
3. THE API SHALL mask secret values for INTEGRATIONS category (show only key names and whether a value is set, never the actual secret)

### Requirement 4: Update Settings by Category

**User Story:** As an Admin_User, I want to update multiple settings within a category at once.

#### Acceptance Criteria

1. WHEN a PATCH request is made to `api/v1/admin/settings/{category}/` with a payload of key-value pairs, THE SettingsService SHALL update each setting's value
2. WHEN a key does not exist in the category, THE SettingsService SHALL create it (upsert behavior)
3. WHEN an invalid category is provided, THE API SHALL return a 400 error
4. THE SettingsService SHALL set updated_by to the requesting admin
5. THE SettingsService SHALL set updated_at to the current timestamp
6. THE SettingsService SHALL create an audit log entry for each update

### Requirement 5: Public Settings Endpoint

**User Story:** As a frontend developer, I want to fetch public settings without authentication for theming and display purposes.

#### Acceptance Criteria

1. WHEN a GET request is made to `api/v1/admin/settings/public/`, THE API SHALL return only settings where is_public=True
2. THE endpoint SHALL NOT require authentication
3. THE response SHALL include: category, key, value
4. THE endpoint SHALL never return INTEGRATIONS or SECURITY category settings regardless of is_public flag

### Requirement 6: Secret Handling

**User Story:** As a system operator, I want integration secrets to be stored securely and never exposed in API responses.

#### Acceptance Criteria

1. THE API SHALL never return raw values for settings in the INTEGRATIONS category that contain API keys, tokens, or secrets
2. FOR INTEGRATIONS settings, THE API SHALL return a masked representation: `{"is_set": true/false}` instead of the actual value
3. THE SettingsService SHALL allow admins to write/overwrite secret values
4. THE database SHALL store the actual values (for internal use by other services)

### Requirement 7: Default Settings Seeding

**User Story:** As a system operator, I want default settings created on first deployment.

#### Acceptance Criteria

1. THE module SHALL provide a management command `seed_settings` that creates default settings if they don't exist
2. THE command SHALL be idempotent (safe to run multiple times)
3. THE command SHALL seed defaults for all categories defined in the spec
4. THE command SHALL NOT overwrite existing settings

### Requirement 8: Authentication and Authorization

**User Story:** As a system operator, I want settings endpoints protected appropriately.

#### Acceptance Criteria

1. THE admin settings endpoints SHALL require a valid JWT access token
2. THE admin settings endpoints SHALL require the requesting user to be in the 'Admin' group
3. THE public settings endpoint SHALL NOT require authentication
4. WHEN a request is made without a valid JWT to admin endpoints, THE API SHALL return 401
5. WHEN a non-Admin user accesses admin endpoints, THE API SHALL return 403

### Requirement 9: Audit Logging

**User Story:** As an Admin_User, I want all settings changes to be logged.

#### Acceptance Criteria

1. WHEN settings are updated, THE SettingsService SHALL create a UserAuditLog record
2. THE audit record SHALL capture: action type (`settings_updated`), actor, category, changed keys, old values, new values
3. THE audit record SHALL NOT store secret/integration values in metadata

### Requirement 10: API Response Format

**User Story:** As a frontend developer, I want consistent API response formatting.

#### Acceptance Criteria

1. THE API SHALL use `success_response()` and `error_response()` from `common/responses.py`
2. THE API SHALL include Swagger/OpenAPI documentation via drf-spectacular
3. THE API SHALL use `StandardPageNumberPagination` where applicable

### Requirement 11: Backward Compatibility

**User Story:** As a system operator, I want the settings module to be fully additive.

#### Acceptance Criteria

1. THE module SHALL NOT modify existing apps or endpoints
2. THE module SHALL mount exclusively under `api/v1/admin/settings/` (admin) with public at `api/v1/settings/public/`
3. THE module SHALL NOT modify any existing migration files
4. THE module SHALL introduce only new files, new migrations in its own app, and URL includes in core/urls.py
