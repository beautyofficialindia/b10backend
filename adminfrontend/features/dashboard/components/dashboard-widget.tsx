import { ReactNode } from 'react';
import { PermissionGuard } from '@/features/auth';
import { ErrorState, EmptyState } from '@/components/common';
import { Skeleton } from '@/components/ui/skeleton';
import { Inbox } from 'lucide-react';
import { cn } from '@/lib/utils';

interface DashboardWidgetProps {
  title?: string;
  description?: string;
  permissions?: readonly string[];
  requireAll?: boolean;
  isLoading?: boolean;
  isError?: boolean;
  isEmpty?: boolean;
  emptyMessage?: string;
  onRetry?: () => void;
  className?: string;
  action?: ReactNode;
  children: ReactNode;
  loadingFallback?: ReactNode;
}

export function DashboardWidget({
  title,
  description,
  permissions = [],
  requireAll = true,
  isLoading,
  isError,
  isEmpty,
  emptyMessage = "No data available",
  onRetry,
  className,
  action,
  children,
  loadingFallback,
}: DashboardWidgetProps) {
  const content = () => {
    if (isLoading) {
      return loadingFallback || <Skeleton className="h-[200px] w-full rounded-xl" />;
    }

    if (isError) {
      return <ErrorState message="Failed to load widget" onRetry={onRetry} />;
    }

    if (isEmpty) {
      return <EmptyState icon={Inbox} title={emptyMessage} className="min-h-[200px]" />;
    }

    return children;
  };

  const hasHeader = title || description || action;

  return (
    <PermissionGuard permissions={permissions} requireAll={requireAll}>
      <div className={cn('rounded-xl border bg-card p-6 shadow-sm flex flex-col', className)}>
        {hasHeader && (
          <div className="flex items-start justify-between mb-4">
            <div>
              {title && <h3 className="text-sm font-medium">{title}</h3>}
              {description && <p className="text-xs text-muted-foreground mt-0.5">{description}</p>}
            </div>
            {action && <div>{action}</div>}
          </div>
        )}
        <div className="flex-1 relative">
          {content()}
        </div>
      </div>
    </PermissionGuard>
  );
}
