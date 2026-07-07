import { cn } from '@/lib/utils';

interface ChartCardProps {
  title: string;
  description?: string;
  children: React.ReactNode;
  className?: string;
  action?: React.ReactNode;
}

function ChartCardWrapper({ title, description, children, className, action }: ChartCardProps) {
  return (
    <div className={cn('rounded-xl border bg-card p-6 shadow-sm', className)}>
      <div className="flex items-start justify-between mb-4">
        <div>
          <h3 className="text-sm font-medium">{title}</h3>
          {description && <p className="text-xs text-muted-foreground mt-0.5">{description}</p>}
        </div>
        {action}
      </div>
      <div className="h-[200px] w-full">{children}</div>
    </div>
  );
}

export function LineChartCard(props: ChartCardProps) {
  return <ChartCardWrapper {...props} />;
}

export function BarChartCard(props: ChartCardProps) {
  return <ChartCardWrapper {...props} />;
}

export function PieChartCard(props: ChartCardProps) {
  return <ChartCardWrapper {...props} />;
}
