import { type LucideIcon, ArrowUpRight, ArrowDownRight, Minus } from 'lucide-react';
import { cn } from '@/lib/utils';
import Link from 'next/link';

interface StatCardProps {
  title: string;
  value: string | number;
  change?: string;
  changeType?: 'positive' | 'negative' | 'neutral';
  icon?: LucideIcon;
  href?: string;
  className?: string;
}

export function StatCard({ title, value, change, changeType = 'neutral', icon: Icon, href, className }: StatCardProps) {
  const content = (
    <>
      <div className="flex items-center justify-between mb-4">
        <p className="text-sm font-medium text-muted-foreground">{title}</p>
        {Icon && (
          <div className="flex h-10 w-10 items-center justify-center rounded-full bg-primary/10">
            <Icon className="h-5 w-5 text-primary" />
          </div>
        )}
      </div>
      <div className="flex items-baseline gap-2">
        <h2 className="text-3xl font-bold tracking-tight">{value}</h2>
      </div>
      {change && (
        <div className="mt-3 flex items-center text-xs">
          <span className={cn('flex items-center font-medium', {
            'text-emerald-500': changeType === 'positive',
            'text-rose-500': changeType === 'negative',
            'text-muted-foreground': changeType === 'neutral',
          })}>
            {changeType === 'positive' && <ArrowUpRight className="mr-1 h-3 w-3" />}
            {changeType === 'negative' && <ArrowDownRight className="mr-1 h-3 w-3" />}
            {changeType === 'neutral' && <Minus className="mr-1 h-3 w-3" />}
            {change}
          </span>
          <span className="ml-2 text-muted-foreground">vs last month</span>
        </div>
      )}
    </>
  );

  const baseClasses = cn(
    'block rounded-2xl border border-border/50 bg-card p-6 shadow-sm transition-all duration-300',
    href && 'hover:shadow-lg hover:border-primary/30 hover:-translate-y-1 cursor-pointer active:scale-[0.98]',
    className
  );

  if (href) {
    return (
      <Link href={href} className={baseClasses}>
        {content}
      </Link>
    );
  }

  return (
    <div className={baseClasses}>
      {content}
    </div>
  );
}

interface MetricCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon?: LucideIcon;
  className?: string;
}

export function MetricCard({ title, value, subtitle, icon: Icon, className }: MetricCardProps) {
  return (
    <div className={cn('rounded-xl border bg-card p-5 shadow-sm', className)}>
      <div className="flex items-start gap-3">
        {Icon && (
          <div className="rounded-lg bg-primary/10 p-2">
            <Icon className="h-5 w-5 text-primary" />
          </div>
        )}
        <div className="flex-1 min-w-0">
          <p className="text-sm text-muted-foreground">{title}</p>
          <p className="mt-1 text-xl font-semibold truncate">{value}</p>
          {subtitle && <p className="mt-0.5 text-xs text-muted-foreground">{subtitle}</p>}
        </div>
      </div>
    </div>
  );
}

interface InfoCardProps {
  title: string;
  description?: string;
  children?: React.ReactNode;
  className?: string;
}

export function InfoCard({ title, description, children, className }: InfoCardProps) {
  return (
    <div className={cn('rounded-xl border bg-card p-6 shadow-sm', className)}>
      <h3 className="text-sm font-medium">{title}</h3>
      {description && <p className="mt-1 text-sm text-muted-foreground">{description}</p>}
      {children && <div className="mt-4">{children}</div>}
    </div>
  );
}

interface ActionCardProps {
  title: string;
  description?: string;
  action?: React.ReactNode;
  children?: React.ReactNode;
  className?: string;
}

export function ActionCard({ title, description, action, children, className }: ActionCardProps) {
  return (
    <div className={cn('rounded-xl border bg-card p-6 shadow-sm', className)}>
      <div className="flex items-start justify-between gap-4">
        <div>
          <h3 className="text-sm font-medium">{title}</h3>
          {description && <p className="mt-1 text-sm text-muted-foreground">{description}</p>}
        </div>
        {action}
      </div>
      {children && <div className="mt-4">{children}</div>}
    </div>
  );
}
