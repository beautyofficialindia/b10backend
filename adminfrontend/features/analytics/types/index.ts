export interface Metric {
  title: string;
  value: number | string | null;
  previous_value?: number | null;
  difference?: number | null;
  growth_percentage?: number | null;
  enabled: boolean;
}

export interface Trend {
  title: string;
  labels: string[];
  values: number[];
}

export interface Health {
  module: string;
  status: "healthy" | "warning" | "error" | "disabled";
  enabled: boolean;
  tracking_enabled: boolean;
  message: string;
}

export interface Insight {
  title: string;
  value: string;
  enabled: boolean;
}

export interface SectionWrapper<T> {
  enabled: boolean;
  data: T;
}

export interface ModuleHealthMap {
  chatbot?: Health;
  crm?: Health;
  knowledge_base?: Health;
  analytics_tracking?: Health;
  settings?: Health;
  users_roles?: Health;
}

export interface OverviewResponse {
  executive_metrics: SectionWrapper<Record<string, Metric>>;
  growth_metrics: SectionWrapper<Record<string, Metric>>;
  module_health: SectionWrapper<ModuleHealthMap>;
  recent_trends: SectionWrapper<Record<string, Trend>>;
  platform_insights: SectionWrapper<Insight[]>;
}

export interface LeadAnalyticsResponse {
  executive_metrics: SectionWrapper<Record<string, Metric>>;
  lead_funnel: SectionWrapper<Trend>;
  lead_sources: SectionWrapper<Trend>;
  status_distribution: SectionWrapper<Trend>;
  score_distribution: SectionWrapper<Trend>;
  growth_trend: SectionWrapper<Trend>;
  lead_insights: SectionWrapper<Insight[]>;
}

export interface CrmAnalyticsResponse {
  executive_metrics: SectionWrapper<Record<string, Metric>>;
  crm_funnel: SectionWrapper<Trend>;
  followup_analytics: SectionWrapper<Trend>;
  status_distribution: SectionWrapper<Trend>;
  activity_trends: SectionWrapper<Trend>;
  user_performance: SectionWrapper<Insight[]>;
  crm_insights: SectionWrapper<Insight[]>;
}

export interface ChatAnalyticsResponse {
  executive_metrics: SectionWrapper<Record<string, Metric>>;
  conversation_growth: SectionWrapper<Trend>;
  message_growth: SectionWrapper<Trend>;
  lead_generation_growth: SectionWrapper<Trend>;
  qualification_growth: SectionWrapper<Trend>;
  chat_insights: SectionWrapper<Insight[]>;
}

export interface KnowledgeAnalyticsResponse {
  executive_metrics: SectionWrapper<Record<string, Metric>>;
  knowledge_growth: SectionWrapper<Trend>;
  published_growth: SectionWrapper<Trend>;
  draft_growth: SectionWrapper<Trend>;
  category_distribution: SectionWrapper<Trend>;
  tag_distribution: SectionWrapper<Trend>;
  knowledge_insights: SectionWrapper<Insight[]>;
}

export interface UserAnalyticsResponse {
  executive_metrics: SectionWrapper<Record<string, Metric>>;
  user_growth: SectionWrapper<Trend>;
  role_distribution: SectionWrapper<Trend>;
  permission_distribution: SectionWrapper<Trend>;
  user_insights: SectionWrapper<Insight[]>;
}
