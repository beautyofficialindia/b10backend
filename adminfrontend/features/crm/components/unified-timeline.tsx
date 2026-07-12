import React from 'react';
import { PermissionGuard } from '@/features/auth';
import { Skeleton } from '@/components/ui/skeleton';
import { ErrorState } from '@/components/common';
import type { TimelineItem } from '../types';

interface UnifiedTimelineProps {
  items: TimelineItem[];
  isLoading?: boolean;
  isError?: boolean;
  onRetry?: () => void;
}

function groupItemsByDate(items: TimelineItem[]) {
  const groups: Record<string, TimelineItem[]> = {
    'Today': [],
    'Yesterday': [],
    'Older': [],
  };

  const today = new Date();
  today.setHours(0, 0, 0, 0);

  const yesterday = new Date(today);
  yesterday.setDate(yesterday.getDate() - 1);

  items.forEach(item => {
    const itemDate = new Date(item.timestamp);
    itemDate.setHours(0, 0, 0, 0);

    if (itemDate.getTime() === today.getTime()) {
      groups['Today'].push(item);
    } else if (itemDate.getTime() === yesterday.getTime()) {
      groups['Yesterday'].push(item);
    } else {
      groups['Older'].push(item);
    }
  });

  return groups;
}

export function UnifiedTimeline({ items, isLoading, isError, onRetry }: UnifiedTimelineProps) {
  if (isError) {
    return (
      <div className="rounded-lg border p-8">
        <ErrorState title="Failed to load timeline" message="There was a problem fetching the timeline events." onRetry={onRetry} />
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="space-y-6">
        {[1, 2, 3].map(i => (
          <div key={i} className="flex gap-4">
            <Skeleton className="h-10 w-10 rounded-full shrink-0" />
            <div className="space-y-2 flex-1">
              <Skeleton className="h-5 w-1/3" />
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-3 w-20" />
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (items.length === 0) {
    return (
      <div className="rounded-lg border p-8 text-center text-muted-foreground">
        <p className="text-sm font-medium">No activity yet</p>
        <p className="text-xs mt-1">Timeline events will appear here.</p>
      </div>
    );
  }

  const sortedItems = [...items].sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());
  const groupedItems = groupItemsByDate(sortedItems);

  return (
    <PermissionGuard permissions={["crm.view_leadactivity"]}>
      <div className="space-y-8">
        {Object.entries(groupedItems).map(([group, groupItems]) => {
          if (groupItems.length === 0) return null;
          
          return (
            <div key={group}>
              <h4 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-4">
                {group}
              </h4>
              <div className="space-y-6">
                {groupItems.map((item, idx) => {
                  const isLast = idx === groupItems.length - 1;
                  return (
                    <div key={item.id} className="relative flex gap-4">
                      {/* Vertical line connecting items */}
                      {!isLast && (
                        <div className="absolute left-5 top-10 bottom-[-24px] w-[2px] bg-border" />
                      )}
                      
                      {/* Icon */}
                      <div className="relative z-10 flex h-10 w-10 shrink-0 items-center justify-center rounded-full border bg-background shadow-sm">
                        <item.icon className="h-4 w-4 text-muted-foreground" />
                      </div>
                      
                      {/* Content */}
                      <div className="flex-1 pb-1 pt-1.5 min-w-0">
                        <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-1 mb-1">
                          <p className="text-sm font-medium">{item.title}</p>
                          <time className="text-xs text-muted-foreground shrink-0" dateTime={item.timestamp}>
                            {new Date(item.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                          </time>
                        </div>
                        {item.description && (
                          <p className="text-sm text-muted-foreground mb-2 break-words">{item.description}</p>
                        )}
                        <p className="text-[11px] text-muted-foreground">By {item.actor}</p>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          );
        })}
      </div>
    </PermissionGuard>
  );
}
