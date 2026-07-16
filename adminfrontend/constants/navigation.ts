import {
  LayoutDashboard,
  Users,
  UserCog,
  Shield,
  MessageSquare,
  BarChart3,
  BookOpen,
  Settings,
  type LucideIcon,
} from 'lucide-react';

export interface NavItem {
  title: string;
  href: string;
  icon: LucideIcon;
  badge?: string;
  permissions?: readonly string[];
  featureFlag?: string;
}

export const navigation: NavItem[] = [
  { title: 'Dashboard', href: '/dashboard', icon: LayoutDashboard }, // Accessible by any authenticated user
  { title: 'Leads', href: '/leads', icon: MessageSquare, permissions: ['leads.view_lead'] },
  { title: 'CRM', href: '/crm', icon: UserCog, permissions: ['crm.view_leadactivity'], featureFlag: 'ENABLE_CRM' },
  { title: 'Analytics', href: '/analytics', icon: BarChart3, permissions: ['analytics.view_analyticsevent'], featureFlag: 'ENABLE_ANALYTICS' },
  { title: 'Knowledge Base', href: '/knowledge', icon: BookOpen, permissions: ['knowledge_base.view_kbentry'], featureFlag: 'ENABLE_KNOWLEDGE_BASE' },
  { title: 'Users', href: '/users', icon: Users, permissions: ['auth.view_user'] },
  { title: 'Roles', href: '/roles', icon: Shield, permissions: ['auth.view_group'] },
  { title: 'Settings', href: '/settings', icon: Settings, permissions: ['platform_settings.view_platformsetting'] },
];
