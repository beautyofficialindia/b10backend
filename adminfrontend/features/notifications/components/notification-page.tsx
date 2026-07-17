'use client';

import { useState, useMemo } from 'react';
import { CheckCheck, Trash2, ChevronLeft, ChevronRight } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { cn } from '@/lib/utils';
import { NotificationList } from './notification-list';
import {
  useNotifications,
  useMarkAllRead,
  useDeleteAllRead,
  useUnreadCount,
} from '../hooks/use-notifications';
import type { NotificationCategory } from '../types';
import { NOTIFICATION_CATEGORY_LABELS } from '../types';

type TabValue = 'ALL' | NotificationCategory;

export function NotificationPage() {
  const [activeCategory, setActiveCategory] = useState<TabValue>('ALL');
  const [page, setPage] = useState(1);

  const { data, isLoading, error } = useNotifications(
    activeCategory === 'ALL' ? undefined : activeCategory,
    page,
  );
  const { data: countData } = useUnreadCount();
  const markAllRead = useMarkAllRead();
  const deleteAllRead = useDeleteAllRead();

  const unreadCount = countData?.unread_count ?? 0;
  const totalPages = data ? Math.ceil(data.count / 20) : 1;

  // Build dynamic category tabs from available_categories (server-provided)
  const availableTabs = useMemo<Array<{ value: TabValue; label: string; count: number }>>(() => {
    const tabs: Array<{ value: TabValue; label: string; count: number }> = [
      { value: 'ALL', label: 'All', count: data?.count ?? 0 },
    ];
    (data?.available_categories ?? []).forEach(({ category, count }) => {
      tabs.push({
        value: category,
        label: NOTIFICATION_CATEGORY_LABELS[category] ?? category,
        count,
      });
    });
    return tabs;
  }, [data]);

  const handleCategoryChange = (tab: TabValue) => {
    setActiveCategory(tab);
    setPage(1);
  };

  const handleMarkAllRead = () => {
    markAllRead.mutate();
  };

  const handleDeleteAllRead = () => {
    deleteAllRead.mutate(undefined, {
      onSuccess: () => setPage(1),
    });
  };

  return (
    <div className="flex flex-col h-full min-h-0">
      {/* Page header */}
      <div className="flex items-center justify-between px-6 py-5 border-b border-border/60">
        <div>
          <h1 className="text-xl font-semibold text-foreground">Notifications</h1>
          <p className="text-sm text-muted-foreground mt-0.5">
            {unreadCount > 0
              ? `${unreadCount} unread notification${unreadCount === 1 ? '' : 's'}`
              : 'All caught up'}
          </p>
        </div>

        {/* Action buttons */}
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            className="gap-1.5 text-xs"
            onClick={handleMarkAllRead}
            disabled={markAllRead.isPending || unreadCount === 0}
          >
            <CheckCheck className="h-3.5 w-3.5" />
            Mark all read
          </Button>
          <Button
            variant="outline"
            size="sm"
            className="gap-1.5 text-xs text-destructive hover:text-destructive"
            onClick={handleDeleteAllRead}
            disabled={deleteAllRead.isPending}
          >
            <Trash2 className="h-3.5 w-3.5" />
            Delete all read
          </Button>
        </div>
      </div>

      {/* Category filter tabs — dynamic, only show non-empty categories */}
      <div className="flex items-center gap-1 px-4 py-3 border-b border-border/60 overflow-x-auto">
        {availableTabs.map((tab) => (
          <button
            key={tab.value}
            onClick={() => handleCategoryChange(tab.value)}
            className={cn(
              'inline-flex items-center gap-1.5 px-3 py-1.5 rounded-md text-sm font-medium transition-colors whitespace-nowrap',
              activeCategory === tab.value
                ? 'bg-primary text-primary-foreground'
                : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground',
            )}
          >
            {tab.label}
            {tab.count > 0 && (
              <Badge
                variant={activeCategory === tab.value ? 'secondary' : 'outline'}
                className="h-4.5 rounded px-1.5 text-[10px] font-semibold"
              >
                {tab.count}
              </Badge>
            )}
          </button>
        ))}
      </div>

      {/* Notification list */}
      <div className="flex-1 overflow-y-auto">
        <NotificationList
          notifications={data?.results ?? []}
          isLoading={isLoading}
          error={error}
        />
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <>
          <Separator />
          <div className="flex items-center justify-between px-6 py-3">
            <p className="text-xs text-muted-foreground">
              Page {page} of {totalPages} &middot; {data?.count ?? 0} total
            </p>
            <div className="flex items-center gap-1">
              <Button
                variant="outline"
                size="icon"
                className="h-8 w-8"
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page === 1}
              >
                <ChevronLeft className="h-4 w-4" />
              </Button>
              <Button
                variant="outline"
                size="icon"
                className="h-8 w-8"
                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                disabled={page === totalPages}
              >
                <ChevronRight className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
