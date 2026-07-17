"use client";

import React from "react";
import { useKnowledgeAnalytics } from "../hooks/use-analytics";
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

export function KnowledgeAnalyticsDashboard() {
  const { queryString } = useAnalyticsFilters();
  const { data, isLoading, error } = useKnowledgeAnalytics(queryString);

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
        <AlertDescription>Failed to load Knowledge Base analytics. Please try again later.</AlertDescription>
      </Alert>
    );
  }

  if (!data.executive_metrics.enabled) {
    return (
      <div className="flex-1 space-y-4 p-8 pt-6">
        <div className="flex items-center justify-between space-y-2">
          <h2 className="text-3xl font-bold tracking-tight">Knowledge Base Analytics</h2>
        </div>
        <div className="p-12 text-center border rounded-lg bg-muted/20">
          <h3 className="text-lg font-medium">Knowledge Base Analytics Disabled</h3>
          <p className="text-sm text-muted-foreground mt-2">
            Knowledge Base analytics is currently disabled by platform settings. Please enable tracking in Settings &gt; System Management.
          </p>
        </div>
      </div>
    );
  }

  const { 
    executive_metrics, 
    knowledge_growth, 
    published_growth, 
    draft_growth, 
    category_distribution, 
    tag_distribution,
    knowledge_insights 
  } = data;

  return (
    <div className="flex-1 space-y-4 p-8 pt-6">
      <div className="flex items-center justify-between space-y-2">
        <h2 className="text-3xl font-bold tracking-tight">Knowledge Base Analytics</h2>
      </div>

      <AnalyticsFilters />

      <AnalyticsSection 
        title="Executive Metrics" 
        description="High-level Knowledge Base snapshot"
        enabled={executive_metrics.enabled}
      >
        {Object.entries(executive_metrics.data || {}).map(([key, metric]) => (
          <MetricCard key={key} metric={metric} />
        ))}
      </AnalyticsSection>

      <div className="grid gap-4 md:grid-cols-3">
        {knowledge_growth.enabled && knowledge_growth.data && (
          <TrendCard type="line" trend={knowledge_growth.data} />
        )}
        {published_growth.enabled && published_growth.data && (
          <TrendCard type="line" trend={published_growth.data} />
        )}
        {draft_growth.enabled && draft_growth.data && (
          <TrendCard type="line" trend={draft_growth.data} />
        )}
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        {category_distribution.enabled && category_distribution.data && (
          <TrendCard type="bar" trend={category_distribution.data} />
        )}
        {tag_distribution.enabled && tag_distribution.data && (
          <TrendCard type="bar" trend={tag_distribution.data} />
        )}
      </div>

      <AnalyticsSection 
        title="Knowledge Base Insights" 
        description="Key data discoveries"
        enabled={knowledge_insights.enabled}
      >
        {(knowledge_insights.data || []).map((insight, index) => (
          <InsightCard key={`insight-${index}`} insight={insight} />
        ))}
      </AnalyticsSection>
    </div>
  );
}
