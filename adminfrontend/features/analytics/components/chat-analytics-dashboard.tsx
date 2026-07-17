"use client";

import React from "react";
import { useChatAnalytics } from "../hooks/use-analytics";
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

export function ChatAnalyticsDashboard() {
  const { queryString } = useAnalyticsFilters();
  const { data, isLoading, error } = useChatAnalytics(queryString);

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
        <AlertDescription>Failed to load Chat analytics. Please try again later.</AlertDescription>
      </Alert>
    );
  }

  if (!data.executive_metrics.enabled) {
    return (
      <div className="flex-1 space-y-4 p-8 pt-6">
        <div className="flex items-center justify-between space-y-2">
          <h2 className="text-3xl font-bold tracking-tight">Chat Analytics</h2>
        </div>
        <div className="p-12 text-center border rounded-lg bg-muted/20">
          <h3 className="text-lg font-medium">Chat Analytics Disabled</h3>
          <p className="text-sm text-muted-foreground mt-2">
            Chat analytics is currently disabled by platform settings. Please enable tracking in Settings &gt; System Management.
          </p>
        </div>
      </div>
    );
  }

  const { 
    executive_metrics, 
    conversation_growth, 
    message_growth, 
    lead_generation_growth, 
    qualification_growth, 
    chat_insights 
  } = data;

  return (
    <div className="flex-1 space-y-4 p-8 pt-6">
      <div className="flex items-center justify-between space-y-2">
        <h2 className="text-3xl font-bold tracking-tight">Chat Analytics</h2>
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
        {conversation_growth.enabled && conversation_growth.data && (
          <TrendCard type="line" trend={conversation_growth.data} />
        )}
        {message_growth.enabled && message_growth.data && (
          <TrendCard type="line" trend={message_growth.data} />
        )}
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        {lead_generation_growth.enabled && lead_generation_growth.data && (
          <TrendCard type="line" trend={lead_generation_growth.data} />
        )}
        {qualification_growth.enabled && qualification_growth.data && (
          <TrendCard type="line" trend={qualification_growth.data} />
        )}
      </div>

      <AnalyticsSection 
        title="Chat Insights" 
        description="Key data discoveries"
        enabled={chat_insights.enabled}
      >
        {(chat_insights.data || []).map((insight, index) => (
          <InsightCard key={`insight-${index}`} insight={insight} />
        ))}
      </AnalyticsSection>
    </div>
  );
}
