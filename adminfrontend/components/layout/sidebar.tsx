'use client';

import { useAuth, PermissionGuard } from '@/features/auth';
import { useFeatureFlags } from '@/features/platform-settings/providers';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import { navigation } from '@/constants/navigation';
import { PanelLeftClose, PanelLeft } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip';
import { motion, AnimatePresence } from 'framer-motion';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';

interface SidebarProps {
  collapsed: boolean;
  onToggle: () => void;
}

export function Sidebar({ collapsed, onToggle }: SidebarProps) {
  const pathname = usePathname();
  const { user } = useAuth();
  const { flags } = useFeatureFlags();
  
  const initials = user
    ? `${user.first_name?.[0] || ''}${user.last_name?.[0] || ''}`.toUpperCase() || user.username[0].toUpperCase()
    : 'U';

  return (
    <motion.aside
      initial={false}
      animate={{ width: collapsed ? 64 : 256 }}
      transition={{ duration: 0.2, ease: 'easeInOut' }}
      className={cn(
        'fixed inset-y-0 left-0 z-30 flex flex-col border-r border-sidebar-border bg-sidebar',
        'hidden lg:flex'
      )}
    >
      {/* Logo */}
      <div className="flex h-14 items-center border-b border-sidebar-border px-4">
        <AnimatePresence mode="wait">
          {!collapsed && (
            <motion.span
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.15 }}
              className="text-lg font-semibold text-sidebar-foreground"
            >
              B10 Admin
            </motion.span>
          )}
        </AnimatePresence>
        {collapsed && (
          <span className="text-lg font-bold text-sidebar-foreground mx-auto">B</span>
        )}
      </div>

      {/* Navigation */}
      <ScrollArea className="flex-1 py-3">
        <nav className="flex flex-col gap-1 px-2">
          {navigation
            .filter((item) => !item.featureFlag || flags[item.featureFlag] !== false)
            .map((item) => {
            const isActive = pathname.startsWith(item.href);
            const Icon = item.icon;

            const linkContent = (
              <Link
                href={item.href}
                className={cn(
                  'flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors',
                  'hover:bg-sidebar-accent hover:text-sidebar-accent-foreground',
                  'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sidebar-ring',
                  isActive
                    ? 'bg-sidebar-accent text-sidebar-accent-foreground'
                    : 'text-sidebar-foreground/70',
                  collapsed && 'justify-center px-2'
                )}
              >
                <Icon className="h-4.5 w-4.5 shrink-0" />
                {!collapsed && <span>{item.title}</span>}
              </Link>
            );

            if (collapsed) {
              return (
                <PermissionGuard key={item.href} permissions={item.permissions}>
                  <Tooltip>
                    <TooltipTrigger render={linkContent} />
                    <TooltipContent side="right" sideOffset={8}>
                      {item.title}
                    </TooltipContent>
                  </Tooltip>
                </PermissionGuard>
              );
            }

            return (
              <PermissionGuard key={item.href} permissions={item.permissions}>
                <div>{linkContent}</div>
              </PermissionGuard>
            );
          })}
        </nav>
      </ScrollArea>

      {/* Bottom Profile & Toggle */}
      <div className="mt-auto border-t border-sidebar-border p-3 flex flex-col gap-3">
        {/* Profile */}
        <div className={cn("flex items-center gap-3 rounded-xl p-2", !collapsed && "bg-sidebar-accent/50 hover:bg-sidebar-accent transition-colors cursor-pointer")}>
          <Avatar className="h-9 w-9 shrink-0 rounded-lg">
             <AvatarFallback className="rounded-lg bg-primary/20 text-primary text-sm font-semibold">{initials}</AvatarFallback>
          </Avatar>
          {!collapsed && (
            <div className="flex flex-col min-w-0">
              <span className="truncate text-sm font-semibold text-sidebar-foreground">
                {user?.first_name || user?.username || 'Admin User'}
              </span>
              <span className="truncate text-xs text-sidebar-foreground/60">
                {user?.email || 'admin@b10.com'}
              </span>
            </div>
          )}
        </div>

        {/* Toggle */}
        <Button
          variant="ghost"
          size="icon"
          onClick={onToggle}
          className={cn('h-8 w-8 text-sidebar-foreground/70 hover:bg-sidebar-accent', !collapsed && 'ml-auto')}
          aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          {collapsed ? <PanelLeft className="h-4 w-4" /> : <PanelLeftClose className="h-4 w-4" />}
        </Button>
      </div>
    </motion.aside>
  );
}
