'use client';

import { forwardRef, useRef } from 'react';
import { Bell } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import { useUnreadCount } from '../hooks/use-notifications';

const NotificationBell = forwardRef<
  HTMLButtonElement,
  React.ComponentPropsWithoutRef<typeof Button>
>(({ className, ...props }, ref) => {
  const { data } = useUnreadCount();
  const count = data?.unread_count ?? 0;

  return (
    <Button
      ref={ref}
      variant="ghost"
      size="icon"
      className={cn('h-9 w-9 relative', className)}
      aria-label={`Notifications${count > 0 ? `, ${count} unread` : ''}`}
      {...props}
    >
      <Bell className="h-4 w-4" />
      {count > 0 && (
        <span
          className={cn(
            'absolute -top-0.5 -right-0.5 flex items-center justify-center',
            'h-4 min-w-4 rounded-full px-0.5',
            'bg-destructive text-[10px] font-semibold text-destructive-foreground',
            'transition-transform duration-200',
          )}
        >
          {count > 99 ? '99+' : count}
        </span>
      )}
    </Button>
  );
});

NotificationBell.displayName = 'NotificationBell';

export { NotificationBell };
