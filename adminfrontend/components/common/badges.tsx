import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';

type StatusVariant = 'active' | 'inactive' | 'pending' | 'error';

const statusStyles: Record<StatusVariant, string> = {
  active: 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400 border-emerald-200 dark:border-emerald-800',
  inactive: 'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-400 border-gray-200 dark:border-gray-700',
  pending: 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400 border-amber-200 dark:border-amber-800',
  error: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400 border-red-200 dark:border-red-800',
};

interface StatusBadgeProps {
  status: StatusVariant;
  label?: string;
  className?: string;
}

export function StatusBadge({ status, label, className }: StatusBadgeProps) {
  return (
    <Badge variant="outline" className={cn('text-xs font-medium', statusStyles[status], className)}>
      <span className={cn('mr-1.5 inline-block h-1.5 w-1.5 rounded-full', {
        'bg-emerald-500': status === 'active',
        'bg-gray-400': status === 'inactive',
        'bg-amber-500': status === 'pending',
        'bg-red-500': status === 'error',
      })} />
      {label || status.charAt(0).toUpperCase() + status.slice(1)}
    </Badge>
  );
}

interface RoleBadgeProps {
  role: string;
  className?: string;
}

export function RoleBadge({ role, className }: RoleBadgeProps) {
  return (
    <Badge variant="secondary" className={cn('text-xs', className)}>
      {role}
    </Badge>
  );
}

type PriorityLevel = 'low' | 'medium' | 'high' | 'critical';

const priorityStyles: Record<PriorityLevel, string> = {
  low: 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400',
  medium: 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400',
  high: 'bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-400',
  critical: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400',
};

interface PriorityBadgeProps {
  priority: PriorityLevel;
  className?: string;
}

export function PriorityBadge({ priority, className }: PriorityBadgeProps) {
  return (
    <Badge variant="outline" className={cn('text-xs font-medium', priorityStyles[priority], className)}>
      {priority.charAt(0).toUpperCase() + priority.slice(1)}
    </Badge>
  );
}
