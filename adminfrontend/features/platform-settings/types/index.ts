export interface PlatformSetting {
  id: string;
  group: string;
  key: string;
  value: string;
  value_type: 'STRING' | 'INTEGER' | 'BOOLEAN' | 'JSON' | 'FLOAT' | 'EMAIL' | 'URL';
  description: string;
  display_name: string;
  display_order: number;
  validation_rules: Record<string, unknown>;
  is_public: boolean;
  is_editable: boolean;
  is_sensitive: boolean;
  created_at: string;
  updated_at: string;
  updated_by: string | null;
}

export interface PlatformSettingsGroup {
  name: string;
  display_name: string;
  count: number;
  editable_count: number;
}

export interface PlatformSettingUpdatePayload {
  value: string;
}

export interface CachePayload {
  group?: string | null;
  key?: string | null;
}

export interface ResetPayload {
  confirm: string; // Must be "RESET_PLATFORM_SETTINGS"
}

export interface PaginatedResponse<T> {
  success: boolean;
  data: T[];
  message: string;
  meta: {
    pagination: {
      page: number;
      page_size: number;
      total_count: number;
      total_pages: number;
    };
  };
}
