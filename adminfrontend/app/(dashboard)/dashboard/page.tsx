'use client';

import { useAuth } from '@/features/auth';
import { PageContainer } from '@/components/layout';
import { StatCard, StatusBadge } from '@/components/common';
import { DataTable, type Column } from '@/components/tables';
import { LineChartCard, BarChartCard } from '@/components/charts';
import { ActivityTimeline } from '@/features/dashboard/components';
import { kpiData, leadsOverTime, leadSources, recentActivity, recentLeads } from '@/features/dashboard/mock';
import { Button } from '@/components/ui/button';
import { Users, TrendingUp, Target, Percent, Plus, BookOpen, Settings, UserPlus } from 'lucide-react';
import Link from 'next/link';

const kpiIcons = [Target, TrendingUp, Users, Percent];

const leadsColumns: Column<typeof recentLeads[0]>[] = [
  { key: 'name', header: 'Name', render: (row) => (
    <div>
      <p className="text-sm font-medium">{row.name}</p>
      <p className="text-xs text-muted-foreground">{row.email}</p>
    </div>
  )},
  { key: 'company', header: 'Company' },
  { key: 'project_type', header: 'Project Type' },
  { key: 'status', header: 'Status', render: (row) => (
    <StatusBadge status={row.status === 'qualified' ? 'active' : 'pending'} label={row.status === 'qualified' ? 'Qualified' : 'Gathering'} />
  )},
  { key: 'created', header: 'Created' },
];

export default function DashboardPage() {
  const { user } = useAuth();

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
        {kpiData.map((kpi, i) => (
          <StatCard
            key={kpi.title}
            title={kpi.title}
            value={kpi.value}
            change={kpi.change}
            changeType={kpi.changeType}
            icon={kpiIcons[i]}
          />
        ))}
      </div>

      {/* Charts Row */}
      <div className="grid gap-4 lg:grid-cols-2">
        <LineChartCard title="Leads Over Time" description="Monthly lead generation">
          <div className="flex items-end justify-between h-full px-2 pb-2">
            {leadsOverTime.map((d) => (
              <div key={d.month} className="flex flex-col items-center gap-1">
                <div
                  className="w-8 rounded-t bg-primary/80 transition-all hover:bg-primary"
                  style={{ height: `${(d.leads / 150) * 100}%`, minHeight: 4 }}
                />
                <span className="text-[10px] text-muted-foreground">{d.month}</span>
              </div>
            ))}
          </div>
        </LineChartCard>
        <BarChartCard title="Lead Sources" description="Where leads come from">
          <div className="flex flex-col justify-center h-full gap-3 px-2">
            {leadSources.map((s) => (
              <div key={s.source} className="flex items-center gap-3">
                <span className="text-xs text-muted-foreground w-16 shrink-0">{s.source}</span>
                <div className="flex-1 h-5 rounded bg-muted overflow-hidden">
                  <div
                    className="h-full rounded bg-primary/70 transition-all"
                    style={{ width: `${(s.count / 50) * 100}%` }}
                  />
                </div>
                <span className="text-xs font-medium w-6 text-right">{s.count}</span>
              </div>
            ))}
          </div>
        </BarChartCard>
      </div>

      {/* Activity + Quick Actions */}
      <div className="grid gap-4 lg:grid-cols-3">
        <div className="lg:col-span-2 rounded-xl border bg-card shadow-sm">
          <div className="p-4 border-b">
            <h3 className="text-sm font-medium">Recent Activity</h3>
          </div>
          <div className="p-2">
            <ActivityTimeline items={recentActivity} />
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

      {/* Recent Leads Table */}
      <div className="rounded-xl border bg-card shadow-sm">
        <div className="p-4 border-b">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-medium">Recent Leads</h3>
            <Button variant="ghost" size="sm">
              <Link href="/leads">View all</Link>
            </Button>
          </div>
        </div>
        <div className="p-4">
          <DataTable columns={leadsColumns} data={recentLeads} />
        </div>
      </div>
    </PageContainer>
  );
}
