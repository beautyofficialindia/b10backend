import { Skeleton } from '@/components/ui/skeleton';
import { Clock } from 'lucide-react';

export interface AuditEntry {
  id: number | string;
  description: string;
  actor_username?: string | null;
  created_at: string;
  action: string;
}

interface AuditTimelineProps {
  entries: AuditEntry[];
  isLoading?: boolean;
}

export function AuditTimeline({ entries, isLoading }: AuditTimelineProps) {
  if (isLoading) {
    return (
      <div className="rounded-lg border p-8 text-center">
        <Skeleton className="h-4 w-48 mx-auto" />
      </div>
    );
  }

  if (!entries || entries.length === 0) {
    return (
      <div className="rounded-lg border p-8 text-center text-sm text-muted-foreground">
        No audit entries
      </div>
    );
  }

  return (
    <div className="rounded-lg border divide-y">
      {entries.map((entry) => (
        <div key={entry.id} className="flex items-start gap-3 p-3">
          <Clock className="h-4 w-4 text-muted-foreground mt-0.5 shrink-0" />
          <div className="flex-1 min-w-0">
            <p className="text-sm">{entry.description}</p>
            <p className="text-xs text-muted-foreground mt-0.5">
              by {entry.actor_username || 'System'} · {new Date(entry.created_at).toLocaleString()}
            </p>
          </div>
          <span className="text-[10px] bg-muted px-1.5 py-0.5 rounded shrink-0">{entry.action}</span>
        </div>
      ))}
    </div>
  );
}
