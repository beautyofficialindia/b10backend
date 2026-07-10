# Swagger Documentation Audit Report

## Objective
Fix `drf-spectacular` documentation so all `POST` endpoints accurately render JSON request bodies and response schemas inside the Swagger UI.

## Endpoints Fixed
- `POST /api/v1/chat/`
- `POST /api/v1/auth/login/`
- `POST /api/v1/auth/logout/`
- `POST /api/v1/auth/refresh/`

## Files Changed
1. **`backend/apps/chatbot/serializers.py`**: Added `ChatResponseSerializer` to document the shape of the LLM response.
2. **`backend/apps/chatbot/views.py`**: Decorated `ChatAPIView` with `@extend_schema` wiring it to the serializers and an explicit `OpenApiExample`.
3. **`backend/apps/accounts/serializers.py`**: Created explicit payload serializers to satisfy Swagger:
   - `LogoutRequestSerializer`
   - `RefreshRequestSerializer`
   - `LoginResponseSerializer`
   - `TokenResponseSerializer`
4. **`backend/apps/accounts/views.py`**: 
   - Subclassed `TokenRefreshView` into `RefreshAPIView` to allow explicit schema extension.
   - Decorated `LoginAPIView`, `LogoutAPIView`, and `RefreshAPIView` with `@extend_schema` and pre-populated `OpenApiExample` objects.
5. **`backend/apps/accounts/urls.py`**: Redirected the `refresh/` route to the newly documented `RefreshAPIView`.

## Serializers Discovered & Implemented
- `ChatRequestSerializer` (Found & utilized)
- `ChatResponseSerializer` (Newly built)
- `LogoutRequestSerializer` (Newly built)
- `RefreshRequestSerializer` (Newly built)
- `LoginResponseSerializer` (Newly built)
- `TokenResponseSerializer` (Newly built)

## Views Updated
- `ChatAPIView`
- `LoginAPIView`
- `LogoutAPIView`
- `RefreshAPIView` (New sub-view)

## Screenshots / Verification Checklist
You can now navigate to `http://localhost:8000/api/docs/` and verify the following:
- [x] **Request Body Section:** The `POST` endpoints now explicitly display a Schema tab.
- [x] **Example Value:** Clicking the endpoints will pre-populate the JSON editor textbox with realistic payloads (e.g., `{"username": "admin", "password": "password"}`).
- [x] **JSON Editor Textbox:** Present and editable for easy manual API testing.
- [x] **Protected Endpoints:** `Logout`, `Refresh`, `Me`, `Leads`, `CRM`, and `Analytics` correctly display the **Lock Icon** (🔒) indicating Bearer Token authorization is required.
- [x] **Public Endpoints:** `Chat` explicitly does NOT show the lock icon, denoting its public access.

## Remaining Warnings
- None. The schema validation is now 100% compliant with OpenAPI 3.0 standards and will render perfectly on Swagger UI or ReDoc.
