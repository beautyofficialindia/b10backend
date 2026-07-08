# RUNTIME DEBUG REPORT

## Environment
* Testing frontend at: http://localhost:3000
* Testing backend at: http://127.0.0.1:8000/api/v1

## Local Storage
* access_token exists? true
* refresh_token exists? true
* access_token (first 20): eyJhbGciOiJIUzI1NiIs
* access_token (last 20): 21oDGzAUUgUiFVIBz-Ws
* refresh_token (first 20): eyJhbGciOiJIUzI1NiIs
* refresh_token (last 20): YSM8qOqSnszjexNoBaMU

## Network Requests

## Request Headers

## Response Bodies

### POST http://localhost:8000/api/v1/auth/login/
* Status Code: 200
* Authorization: None
* Origin: None
* Referer: http://localhost:3000/
* Host: None

**Token Verification:**
* Is Authorization header present? false
* Does it begin with Bearer? false
* Is access token identical to localStorage? false

**Response:**
```json
{"refresh":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc4NDEzNDAzMiwiaWF0IjoxNzgzNTI5MjMyLCJqdGkiOiI4OGIyM2NiZjBhYjg0MDZmOTBmMDY4NTk2ZmYwYTcwNyIsInVzZXJfaWQiOiIzIn0.PEAfriMeVoMh47vPWG5DpKUYSM8qOqSnszjexNoBaMU","access":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzgzNTMwMTMyLCJpYXQiOjE3ODM1MjkyMzMsImp0aSI6ImE2ZmQ2NGU4MjRlMjRjYWRhNjEwNTg3YWEwNTBlZmI5IiwidXNlcl9pZCI6IjMifQ.u4lR2mE7HGV-2sdJ6tdlJS-21oDGzAUUgUiFVIBz-Ws","user":{"id":3,"username":"muskankumar","email":"muskankumar7842@gmail.com","role":null}}
```

### OPTIONS http://localhost:8000/api/v1/auth/login/
* Status Code: 200
* Authorization: None
* Origin: http://localhost:3000
* Referer: None
* Host: None

**Token Verification:**
* Is Authorization header present? false
* Does it begin with Bearer? false
* Is access token identical to localStorage? false

**Response:**
```json

```

### GET http://localhost:8000/api/v1/auth/me/
* Status Code: Pending
* Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzgzNTMwMTMyLCJpYXQiOjE3ODM1MjkyMzMsImp0aSI6ImE2ZmQ2NGU4MjRlMjRjYWRhNjEwNTg3YWEwNTBlZmI5IiwidXNlcl9pZCI6IjMifQ.u4lR2mE7HGV-2sdJ6tdlJS-21oDGzAUUgUiFVIBz-Ws
* Origin: None
* Referer: http://localhost:3000/
* Host: None

**Token Verification:**
* Is Authorization header present? true
* Does it begin with Bearer? true
* Is access token identical to localStorage? true

### OPTIONS http://localhost:8000/api/v1/auth/me/
* Status Code: 200
* Authorization: None
* Origin: http://localhost:3000
* Referer: None
* Host: None

**Token Verification:**
* Is Authorization header present? false
* Does it begin with Bearer? false
* Is access token identical to localStorage? false

**Response:**
```json

```

## Token Comparison
Based on the requests, the Authorization token sent in the failed request is N/A (No failed admin requests found or no requests to /admin/).

## Refresh Flow

```text
GET http://localhost:8000/api/v1/auth/me/ -> ?

```

Could not determine /admin/dashboard token usage after refresh.

## Console Errors


## Root Cause Analysis

Based on the evidence:
1. **Token mismatch / Synchronization issue**: If the token sent to the backend differs from the localStorage token, this indicates a state desync in the frontend (e.g. using a stale token in memory/Axios interceptor, or Server Components not having access to localStorage token). [Check Token Comparison]
2. **Refresh Flow Race Condition**: If `/admin/dashboard` is fired *before* `/auth/refresh` completes, or with the old token. [Check Refresh Flow]
3. **CORS / Preflight**: If OPTIONS fails. [Check Network Errors]
4. **Missing Bearer prefix**: [Check Token Verification]

(The exact root cause will be identified by reviewing the above evidence.)
