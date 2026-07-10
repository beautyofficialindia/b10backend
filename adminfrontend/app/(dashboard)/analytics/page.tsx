'use client';

import { PageContainer, PageHeader } from '@/components/layout';
import { StatCard, MetricCard, SkeletonCard, ErrorState } from '@/components/common';
import { BarChartCard, LineChartCard } from '@/components/charts';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import { RefreshCw, Users, TrendingUp, Target, Percent, MessageSquare, Zap, Download } from 'lucide-react';
import { Tooltip, TooltipTrigger, TooltipContent } from '@/components/ui/tooltip';
import { useAnalyticsStats, useAnalyticsTimeline, useAnalyticsFunnel, useLeadSummary } from '@/features/analytics';

export default function AnalyticsPage() {
  const stats = useAnalyticsStats();
  const timeline = useAnalyticsTimeline();
  const funnel = useAnalyticsFunnel();
  const leadSummary = useLeadSummary();

  const refetchAll = () => {
    stats.refetch();
    timeline.refetch();
    funnel.refetch();
    leadSummary.refetch();
  };

  const isFetching = stats.isFetching || timeline.isFetching || funnel.isFetching || leadSummary.isFetching;

  // Process timeline data for chart
  const timelineEntries = timeline.data ? Object.entries(timeline.data).slice(-14) : [];

  return (
    <PageContainer>
      <PageHeader title="Analytics" description="Platform performance metrics and insights">
        <Tooltip>
          <TooltipTrigger
            render={
              <Button variant="outline" size="sm" disabled className="gap-1.5">
                <Download className="h-3.5 w-3.5" />
                Export
              </Button>
            }
          />
          <TooltipContent>Available when backend export API is implemented</TooltipContent>
        </Tooltip>
        <Button
          variant="outline"
          size="sm"
          onClick={refetchAll}
          disabled={isFetching}
          className="gap-1.5"
        >
          <RefreshCw className={`h-3.5 w-3.5 ${isFetching ? 'animate-spin' : ''}`} />
          Refresh
        </Button>
      </PageHeader>

      {/* KPI Cards */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {stats.isLoading ? (
          Array.from({ length: 4 }).map((_, i) => <SkeletonCard key={i} />)
        ) : stats.isError ? (
          <div className="col-span-full"><ErrorState message="Failed to load stats" onRetry={() => stats.refetch()} /></div>
        ) : stats.data ? (
          <>
            <StatCard title="Total Leads" value={stats.data.total_leads.toLocaleString()} icon={Target} />
            <StatCard title="Qualified" value={stats.data.qualified_leads.toLocaleString()} icon={TrendingUp} />
            <StatCard title="Converted" value={stats.data.converted_leads.toLocaleString()} icon={Users} />
            <StatCard title="Conversion Rate" value={`${stats.data.conversion_rate}%`} icon={Percent} />
          </>
        ) : null}
      </div>

      {/* Secondary Metrics */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {stats.isLoading ? (
          Array.from({ length: 4 }).map((_, i) => <SkeletonCard key={i} />)
        ) : stats.data ? (
          <>
            <MetricCard title="Total Chats" value={stats.data.total_chats.toLocaleString()} icon={MessageSquare} subtitle="All time" />
            <MetricCard title="Total Messages" value={stats.data.total_messages.toLocaleString()} icon={Zap} subtitle="All time" />
            <MetricCard title="Qualification Rate" value={`${stats.data.qualification_rate}%`} icon={TrendingUp} subtitle="Leads → Qualified" />
            <MetricCard title="Lost Leads" value={stats.data.lost_leads.toLocaleString()} icon={Target} subtitle="All time" />
          </>
        ) : null}
      </div>

      {/* Charts */}
      <div className="grid gap-4 lg:grid-cols-2">
        {/* Funnel */}
        {funnel.isLoading ? (
          <div className="rounded-xl border bg-card p-6 shadow-sm">
            <Skeleton className="h-4 w-32 mb-4" />
            <Skeleton className="h-[240px] w-full" />
          </div>
        ) : funnel.isError ? (
          <div className="rounded-xl border bg-card p-6 shadow-sm">
            <ErrorState message="Failed to load funnel" onRetry={() => funnel.refetch()} />
          </div>
        ) : (
          <BarChartCard title="Qualification Funnel" description="Conversion at each stage">
            <div className="flex flex-col justify-center h-full gap-4 px-2">
              {funnel.data?.map((stage) => {
                const maxVal = Math.max(...(funnel.data?.map(s => s.value) || [1]));
                const pct = maxVal > 0 ? (stage.value / maxVal) * 100 : 0;
                return (
                  <div key={stage.stage} className="flex items-center gap-3">
                    <span className="text-xs text-muted-foreground w-28 shrink-0 truncate">{stage.stage}</span>
                    <div className="flex-1 h-7 rounded bg-muted overflow-hidden">
                      <div
                        className="h-full rounded bg-primary/70 flex items-center justify-end pr-2 transition-all"
                        style={{ width: `${Math.max(pct, 5)}%` }}
                      >
                        {pct > 20 && <span className="text-[10px] text-primary-foreground font-medium">{stage.value}</span>}
                      </div>
                    </div>
                    {pct <= 20 && <span className="text-xs font-medium w-8 text-right">{stage.value}</span>}
                  </div>
                );
              })}
            </div>
          </BarChartCard>
        )}

        {/* Lead Status Distribution */}
        {leadSummary.isLoading ? (
          <div className="rounded-xl border bg-card p-6 shadow-sm">
            <Skeleton className="h-4 w-32 mb-4" />
            <Skeleton className="h-[240px] w-full" />
          </div>
        ) : leadSummary.isError ? (
          <div className="rounded-xl border bg-card p-6 shadow-sm">
            <ErrorState message="Failed to load summary" onRetry={() => leadSummary.refetch()} />
          </div>
        ) : leadSummary.data ? (
          <LineChartCard title="Lead Status Distribution" description="Current breakdown by status">
            <div className="flex flex-col justify-center h-full gap-3 px-2">
              {Object.entries(leadSummary.data)
                .filter(([key]) => key !== 'total_leads')
                .map(([key, value]) => {
                  const total = leadSummary.data!.total_leads;
                  const pct = total > 0 ? (Number(value) / total) * 100 : 0;
                  return (
                    <div key={key} className="flex items-center gap-3">
                      <span className="text-xs text-muted-foreground w-20 shrink-0 capitalize">{key}</span>
                      <div className="flex-1 h-5 rounded bg-muted overflow-hidden">
                        <div className="h-full rounded bg-primary/70 transition-all" style={{ width: `${Math.max(pct, 2)}%` }} />
                      </div>
                      <span className="text-xs font-medium w-8 text-right">{value}</span>
                    </div>
                  );
                })}
            </div>
          </LineChartCard>
        ) : null}
      </div>

      {/* Timeline */}
      {timeline.isLoading ? (
        <div className="rounded-xl border bg-card p-6 shadow-sm">
          <Skeleton className="h-4 w-48 mb-4" />
          <Skeleton className="h-[200px] w-full" />
        </div>
      ) : timeline.isError ? (
        <div className="rounded-xl border bg-card p-6 shadow-sm">
          <ErrorState message="Failed to load timeline" onRetry={() => timeline.refetch()} />
        </div>
      ) : timelineEntries.length > 0 ? (
        <div className="rounded-xl border bg-card p-6 shadow-sm">
          <div className="mb-4">
            <h3 className="text-sm font-medium">Activity Timeline</h3>
            <p className="text-xs text-muted-foreground mt-0.5">Events per day (last 14 days)</p>
          </div>
          <div className="h-[180px] flex items-end justify-between gap-1 px-1">
            {timelineEntries.map(([date, events]) => {
              const total = Object.values(events).reduce((a, b) => a + b, 0);
              const maxHeight = Math.max(...timelineEntries.map(([, e]) => Object.values(e).reduce((a, b) => a + b, 0)));
              const height = maxHeight > 0 ? (total / maxHeight) * 100 : 0;
              return (
                <div key={date} className="flex flex-col items-center gap-1 flex-1">
                  <span className="text-[9px] text-muted-foreground">{total}</span>
                  <div
                    className="w-full max-w-[32px] rounded-t bg-primary/70 hover:bg-primary transition-colors"
                    style={{ height: `${Math.max(height, 4)}%` }}
                  />
                  <span className="text-[9px] text-muted-foreground truncate w-full text-center">
                    {new Date(date).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })}
                  </span>
                </div>
              );
            })}
          </div>
        </div>
      ) : (
        <div className="rounded-xl border bg-card p-6 shadow-sm text-center">
          <p className="text-sm text-muted-foreground">No timeline data available yet</p>
        </div>
      )}

      {/* Backend limitations notice */}
      <div className="rounded-lg border border-dashed p-4 text-center">
        <p className="text-xs text-muted-foreground">
          Date range filtering, industry/project type breakdowns, and export will be available when backend analytics endpoints are extended.
        </p>
      </div>
    </PageContainer>
  );
}
