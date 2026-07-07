# Implementation Plan: Settings Management

## Overview

Generic key-value settings system. New app `apps/settings_management/` with a `Setting` model (JSONField values), service layer, ViewSet, management command for seeding defaults, and comprehensive tests.

## Tasks

- [ ] 1. Set up app structure and data model
  - [ ] 1.1 Create `apps/settings_management/` app with package structure
    - `__init__.py`, `apps.py`, `admin.py`, `models.py`, `serializers.py`, `views.py`, `urls.py`
    - `services/__init__.py`, `services/settings_service.py`
    - `management/commands/__init__.py`, `management/commands/seed_settings.py`
    - `tests/__init__.py`, `tests/conftest.py`
    - Register in INSTALLED_APPS, mount URLs in core/urls.py
  - [ ] 1.2 Implement Setting model, generate and apply migration
  - [ ] 1.3 Register in Django admin

- [ ] 2. Implement serializers
  - [ ] 2.1 SettingSerializer, SettingPublicSerializer, SettingUpdateSerializer

- [ ] 3. Implement SettingsService
  - [ ] 3.1 list_settings, get_category_settings, get_public_settings
  - [ ] 3.2 update_category_settings (upsert, audit logging)
  - [ ] 3.3 mask_secret_value, secret handling logic
  - [ ] 3.4 _create_audit_log

- [ ] 4. Implement SettingsViewSet
  - [ ] 4.1 Admin endpoints: list_all, get_category, update_category
  - [ ] 4.2 Public endpoint: get_public (AllowAny)
  - [ ] 4.3 Swagger documentation

- [ ] 5. Implement seed_settings management command
  - [ ] 5.1 Default values for all 8 categories
  - [ ] 5.2 Idempotent (skip existing)

- [ ] 6. Implement tests
  - [ ] 6.1 Auth/permission tests
  - [ ] 6.2 CRUD tests (list, get category, update category)
  - [ ] 6.3 Public endpoint tests
  - [ ] 6.4 Secret masking tests
  - [ ] 6.5 Seed command tests
  - [ ] 6.6 Audit logging tests

- [ ] 7. Final checkpoint

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["1.1", "1.2", "1.3"] },
    { "id": 1, "tasks": ["2.1"] },
    { "id": 2, "tasks": ["3.1", "3.2", "3.3", "3.4"] },
    { "id": 3, "tasks": ["4.1", "4.2", "4.3"] },
    { "id": 4, "tasks": ["5.1", "5.2"] },
    { "id": 5, "tasks": ["6.1", "6.2", "6.3", "6.4", "6.5", "6.6"] },
    { "id": 6, "tasks": ["7"] }
  ]
}
```
