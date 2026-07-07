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
}

export const navigation: NavItem[] = [
  { title: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { title: 'Leads', href: '/leads', icon: MessageSquare },
  { title: 'CRM', href: '/crm', icon: UserCog },
  { title: 'Analytics', href: '/analytics', icon: BarChart3 },
  { title: 'Knowledge Base', href: '/knowledge', icon: BookOpen },
  { title: 'Users', href: '/users', icon: Users },
  { title: 'Roles', href: '/roles', icon: Shield },
  { title: 'Settings', href: '/settings', icon: Settings },
];
