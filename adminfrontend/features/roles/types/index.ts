export interface Role {
  id: number;
  name: string;
  permissions_count: number;
  users_count: number;
}

export interface RoleDetail {
  id: number;
  name: string;
  permissions: Permission[];
  users_count: number;
}

export interface Permission {
  id: number;
  codename: string;
  name: string;
  content_type: string; // "app_label.model"
}

export interface RoleUser {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  is_active: boolean;
}

export interface RoleFilters {
  search?: string;
  ordering?: string;
  page?: number;
  page_size?: number;
}
