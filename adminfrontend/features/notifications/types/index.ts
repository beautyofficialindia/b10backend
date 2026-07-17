export type NotificationType = 'INFO' | 'SUCCESS' | 'NOTICE' | 'WARNING' | 'CRITICAL';

export type NotificationCategory =
  | 'SYSTEM'
  | 'CRM'
  | 'LEADS'
  | 'KNOWLEDGE'
  | 'USERS'
  | 'ROLES'
  | 'SETTINGS'
  | 'ANALYTICS'
  | 'AI'
  | 'AUTHENTICATION'
  | 'DEPLOYMENT'
  | 'SECURITY';

export interface Notification {
  id: string;
  title: string;
  message: string;
  type: NotificationType;
  category: NotificationCategory;
  action_url: string;
  is_read: boolean;
  actor: number | null;
  actor_name: string | null;
  recipient: number | null;
  recipient_name: string | null;
  created_at: string;
}

export interface NotificationListResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: Notification[];
  available_categories: Array<{ category: NotificationCategory; count: number }>;
}

export interface UnreadCountResponse {
  unread_count: number;
}

export const NOTIFICATION_TYPE_CONFIG: Record<
  NotificationType,
  { label: string; color: string; bgColor: string; borderColor: string }
> = {
  INFO:     { label: 'Info',     color: 'text-blue-600 dark:text-blue-400',   bgColor: 'bg-blue-50 dark:bg-blue-950/40',    borderColor: 'border-blue-400' },
  SUCCESS:  { label: 'Success',  color: 'text-emerald-600 dark:text-emerald-400', bgColor: 'bg-emerald-50 dark:bg-emerald-950/40', borderColor: 'border-emerald-400' },
  NOTICE:   { label: 'Notice',   color: 'text-slate-600 dark:text-slate-400', bgColor: 'bg-slate-50 dark:bg-slate-950/40',  borderColor: 'border-slate-400' },
  WARNING:  { label: 'Warning',  color: 'text-amber-600 dark:text-amber-400', bgColor: 'bg-amber-50 dark:bg-amber-950/40',  borderColor: 'border-amber-400' },
  CRITICAL: { label: 'Critical', color: 'text-red-600 dark:text-red-400',     bgColor: 'bg-red-50 dark:bg-red-950/40',      borderColor: 'border-red-500' },
};

export const NOTIFICATION_CATEGORY_LABELS: Record<NotificationCategory, string> = {
  SYSTEM:         'System',
  CRM:            'CRM',
  LEADS:          'Leads',
  KNOWLEDGE:      'Knowledge',
  USERS:          'Users',
  ROLES:          'Roles',
  SETTINGS:       'Settings',
  ANALYTICS:      'Analytics',
  AI:             'AI',
  AUTHENTICATION: 'Auth',
  DEPLOYMENT:     'Deployment',
  SECURITY:       'Security',
};
