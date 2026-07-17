"use client";

import { useAuth } from '@/features/auth';
import { PageContainer } from '@/components/layout';
import { useOverviewAnalytics } from '@/features/analytics/hooks/use-analytics';
import { Metric, Health } from '@/features/analytics/types';
import { MetricCard, HealthCard } from '@/features/analytics/components/ui';
import { useFeatureFlags } from '@/features/platform-settings/providers';
import { 
  RecentLeadsWidget, 
  PendingFollowups, 
  KnowledgeStatusWidget, 
  SystemAlerts, 
  QuickActions
} from '@/features/dashboard/components';

export default function DashboardPage() {
  const { user } = useAuth();
  const { flags } = useFeatureFlags();

  const greeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 18) return 'Good afternoon';
    return 'Good evening';
  };

  const { data: analyticsData } = useOverviewAnalytics();

  return (
    <PageContainer>
      {/* Welcome Header */}
      <div className="flex flex-col gap-1 sm:flex-row sm:items-center sm:justify-between mb-8">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">
            {greeting()}, {user?.first_name || user?.username}
          </h1>
          <p className="text-sm text-muted-foreground">
            {new Date().toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}
          </p>
        </div>
      </div>

      <div className="space-y-6">
        {/* Executive Metrics */}
        {flags["ENABLE_ANALYTICS"] && analyticsData?.executive_metrics?.enabled && (
          <section className="space-y-4">
            <h2 className="text-lg font-semibold tracking-tight">Executive Metrics</h2>
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
              {Object.values(analyticsData.executive_metrics.data).map((metric: Metric, i: number) => (
                <MetricCard key={i} metric={metric} />
              ))}
            </div>
          </section>
        )}

        {/* Module Health */}
        {flags["ENABLE_ANALYTICS"] && analyticsData?.module_health?.enabled && (
          <section className="space-y-4">
            <h2 className="text-lg font-semibold tracking-tight">Module Health</h2>
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {Object.values(analyticsData.module_health.data).map((health: Health, i: number) => (
                <HealthCard key={i} health={health} />
              ))}
            </div>
          </section>
        )}

        <div className="grid gap-6 md:grid-cols-2">
          <div className="space-y-6">
            {/* Recent Leads */}
            {flags["ENABLE_CRM"] && (
              <section>
                <RecentLeadsWidget />
              </section>
            )}

            {/* Knowledge Base Status */}
            {flags["ENABLE_KNOWLEDGE_BASE"] && (
              <section>
                <KnowledgeStatusWidget />
              </section>
            )}
            
            {/* System Alerts */}
            <section>
              <SystemAlerts />
            </section>
          </div>

          <div className="space-y-6">
            {/* Pending Followups */}
            {flags["ENABLE_CRM"] && (
              <section>
                <PendingFollowups />
              </section>
            )}

            {/* Quick Actions */}
            <section>
              <QuickActions />
            </section>
          </div>
        </div>
      </div>
    </PageContainer>
  );
}
