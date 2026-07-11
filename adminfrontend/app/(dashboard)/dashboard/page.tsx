'use client';

import Link from 'next/link';
import { useAuth, PermissionGuard } from '@/features/auth';
import { PageContainer } from '@/components/layout';
import { StatCard, StatusBadge } from '@/components/common';
import { DataTable, type Column } from '@/components/tables';
import { useDashboardStats, useLeadSummary, useFunnel, useRecentLeads } from '@/features/dashboard/hooks/use-dashboard';
import { Button } from '@/components/ui/button';
import { Users, TrendingUp, Target, Percent, BookOpen, Settings, UserPlus } from 'lucide-react';
import type { Lead } from '@/features/dashboard/types';
import { DashboardWidget } from '@/features/dashboard/components/dashboard-widget';
import { WIDGET_REGISTRY } from '@/features/dashboard/constants';

const leadsColumns: Column<Lead>[] = [
  { key: 'full_name', header: 'Name', render: (row) => (
    <div>
      <p className="text-sm font-medium">{row.full_name || '—'}</p>
      <p className="text-xs text-muted-foreground">{row.email || ''}</p>
    </div>
  )},
  { key: 'company_name', header: 'Company', render: (row) => <span>{row.company_name || '—'}</span> },
  { key: 'project_type', header: 'Project', render: (row) => <span>{row.project_type || '—'}</span> },
  { key: 'status', header: 'Status', render: (row) => (
    <StatusBadge status={row.status === 'qualified' || row.status === 'converted' ? 'active' : row.status === 'lost' ? 'error' : 'pending'} label={row.status} />
  )},
  { key: 'created_at', header: 'Created', render: (row) => (
    <span className="text-xs text-muted-foreground">{new Date(row.created_at).toLocaleDateString()}</span>
  )},
];

export default function DashboardPage() {
  const { user } = useAuth();
  const stats = useDashboardStats();
  const leadSummary = useLeadSummary();
  const funnel = useFunnel();
  const recentLeads = useRecentLeads();

  const greeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 18) return 'Good afternoon';
    return 'Good evening';
  };

  return (
    <PageContainer>
      {/* Welcome Header */}
      <div className="flex flex-col gap-1 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">
            {greeting()}, {user?.first_name || user?.username}
          </h1>
          <p className="text-sm text-muted-foreground">
            {new Date().toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}
          </p>
        </div>
      </div>

      {/* KPI Cards Row */}
      <DashboardWidget
        permissions={WIDGET_REGISTRY.kpiCards.permissions}
        isLoading={stats.isLoading}
        isError={stats.isError}
        onRetry={() => stats.refetch()}
        className="p-0 border-0 shadow-none bg-transparent"
        loadingFallback={
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {Array.from({ length: 4 }).map((_, i) => (
              <div key={i} className="h-28 rounded-xl bg-card border shadow-sm animate-pulse" />
            ))}
          </div>
        }
      >
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <StatCard title="Total Leads" value={stats.data?.total_leads.toLocaleString() || '0'} icon={Target} />
          <StatCard title="Qualified Leads" value={stats.data?.qualified_leads.toLocaleString() || '0'} icon={TrendingUp} />
          <StatCard title="Converted" value={stats.data?.converted_leads.toLocaleString() || '0'} icon={Users} />
          <StatCard title="Conversion Rate" value={`${stats.data?.conversion_rate || 0}%`} icon={Percent} />
        </div>
      </DashboardWidget>

      {/* Charts Row */}
      <div className="grid gap-4 lg:grid-cols-2 mt-4">
        <DashboardWidget
          title="Qualification Funnel"
          description="Lead progression stages"
          permissions={WIDGET_REGISTRY.funnelChart.permissions}
          isLoading={funnel.isLoading}
          isError={funnel.isError}
          onRetry={() => funnel.refetch()}
        >
          <div className="flex flex-col justify-center h-full gap-3 px-2">
            {funnel.data?.map((stage) => (
              <div key={stage.stage} className="flex items-center gap-3">
                <span className="text-xs text-muted-foreground w-28 shrink-0 truncate">{stage.stage}</span>
                <div className="flex-1 h-5 rounded bg-muted overflow-hidden">
                  <div
                    className="h-full rounded bg-primary/70 transition-all"
                    style={{ width: `${Math.min((stage.value / Math.max(...(funnel.data?.map(s => s.value) || [1]))) * 100, 100)}%` }}
                  />
                </div>
                <span className="text-xs font-medium w-8 text-right">{stage.value}</span>
              </div>
            ))}
          </div>
        </DashboardWidget>

        <DashboardWidget
          title="Leads by Status"
          description="Current distribution"
          permissions={WIDGET_REGISTRY.timelineChart.permissions}
          isLoading={leadSummary.isLoading}
          isError={leadSummary.isError}
          onRetry={() => leadSummary.refetch()}
        >
          <div className="flex flex-col justify-center h-full gap-3 px-2">
            {leadSummary.data && Object.entries(leadSummary.data)
              .filter(([key]) => key !== 'total_leads')
              .map(([key, value]) => (
                <div key={key} className="flex items-center gap-3">
                  <span className="text-xs text-muted-foreground w-20 shrink-0 capitalize">{key}</span>
                  <div className="flex-1 h-5 rounded bg-muted overflow-hidden">
                    <div
                      className="h-full rounded bg-primary/70 transition-all"
                      style={{ width: `${leadSummary.data.total_leads > 0 ? (Number(value) / leadSummary.data.total_leads) * 100 : 0}%` }}
                    />
                  </div>
                  <span className="text-xs font-medium w-6 text-right">{value}</span>
                </div>
              ))}
          </div>
        </DashboardWidget>
      </div>

      {/* Data Row */}
      <div className="grid gap-4 lg:grid-cols-3 mt-4">
        <div className="lg:col-span-2">
          <DashboardWidget
            title="Recent Leads"
            permissions={WIDGET_REGISTRY.recentLeads.permissions}
            isLoading={recentLeads.isLoading}
            isError={recentLeads.isError}
            onRetry={() => recentLeads.refetch()}
            className="p-4"
            action={
              <Link href="/leads">
                <Button variant="ghost" size="sm">View all</Button>
              </Link>
            }
          >
            <div className="-mx-4 mt-2">
              <DataTable
                columns={leadsColumns}
                data={recentLeads.data?.results || []}
                isLoading={false} // Handled by wrapper
                emptyMessage="No leads yet"
              />
            </div>
          </DashboardWidget>
        </div>

        <div className="rounded-xl border bg-card p-4 shadow-sm space-y-3 h-fit">
          <h3 className="text-sm font-medium">Quick Actions</h3>
          <div className="grid grid-cols-2 gap-2">
            {[
              { label: 'Knowledge', icon: BookOpen, href: '/knowledge', reqs: ['knowledge_base.view_kbentry'] },
              { label: 'Users', icon: UserPlus, href: '/users', reqs: ['auth.view_user'] },
              { label: 'Settings', icon: Settings, href: '/settings', reqs: ['core.view_setting'] },
            ].map((item) => (
              <PermissionGuard key={item.label} permissions={item.reqs}>
                <Link
                  href={item.href}
                  className="flex flex-col items-center gap-2 rounded-lg border p-3 text-center text-xs font-medium hover:bg-muted/50 transition-colors"
                >
                  <item.icon className="h-5 w-5 text-muted-foreground" />
                  {item.label}
                </Link>
              </PermissionGuard>
            ))}
          </div>
        </div>
      </div>
    </PageContainer>
  );
}
