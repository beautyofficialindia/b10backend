export interface Setting {
  id: number;
  category: SettingCategory;
  key: string;
  value: unknown;
  description: string | null;
  is_public: boolean;
  updated_at: string;
  updated_by_username: string | null;
}

export type SettingCategory = 'GENERAL' | 'BRANDING' | 'AI' | 'CHATBOT' | 'NOTIFICATIONS' | 'SECURITY' | 'FEATURE_FLAGS' | 'INTEGRATIONS';

export const SETTING_CATEGORIES: { value: SettingCategory; label: string; description: string }[] = [
  { value: 'GENERAL', label: 'General', description: 'Company information and basic settings' },
  { value: 'BRANDING', label: 'Branding', description: 'Logo, colors, and visual identity' },
  { value: 'AI', label: 'AI', description: 'AI provider and model configuration' },
  { value: 'CHATBOT', label: 'Chatbot', description: 'Chatbot behavior and messaging' },
  { value: 'NOTIFICATIONS', label: 'Notifications', description: 'Email and alert preferences' },
  { value: 'SECURITY', label: 'Security', description: 'Authentication and access control' },
  { value: 'FEATURE_FLAGS', label: 'Feature Flags', description: 'Enable or disable modules' },
  { value: 'INTEGRATIONS', label: 'Integrations', description: 'Third-party service connections' },
];
