'use client';

import { useRouter } from 'next/navigation';
import { formatDistanceToNow } from 'date-fns';
import {
  Info,
  CheckCircle2,
  Bell,
  AlertTriangle,
  AlertOctagon,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { Badge } from '@/components/ui/badge';
import { useMarkRead } from '../hooks/use-notifications';
import type { Notification, NotificationType, NotificationCategory } from '../types';
import { NOTIFICATION_TYPE_CONFIG, NOTIFICATION_CATEGORY_LABELS } from '../types';

const TYPE_ICONS: Record<NotificationType, React.ElementType> = {
  INFO:     Info,
  SUCCESS:  CheckCircle2,
  NOTICE:   Bell,
  WARNING:  AlertTriangle,
  CRITICAL: AlertOctagon,
};

interface NotificationCardProps {
  notification: Notification;
  compact?: boolean;
}

export function NotificationCard({ notification, compact = false }: NotificationCardProps) {
  const router = useRouter();
  const markRead = useMarkRead();

  const config = NOTIFICATION_TYPE_CONFIG[notification.type];
  const Icon = TYPE_ICONS[notification.type];
  const categoryLabel = NOTIFICATION_CATEGORY_LABELS[notification.category as NotificationCategory] ?? notification.category;

  const relativeTime = formatDistanceToNow(new Date(notification.created_at), { addSuffix: true });

  const handleClick = () => {
    if (!notification.is_read) {
      markRead.mutate(notification.id);
    }
    if (notification.action_url) {
      router.push(notification.action_url);
    }
  };

  return (
    <div
      role="button"
      tabIndex={0}
      onClick={handleClick}
      onKeyDown={(e) => e.key === 'Enter' && handleClick()}
      className={cn(
        'relative flex gap-3 transition-colors cursor-pointer outline-none',
        'focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-1',
        compact ? 'px-3 py-2.5 mx-1 rounded-md' : 'px-4 py-3',
        !notification.is_read
          ? 'bg-accent/50 hover:bg-accent'
          : 'hover:bg-accent/30',
      )}
    >
      {/* Left type accent bar (full page only) */}
      {!compact && (
        <span
          className={cn('absolute left-0 top-2 bottom-2 w-0.5 rounded-full', config.borderColor)}
        />
      )}

      {/* Icon */}
      <span
        className={cn(
          'mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-full',
          config.bgColor,
        )}
      >
        <Icon className={cn('h-4 w-4', config.color)} />
      </span>

      {/* Content */}
      <div className="flex-1 min-w-0">
        <div className="flex items-start justify-between gap-2">
          <p
            className={cn(
              'text-sm leading-snug',
              !notification.is_read
                ? 'font-semibold text-foreground'
                : 'font-medium text-muted-foreground',
            )}
          >
            {notification.title}
          </p>
          {/* Unread dot (compact only) */}
          {compact && !notification.is_read && (
            <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-primary" />
          )}
        </div>

        <p className={cn('mt-0.5 text-xs line-clamp-2', compact ? 'text-muted-foreground/80' : 'text-muted-foreground')}>
          {notification.message}
        </p>

        <div className="mt-1.5 flex items-center gap-2">
          <time className="text-[11px] text-muted-foreground/70">{relativeTime}</time>
          <Badge
            variant="secondary"
            className="h-4 rounded px-1.5 text-[10px] font-medium capitalize"
          >
            {categoryLabel}
          </Badge>
        </div>
      </div>
    </div>
  );
}
