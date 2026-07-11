'use client';

import Link from 'next/link';
import { useAuth, PermissionGuard } from '@/features/auth';
import { PageContainer } from '@/components/layout';
import { StatCard, StatusBadge } from '@/components/common';
import { DataTable, type Column } from '@/components/tables';
import { useDashboardStats, useLeadSummary, useFunnel, useRecentLeads, useAnalyticsTimeline } from '@/features/dashboard/hooks/use-dashboard';
import { Button } from '@/components/ui/button';
import { Users, TrendingUp, Target, Percent, BookOpen, Settings, UserPlus, MessageCircle, MessageSquare, AlertCircle } from 'lucide-react';
import type { Lead } from '@/features/dashboard/types';
import { DashboardWidget, FunnelChart, StatusChart, TimelineChart } from '@/features/dashboard/components';
import { WIDGET_REGISTRY } from '@/features/dashboard/constants';
import { cn } from '@/lib/utils';
import { useRouter } from 'next/navigation';

const leadsColumns: Column<Lead>[] = [
  { key: 'full_name', header: 'Name', render: (row) => {
    const initials = (row.full_name || 'U').substring(0, 2).toUpperCase();
    return (
      <div className="flex items-center gap-3">
        <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-primary/20 text-xs font-semibold text-primary">
          {initials}
        </div>
        <div>
          <p className="text-sm font-medium">{row.full_name || '—'}</p>
          <p className="text-xs text-muted-foreground">{row.email || ''}</p>
        </div>
      </div>
    );
  }},
  { key: 'company_name', header: 'Company', render: (row) => <span className="font-medium text-muted-foreground">{row.company_name || '—'}</span> },
  { key: 'project_type', header: 'Project', render: (row) => <span className="font-medium text-muted-foreground">{row.project_type || '—'}</span> },
  { key: 'status', header: 'Status', render: (row) => {
    const statusMap = {
      gathering: { label: 'Gathering', color: 'bg-blue-500/10 text-blue-500 border-blue-500/20' },
      qualified: { label: 'Qualified', color: 'bg-green-500/10 text-green-500 border-green-500/20' },
      converted: { label: 'Converted', color: 'bg-orange-500/10 text-orange-500 border-orange-500/20' },
      lost: { label: 'Lost', color: 'bg-red-500/10 text-red-500 border-red-500/20' },
      escalated: { label: 'Escalated', color: 'bg-purple-500/10 text-purple-500 border-purple-500/20' },
    };
    const s = statusMap[row.status as keyof typeof statusMap] || statusMap.gathering;
    return (
      <span className={cn("px-2.5 py-1 rounded-md text-[11px] font-semibold tracking-wide uppercase border", s.color)}>
        {s.label}
      </span>
    );
  }},
  { key: 'created_at', header: 'Created', render: (row) => (
    <span className="text-xs font-medium text-muted-foreground">{new Date(row.created_at).toLocaleDateString()}</span>
  )},
];

export default function DashboardPage() {
  const { user } = useAuth();
  const router = useRouter();

  const hasPerm = (perms: readonly string[]) => {
    if (user?.is_superuser) return true;
    if (perms.length === 0) return true;
    return perms.some((p) => user?.permissions?.includes(p));
  };

  const stats = useDashboardStats(hasPerm(WIDGET_REGISTRY.kpiCards.permissions));
  const leadSummary = useLeadSummary(hasPerm(WIDGET_REGISTRY.timelineChart.permissions));
  const funnel = useFunnel(hasPerm(WIDGET_REGISTRY.funnelChart.permissions));
  const recentLeads = useRecentLeads(hasPerm(WIDGET_REGISTRY.recentLeads.permissions));
  const timeline = useAnalyticsTimeline(hasPerm(WIDGET_REGISTRY.timelineChart.permissions));

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
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4 xl:grid-cols-4">
          <StatCard title="Total Leads" value={stats.data?.total_leads.toLocaleString() || '0'} icon={Target} change="+12.5%" changeType="positive" href="/leads" />
          <StatCard title="Qualified Leads" value={stats.data?.qualified_leads.toLocaleString() || '0'} icon={TrendingUp} change="+5.2%" changeType="positive" href="/leads?status=qualified" />
          <StatCard title="Converted Leads" value={stats.data?.converted_leads.toLocaleString() || '0'} icon={Users} change="+3.1%" changeType="positive" href="/leads?status=converted" />
          <StatCard title="Lost Leads" value={stats.data?.lost_leads?.toLocaleString() || '0'} icon={AlertCircle} change="-2.1%" changeType="negative" href="/leads?status=lost" />
          
          <StatCard title="Total Chats" value={stats.data?.total_chats?.toLocaleString() || '0'} icon={MessageCircle} change="+8.4%" changeType="positive" href="/analytics" />
          <StatCard title="Total Messages" value={stats.data?.total_messages?.toLocaleString() || '0'} icon={MessageSquare} change="+15.2%" changeType="positive" href="/analytics" />
          <StatCard title="Qualification Rate" value={`${stats.data?.qualification_rate || 0}%`} icon={Percent} change="+2.4%" changeType="positive" href="/analytics" />
          <StatCard title="Conversion Rate" value={`${stats.data?.conversion_rate || 0}%`} icon={Percent} change="+1.4%" changeType="positive" href="/analytics" />
        </div>
      </DashboardWidget>

      {/* Timeline Row */}
      <div className="mt-4">
        <DashboardWidget
          title="Analytics Timeline"
          description="Activity over time"
          permissions={WIDGET_REGISTRY.timelineChart.permissions}
          isLoading={timeline.isLoading}
          isError={timeline.isError}
          isEmpty={!timeline.isLoading && (!timeline.data || Object.keys(timeline.data).length === 0)}
          emptyMessage="No timeline data available"
          onRetry={() => timeline.refetch()}
        >
          <TimelineChart data={timeline.data} />
        </DashboardWidget>
      </div>

      {/* Charts Row */}
      <div className="grid gap-4 lg:grid-cols-2 mt-4">
        <DashboardWidget
          title="Qualification Funnel"
          description="Lead progression stages"
          permissions={WIDGET_REGISTRY.funnelChart.permissions}
          isLoading={funnel.isLoading}
          isError={funnel.isError}
          isEmpty={!funnel.isLoading && (!funnel.data || funnel.data.length === 0)}
          emptyMessage="No funnel data available"
          onRetry={() => funnel.refetch()}
          action={
            <select className="text-xs border border-border/50 bg-background rounded-md px-2 py-1 text-muted-foreground outline-none focus:ring-1 focus:ring-primary cursor-pointer hover:bg-accent transition-colors">
              <option>This Month</option>
              <option>Last 30 Days</option>
              <option>This Quarter</option>
            </select>
          }
        >
          <FunnelChart data={funnel.data} />
        </DashboardWidget>

        <DashboardWidget
          title="Leads by Status"
          description="Current distribution"
          permissions={WIDGET_REGISTRY.timelineChart.permissions}
          isLoading={leadSummary.isLoading}
          isError={leadSummary.isError}
          isEmpty={!leadSummary.isLoading && (!leadSummary.data || Object.keys(leadSummary.data).length <= 1)} // total_leads is always present
          emptyMessage="No leads found"
          onRetry={() => leadSummary.refetch()}
        >
          <StatusChart data={leadSummary.data} />
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
            isEmpty={!recentLeads.isLoading && (!recentLeads.data?.results || recentLeads.data.results.length === 0)}
            emptyMessage="No recent leads found"
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
                onRowClick={(row) => router.push(`/leads/${row.id}`)}
              />
            </div>
          </DashboardWidget>
        </div>

        <div className="rounded-2xl border border-border/50 bg-card p-6 shadow-sm space-y-4 h-fit">
          <h3 className="text-sm font-medium text-muted-foreground">Quick Actions</h3>
          <div className="grid grid-cols-2 gap-3">
            {[
              { label: 'Knowledge', icon: BookOpen, href: '/knowledge', reqs: ['knowledge_base.view_kbentry'], color: 'from-purple-500/10 to-purple-500/0 hover:from-purple-500/20 text-purple-500 border-purple-500/20' },
              { label: 'Users', icon: UserPlus, href: '/users', reqs: ['auth.view_user'], color: 'from-blue-500/10 to-blue-500/0 hover:from-blue-500/20 text-blue-500 border-blue-500/20' },
              { label: 'Leads', icon: Target, href: '/leads', reqs: ['leads.view_lead'], color: 'from-green-500/10 to-green-500/0 hover:from-green-500/20 text-green-500 border-green-500/20' },
              { label: 'Analytics', icon: TrendingUp, href: '/analytics', reqs: ['analytics.view_analyticsevent'], color: 'from-orange-500/10 to-orange-500/0 hover:from-orange-500/20 text-orange-500 border-orange-500/20' },
              { label: 'Settings', icon: Settings, href: '/settings', reqs: ['core.view_setting'], color: 'from-red-500/10 to-red-500/0 hover:from-red-500/20 text-red-500 border-red-500/20' },
            ].map((item) => (
              <PermissionGuard key={item.label} permissions={item.reqs}>
                <Link
                  href={item.href}
                  className={cn(
                    "group relative flex flex-col items-center justify-center gap-3 overflow-hidden rounded-xl border bg-gradient-to-br p-4 text-center transition-all duration-300 hover:scale-[1.03] hover:shadow-md",
                    item.color
                  )}
                >
                  <item.icon className="h-7 w-7 transition-transform duration-300 group-hover:scale-110 group-hover:-translate-y-0.5" />
                  <span className="text-xs font-semibold tracking-wide text-foreground">{item.label}</span>
                </Link>
              </PermissionGuard>
            ))}
          </div>
        </div>
      </div>
    </PageContainer>
  );
}
