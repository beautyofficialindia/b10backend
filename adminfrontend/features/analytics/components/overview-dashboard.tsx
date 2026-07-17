"use client";

import React from "react";
import { useOverviewAnalytics } from "../hooks/use-analytics";
import { useAnalyticsFilters } from "../hooks/use-analytics-filters";
import { 
  MetricCard, 
  HealthCard, 
  InsightCard, 
  AnalyticsSection, 
  TrendCard,
  AnalyticsFilters
} from "./ui";
import { Loader2 } from "lucide-react";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";

export function OverviewDashboard() {
  const { queryString } = useAnalyticsFilters();
  const { data, isLoading, error } = useOverviewAnalytics(queryString);

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
        <AlertDescription>Failed to load analytics overview. Please try again later.</AlertDescription>
      </Alert>
    );
  }

  const { executive_metrics, growth_metrics, module_health, recent_trends, platform_insights } = data;

  return (
    <div className="flex-1 space-y-4 p-8 pt-6">
      <div className="flex items-center justify-between space-y-2">
        <h2 className="text-3xl font-bold tracking-tight">Analytics Overview</h2>
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

      <AnalyticsSection 
        title="Growth Metrics" 
        description="Growth compared to the previous period"
        enabled={growth_metrics.enabled}
      >
        {Object.entries(growth_metrics.data || {}).map(([key, metric]) => (
          <MetricCard key={key} metric={metric} />
        ))}
      </AnalyticsSection>

      <AnalyticsSection 
        title="Recent Trends" 
        description="Visual trends over time"
        enabled={recent_trends.enabled}
      >
        {Object.entries(recent_trends.data || {}).map(([key, trend]) => (
          <TrendCard key={key} trend={trend} />
        ))}
      </AnalyticsSection>

      <AnalyticsSection 
        title="Platform Insights" 
        description="Key data discoveries"
        enabled={platform_insights.enabled}
      >
        {(platform_insights.data || []).map((insight, index) => (
          <InsightCard key={index} insight={insight} />
        ))}
      </AnalyticsSection>

      <AnalyticsSection 
        title="Module Health" 
        description="Status of platform systems"
        enabled={module_health.enabled}
      >
        {Object.entries(module_health.data || {}).map(([key, health]) => (
          <HealthCard key={key} health={health} />
        ))}
      </AnalyticsSection>
    </div>
  );
}
