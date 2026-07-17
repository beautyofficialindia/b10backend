'use client';

import { Skeleton } from '@/components/ui/skeleton';
import { NotificationCard } from './notification-card';
import { NotificationEmptyState } from './notification-empty-state';
import type { Notification } from '../types';

interface NotificationListProps {
  notifications: Notification[];
  isLoading: boolean;
  error?: Error | null;
}

export function NotificationList({ notifications, isLoading, error }: NotificationListProps) {
  if (isLoading) {
    return (
      <div className="divide-y divide-border">
        {Array.from({ length: 5 }).map((_, i) => (
          <NotificationSkeleton key={i} />
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center py-16 text-center px-8">
        <p className="text-sm font-medium text-destructive">Failed to load notifications</p>
        <p className="mt-1 text-xs text-muted-foreground">{error.message}</p>
      </div>
    );
  }

  if (notifications.length === 0) {
    return <NotificationEmptyState variant="empty" />;
  }

  return (
    <div className="divide-y divide-border/60">
      {notifications.map((notification) => (
        <NotificationCard key={notification.id} notification={notification} />
      ))}
    </div>
  );
}

function NotificationSkeleton() {
  return (
    <div className="flex gap-3 px-4 py-3">
      <Skeleton className="h-8 w-8 rounded-full shrink-0" />
      <div className="flex-1 space-y-2 pt-0.5">
        <Skeleton className="h-3.5 w-2/3" />
        <Skeleton className="h-3 w-full" />
        <Skeleton className="h-3 w-1/2" />
        <div className="flex gap-2 pt-0.5">
          <Skeleton className="h-3 w-16" />
          <Skeleton className="h-4 w-14 rounded" />
        </div>
      </div>
    </div>
  );
}
