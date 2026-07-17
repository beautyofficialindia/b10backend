"use client";

import React from "react";
import { useCrmAnalytics } from "../hooks/use-analytics";
import { useAnalyticsFilters } from "../hooks/use-analytics-filters";
import { 
  MetricCard, 
  InsightCard, 
  AnalyticsSection, 
  TrendCard,
  AnalyticsFilters
} from "./ui";
import { Loader2 } from "lucide-react";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";

export function CrmAnalyticsDashboard() {
  const { queryString } = useAnalyticsFilters();
  const { data, isLoading, error } = useCrmAnalytics(queryString);

  if (isLoading) {
    return (
      <div className="flex h-[400px] items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (error || !data) {
    return (
      <Alert variant="destructive">
        <AlertTitle>Error</AlertTitle>
        <AlertDescription>Failed to load CRM analytics. Please try again later.</AlertDescription>
      </Alert>
    );
  }

  if (!data.executive_metrics.enabled) {
    return (
      <div className="flex-1 space-y-4 p-8 pt-6">
        <div className="flex items-center justify-between space-y-2">
          <h2 className="text-3xl font-bold tracking-tight">CRM Analytics</h2>
        </div>
        <div className="p-12 text-center border rounded-lg bg-muted/20">
          <h3 className="text-lg font-medium">CRM Analytics Disabled</h3>
          <p className="text-sm text-muted-foreground mt-2">
            CRM analytics is currently disabled by platform settings. Please enable tracking in Settings &gt; System Management.
          </p>
        </div>
      </div>
    );
  }

  const { 
    executive_metrics, 
    crm_funnel, 
    followup_analytics, 
    status_distribution, 
    activity_trends, 
    user_performance, 
    crm_insights 
  } = data;

  return (
    <div className="flex-1 space-y-4 p-8 pt-6">
      <div className="flex items-center justify-between space-y-2">
        <h2 className="text-3xl font-bold tracking-tight">CRM Analytics</h2>
      </div>

      <AnalyticsFilters />

      <AnalyticsSection 
        title="Executive Metrics" 
        description="High-level performance snapshot"
        enabled={executive_metrics.enabled}
      >
        {Object.entries(executive_metrics.data || {}).map(([key, metric]) => (
          <MetricCard key={key} metric={metric} />
        ))}
      </AnalyticsSection>

      <div className="grid gap-4 md:grid-cols-2">
        {crm_funnel.enabled && crm_funnel.data && (
          <TrendCard type="bar" trend={crm_funnel.data} />
        )}
        {status_distribution.enabled && status_distribution.data && (
          <TrendCard type="bar" trend={status_distribution.data} />
        )}
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        {followup_analytics.enabled && followup_analytics.data && (
          <TrendCard type="bar" trend={followup_analytics.data} />
        )}
        {activity_trends.enabled && activity_trends.data && (
          <TrendCard type="line" trend={activity_trends.data} />
        )}
      </div>

      <AnalyticsSection 
        title="User Performance" 
        description="Sales team activity metrics"
        enabled={user_performance.enabled}
      >
        {(user_performance.data || []).map((insight, index) => (
          <InsightCard key={`user-${index}`} insight={insight} />
        ))}
      </AnalyticsSection>

      <AnalyticsSection 
        title="CRM Insights" 
        description="Key data discoveries"
        enabled={crm_insights.enabled}
      >
        {(crm_insights.data || []).map((insight, index) => (
          <InsightCard key={`insight-${index}`} insight={insight} />
        ))}
      </AnalyticsSection>
    </div>
  );
}
