"use client";

import React from "react";
import { useUserAnalytics } from "../hooks/use-analytics";
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

export function UserAnalyticsDashboard() {
  const { queryString } = useAnalyticsFilters();
  const { data, isLoading, error } = useUserAnalytics(queryString);

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
        <AlertDescription>Failed to load User analytics. Please try again later.</AlertDescription>
      </Alert>
    );
  }

  if (!data.executive_metrics.enabled) {
    return (
      <div className="flex-1 space-y-4 p-8 pt-6">
        <div className="flex items-center justify-between space-y-2">
          <h2 className="text-3xl font-bold tracking-tight">User Analytics</h2>
        </div>
        <div className="p-12 text-center border rounded-lg bg-muted/20">
          <h3 className="text-lg font-medium">Analytics Disabled</h3>
          <p className="text-sm text-muted-foreground mt-2">
            Analytics is currently disabled by platform settings. Please enable tracking in Settings &gt; System Management.
          </p>
        </div>
      </div>
    );
  }

  const { 
    executive_metrics, 
    user_growth, 
    role_distribution, 
    permission_distribution, 
    user_insights 
  } = data;

  return (
    <div className="flex-1 space-y-4 p-8 pt-6">
      <div className="flex items-center justify-between space-y-2">
        <h2 className="text-3xl font-bold tracking-tight">User Analytics</h2>
      </div>

      <AnalyticsFilters />

      <AnalyticsSection 
        title="Executive Metrics" 
        description="High-level user base snapshot"
        enabled={executive_metrics.enabled}
      >
        {Object.entries(executive_metrics.data || {}).map(([key, metric]) => (
          <MetricCard key={key} metric={metric} />
        ))}
      </AnalyticsSection>

      <div className="grid gap-4 md:grid-cols-1">
        {user_growth.enabled && user_growth.data && (
          <TrendCard type="line" trend={user_growth.data} />
        )}
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        {role_distribution.enabled && role_distribution.data && (
          <TrendCard type="bar" trend={role_distribution.data} />
        )}
        {permission_distribution.enabled && permission_distribution.data && (
          <TrendCard type="bar" trend={permission_distribution.data} />
        )}
      </div>

      <AnalyticsSection 
        title="User Insights" 
        description="Key data discoveries"
        enabled={user_insights.enabled}
      >
        {(user_insights.data || []).map((insight, index) => (
          <InsightCard key={`insight-${index}`} insight={insight} />
        ))}
      </AnalyticsSection>
    </div>
  );
}
