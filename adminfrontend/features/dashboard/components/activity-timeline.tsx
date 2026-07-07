import { MessageSquare, CheckCircle2, BookOpen, UserPlus, Settings } from 'lucide-react';
import { cn } from '@/lib/utils';

interface ActivityItem {
  id: number;
  action: string;
  description: string;
  time: string;
  type: 'lead' | 'qualified' | 'knowledge' | 'user' | 'settings';
}

const typeConfig = {
  lead: { icon: MessageSquare, color: 'text-blue-500 bg-blue-50 dark:bg-blue-950/50' },
  qualified: { icon: CheckCircle2, color: 'text-emerald-500 bg-emerald-50 dark:bg-emerald-950/50' },
  knowledge: { icon: BookOpen, color: 'text-purple-500 bg-purple-50 dark:bg-purple-950/50' },
  user: { icon: UserPlus, color: 'text-amber-500 bg-amber-50 dark:bg-amber-950/50' },
  settings: { icon: Settings, color: 'text-gray-500 bg-gray-50 dark:bg-gray-800' },
};

interface ActivityTimelineProps {
  items: ActivityItem[];
  className?: string;
}

export function ActivityTimeline({ items, className }: ActivityTimelineProps) {
  return (
    <div className={cn('space-y-1', className)}>
      {items.map((item) => {
        const config = typeConfig[item.type];
        const Icon = config.icon;
        return (
          <div key={item.id} className="flex items-start gap-3 rounded-lg p-2.5 hover:bg-muted/50 transition-colors">
            <div className={cn('rounded-lg p-1.5 shrink-0', config.color)}>
              <Icon className="h-3.5 w-3.5" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium truncate">{item.action}</p>
              <p className="text-xs text-muted-foreground truncate">{item.description}</p>
            </div>
            <span className="text-xs text-muted-foreground whitespace-nowrap">{item.time}</span>
          </div>
        );
      })}
    </div>
  );
}
