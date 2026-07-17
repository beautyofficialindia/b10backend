'use client';

import { BellOff, Inbox } from 'lucide-react';
import { cn } from '@/lib/utils';

interface NotificationEmptyStateProps {
  variant?: 'all-clear' | 'empty';
  compact?: boolean;
}

export function NotificationEmptyState({
  variant = 'empty',
  compact = false,
}: NotificationEmptyStateProps) {
  const isAllClear = variant === 'all-clear';

  return (
    <div
      className={cn(
        'flex flex-col items-center justify-center text-center',
        compact ? 'gap-2 py-4 px-6' : 'gap-3 py-16 px-8',
      )}
    >
      <span
        className={cn(
          'flex items-center justify-center rounded-full bg-muted',
          compact ? 'h-10 w-10' : 'h-14 w-14',
        )}
      >
        {isAllClear ? (
          <BellOff className={cn('text-muted-foreground', compact ? 'h-5 w-5' : 'h-7 w-7')} />
        ) : (
          <Inbox className={cn('text-muted-foreground', compact ? 'h-5 w-5' : 'h-7 w-7')} />
        )}
      </span>

      <div>
        <p className={cn('font-semibold text-foreground', compact ? 'text-sm' : 'text-base')}>
          {isAllClear ? "You're all caught up" : 'No notifications yet'}
        </p>
        {!compact && (
          <p className="mt-1 text-sm text-muted-foreground">
            {isAllClear
              ? 'No unread notifications. Check back later.'
              : 'Platform events and alerts will appear here.'}
          </p>
        )}
      </div>
    </div>
  );
}
