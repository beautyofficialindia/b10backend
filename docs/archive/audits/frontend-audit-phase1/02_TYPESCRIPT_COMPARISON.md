# TypeScript Interface vs Backend Serializer Comparison

## 🔴 CRITICAL: Auth User Type Mismatch

### Backend `UserSerializer` (accounts/serializers.py)
```python
fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 'groups']
# groups = GroupSerializer(many=True) → [{id: int, name: str}]
# role = SerializerMethodField → str | null
```

### Frontend `User` type (features/auth/types/index.ts)
```typescript
interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  is_active: boolean;      // ❌ NOT returned by /auth/me/
  is_staff: boolean;       // ❌ NOT returned by /auth/me/
  is_superuser: boolean;   // ❌ NOT returned by /auth/me/
  groups: string[];        // ❌ Backend returns {id, name}[] not string[]
}
```

### Impact
- `is_active`, `is_staff`, `is_superuser` will always be `undefined` from `/auth/me/`
- `groups` will be an array of objects `[{id: 1, name: "Admin"}]` not strings
- The Header component uses `user?.first_name` — works because the field exists
- The AuthGuard uses `!!user` — works because the object is truthy regardless

### Severity: 🔴 Critical
- If any component checks `user.is_active` or `user.is_superuser`, it will fail silently
- `groups` type mismatch means any `user.groups.includes('Admin')` check would fail

---

## ✅ Leads Types — Match

### Backend `LeadListSerializer`
```python
fields = ['id', 'full_name', 'company_name', 'email', 'phone', 'industry', 'project_type', 'status', 'created_at']
```

### Frontend `Lead` type
```typescript
interface Lead {
  id: string; full_name: string | null; company_name: string | null;
  email: string | null; phone: string | null; industry: string | null;
  project_type: string | null; status: LeadStatus; created_at: string;
}
```
✅ All fields match. UUID renders as string. Nullable fields correctly typed.

---

## ✅ Lead Detail Types — Match

### Backend `LeadDetailSerializer`
```python
fields = '__all__'  # includes conversation with messages
```

### Frontend `LeadDetail` type
All model fields represented. `conversation` correctly typed as nested object with messages array.

---

## ✅ Knowledge Base Types — Match

Backend serializer fields align with frontend `KnowledgeEntry` and `KnowledgeEntryDetail` types.

---

## ✅ Users Management Types — Match

Backend `UserListSerializer` fields: `id, username, email, first_name, last_name, is_active, is_staff, is_superuser, groups, date_joined, last_login`
Frontend `User` type matches exactly. `groups` here is `string[]` (via SerializerMethodField) — correct.

Note: The User Management `/admin/users/` endpoint returns `groups: string[]` (list of names). This is DIFFERENT from `/auth/me/` which returns `groups: [{id, name}]`. Both are correct for their respective serializers but the frontend uses the SAME `User` type for both contexts.

---

## ✅ Roles Types — Match
## ✅ Settings Types — Match
## ✅ Analytics/Dashboard Types — Match
