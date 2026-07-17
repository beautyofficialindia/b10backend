"use client";

import React from "react";
import { useLeadAnalytics } from "../hooks/use-analytics";
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

export function LeadAnalyticsDashboard() {
  const { queryString } = useAnalyticsFilters();
  const { data, isLoading, error } = useLeadAnalytics(queryString);

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
        <AlertDescription>Failed to load lead analytics. Please try again later.</AlertDescription>
      </Alert>
    );
  }

  // Handle case where analytics is globally disabled
  if (!data.executive_metrics.enabled && !data.lead_funnel.enabled) {
    return (
      <div className="flex-1 space-y-4 p-8 pt-6">
        <div className="flex items-center justify-between space-y-2">
          <h2 className="text-3xl font-bold tracking-tight">Lead Analytics</h2>
        </div>
        <div className="p-12 text-center border rounded-lg bg-muted/20">
          <h3 className="text-lg font-medium">Lead Analytics Disabled</h3>
          <p className="text-sm text-muted-foreground mt-2">
            Lead analytics is currently disabled by platform settings. Please enable tracking in Settings &gt; System Management.
          </p>
        </div>
      </div>
    );
  }

  const { 
    executive_metrics, 
    lead_funnel, 
    lead_sources, 
    status_distribution, 
    score_distribution, 
    growth_trend, 
    lead_insights 
  } = data;

  return (
    <div className="flex-1 space-y-4 p-8 pt-6">
      <div className="flex items-center justify-between space-y-2">
        <h2 className="text-3xl font-bold tracking-tight">Lead Analytics</h2>
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
        {lead_funnel.enabled && lead_funnel.data && (
          <TrendCard type="bar" trend={lead_funnel.data} />
        )}
        {status_distribution.enabled && status_distribution.data && (
          <TrendCard type="bar" trend={status_distribution.data} />
        )}
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        {lead_sources.enabled && lead_sources.data && (
          <TrendCard type="bar" trend={lead_sources.data} />
        )}
        {score_distribution.enabled && score_distribution.data && (
          <TrendCard type="bar" trend={score_distribution.data} />
        )}
      </div>
      
      <AnalyticsSection 
        title="Lead Growth" 
        description="Lead generation volume over time"
        enabled={growth_trend.enabled}
      >
        {growth_trend.enabled && growth_trend.data && (
           <TrendCard type="line" trend={growth_trend.data} />
        )}
      </AnalyticsSection>

      <AnalyticsSection 
        title="Lead Insights" 
        description="Key data discoveries"
        enabled={lead_insights.enabled}
      >
        {(lead_insights.data || []).map((insight, index) => (
          <InsightCard key={index} insight={insight} />
        ))}
      </AnalyticsSection>
    </div>
  );
}
