export interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  is_active: boolean;
  is_staff: boolean;
  is_superuser: boolean;
  groups: string[];
  date_joined: string;
  last_login: string | null;
}

export interface UserDetail extends User {
  permissions: string[];
}

export interface UserCreatePayload {
  username: string;
  email: string;
  password: string;
  first_name?: string;
  last_name?: string;
  groups?: string[];
  is_active?: boolean;
  is_staff?: boolean;
  is_superuser?: boolean;
}

export interface UserUpdatePayload {
  first_name?: string;
  last_name?: string;
  email?: string;
  groups?: string[];
  is_active?: boolean;
  is_staff?: boolean;
  is_superuser?: boolean;
}

export interface UserFilters {
  search?: string;
  is_active?: string;
  is_superuser?: string;
  group?: string;
  ordering?: string;
  page?: number;
  page_size?: number;
}

export interface AuditLogEntry {
  id: number;
  actor: number | null;
  actor_username: string | null;
  target_user: number | null;
  action: string;
  description: string;
  metadata: Record<string, unknown>;
  created_at: string;
}

export interface UserListResponse {
  success: boolean;
  data: User[];
  meta: { pagination: { page: number; page_size: number; total_count: number; total_pages: number } };
}

export interface BulkResult {
  activated_count?: number;
  deactivated_count?: number;
  skipped: { id: number; reason: string }[];
}
