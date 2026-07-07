'use client';

import Link from 'next/link';
import { useAuth } from '@/features/auth';
import { PageContainer } from '@/components/layout';
import { StatCard, StatusBadge, SkeletonCard, ErrorState } from '@/components/common';
import { DataTable, type Column } from '@/components/tables';
import { LineChartCard, BarChartCard } from '@/components/charts';
import { useDashboardStats, useLeadSummary, useFunnel, useRecentLeads } from '@/features/dashboard/hooks/use-dashboard';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import { Users, TrendingUp, Target, Percent, Plus, BookOpen, Settings, UserPlus } from 'lucide-react';
import type { Lead } from '@/features/dashboard/types';

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
        <div className="flex gap-2 mt-3 sm:mt-0">
          <Link href="/leads">
            <Button size="sm"><Plus className="mr-1.5 h-3.5 w-3.5" />New Lead</Button>
          </Link>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {stats.isLoading ? (
          Array.from({ length: 4 }).map((_, i) => <SkeletonCard key={i} />)
        ) : stats.isError ? (
          <div className="col-span-full"><ErrorState message="Failed to load statistics" onRetry={() => stats.refetch()} /></div>
        ) : stats.data ? (
          <>
            <StatCard title="Total Leads" value={stats.data.total_leads.toLocaleString()} icon={Target} />
            <StatCard title="Qualified Leads" value={stats.data.qualified_leads.toLocaleString()} icon={TrendingUp} />
            <StatCard title="Converted" value={stats.data.converted_leads.toLocaleString()} icon={Users} />
            <StatCard title="Conversion Rate" value={`${stats.data.conversion_rate}%`} icon={Percent} />
          </>
        ) : null}
      </div>

      {/* Charts Row */}
      <div className="grid gap-4 lg:grid-cols-2">
        {/* Funnel Chart */}
        {funnel.isLoading ? (
          <div className="rounded-xl border bg-card p-6 shadow-sm">
            <Skeleton className="h-4 w-32 mb-4" />
            <Skeleton className="h-[200px] w-full" />
          </div>
        ) : funnel.isError ? (
          <div className="rounded-xl border bg-card p-6 shadow-sm">
            <ErrorState message="Failed to load funnel" onRetry={() => funnel.refetch()} />
          </div>
        ) : (
          <BarChartCard title="Qualification Funnel" description="Lead progression stages">
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
          </BarChartCard>
        )}

        {/* Lead Summary */}
        {leadSummary.isLoading ? (
          <div className="rounded-xl border bg-card p-6 shadow-sm">
            <Skeleton className="h-4 w-32 mb-4" />
            <Skeleton className="h-[200px] w-full" />
          </div>
        ) : leadSummary.isError ? (
          <div className="rounded-xl border bg-card p-6 shadow-sm">
            <ErrorState message="Failed to load lead summary" onRetry={() => leadSummary.refetch()} />
          </div>
        ) : (
          <LineChartCard title="Leads by Status" description="Current distribution">
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
          </LineChartCard>
        )}
      </div>

      {/* Quick Actions */}
      <div className="grid gap-4 lg:grid-cols-3">
        <div className="lg:col-span-2">
          {/* Recent Leads Table */}
          <div className="rounded-xl border bg-card shadow-sm">
            <div className="p-4 border-b flex items-center justify-between">
              <h3 className="text-sm font-medium">Recent Leads</h3>
              <Link href="/leads">
                <Button variant="ghost" size="sm">View all</Button>
              </Link>
            </div>
            <div className="p-4">
              <DataTable
                columns={leadsColumns}
                data={recentLeads.data?.results || []}
                isLoading={recentLeads.isLoading}
                emptyMessage="No leads yet"
              />
              {recentLeads.isError && (
                <ErrorState message="Failed to load leads" onRetry={() => recentLeads.refetch()} />
              )}
            </div>
          </div>
        </div>

        <div className="rounded-xl border bg-card p-4 shadow-sm space-y-3">
          <h3 className="text-sm font-medium">Quick Actions</h3>
          <div className="grid grid-cols-2 gap-2">
            {[
              { label: 'New Lead', icon: Plus, href: '/leads' },
              { label: 'Knowledge', icon: BookOpen, href: '/knowledge' },
              { label: 'Users', icon: UserPlus, href: '/users' },
              { label: 'Settings', icon: Settings, href: '/settings' },
            ].map((item) => (
              <Link
                key={item.label}
                href={item.href}
                className="flex flex-col items-center gap-2 rounded-lg border p-3 text-center text-xs font-medium hover:bg-muted/50 transition-colors"
              >
                <item.icon className="h-5 w-5 text-muted-foreground" />
                {item.label}
              </Link>
            ))}
          </div>
        </div>
      </div>
    </PageContainer>
  );
}
