'use client';

import Link from 'next/link';
import { CheckCheck, ArrowRight } from 'lucide-react';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';
import { ScrollArea } from '@/components/ui/scroll-area';
import { NotificationBell } from './notification-bell';
import { NotificationCard } from './notification-card';
import { NotificationEmptyState } from './notification-empty-state';
import { useNotifications, useMarkAllRead } from '../hooks/use-notifications';
import type { Notification } from '../types';

const DROPDOWN_LIMIT = 5;

export function NotificationDropdown() {
  const { data, isLoading } = useNotifications(undefined, 1);
  const markAllRead = useMarkAllRead();

  // Sort: unread first, then by created_at desc — take top DROPDOWN_LIMIT
  const results = data?.results ?? [];
  const sorted: Notification[] = [...results]
    .sort((a, b) => {
      if (a.is_read !== b.is_read) return a.is_read ? 1 : -1;
      return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
    })
    .slice(0, DROPDOWN_LIMIT);

  const unread = sorted.filter((n) => !n.is_read);
  const read = sorted.filter((n) => n.is_read);
  const hasUnread = unread.length > 0;

  return (
    <Popover>
      <PopoverTrigger render={<NotificationBell />} />

      <PopoverContent
        align="end"
        sideOffset={8}
        className="w-96 p-0 shadow-lg"
      >
        {/* Header */}
        <div className="flex items-center justify-between px-4 py-3 border-b border-border">
          <h3 className="text-sm font-semibold text-foreground">Notifications</h3>
          {hasUnread && (
            <Button
              variant="ghost"
              size="sm"
              className="h-7 gap-1.5 text-xs text-muted-foreground hover:text-foreground"
              onClick={() => markAllRead.mutate()}
              disabled={markAllRead.isPending}
            >
              <CheckCheck className="h-3.5 w-3.5" />
              Mark all read
            </Button>
          )}
        </div>

        {/* Body */}
        <ScrollArea className="max-h-[420px]">
          {isLoading ? (
            <DropdownSkeleton />
          ) : sorted.length === 0 ? (
            <div className="py-8">
              <NotificationEmptyState variant="all-clear" compact />
            </div>
          ) : (
            <div className="py-1">
              {/* Unread group */}
              {unread.length > 0 && (
                <>
                  <p className="px-4 pt-2 pb-1 text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">
                    Unread
                  </p>
                  {unread.map((n) => (
                    <NotificationCard key={n.id} notification={n} compact />
                  ))}
                </>
              )}

              {/* Read group */}
              {read.length > 0 && (
                <>
                  {unread.length > 0 && <Separator className="my-1" />}
                  <p className="px-4 pt-2 pb-1 text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">
                    Read
                  </p>
                  {read.map((n) => (
                    <NotificationCard key={n.id} notification={n} compact />
                  ))}
                </>
              )}
            </div>
          )}
        </ScrollArea>

        {/* Footer */}
        <div className="border-t border-border">
          <Link
            href="/notifications"
            className="flex items-center justify-center gap-1.5 px-4 py-3 text-sm text-muted-foreground hover:text-foreground hover:bg-accent transition-colors rounded-b-md"
          >
            View all notifications
            <ArrowRight className="h-3.5 w-3.5" />
          </Link>
        </div>
      </PopoverContent>
    </Popover>
  );
}

function DropdownSkeleton() {
  return (
    <div className="space-y-px py-2 px-2">
      {[1, 2, 3].map((i) => (
        <div key={i} className="flex gap-3 rounded-md p-3">
          <div className="h-8 w-8 rounded-full bg-muted animate-pulse shrink-0" />
          <div className="flex-1 space-y-2">
            <div className="h-3.5 w-3/4 rounded bg-muted animate-pulse" />
            <div className="h-3 w-full rounded bg-muted animate-pulse" />
            <div className="h-3 w-1/3 rounded bg-muted animate-pulse" />
          </div>
        </div>
      ))}
    </div>
  );
}
