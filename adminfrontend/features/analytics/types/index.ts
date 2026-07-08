export interface AnalyticsStats {
  total_chats: number;
  total_messages: number;
  total_leads: number;
  qualified_leads: number;
  converted_leads: number;
  lost_leads: number;
  qualification_rate: number;
  conversion_rate: number;
}

export type AnalyticsTimeline = Record<string, Record<string, number>>;

export interface FunnelStage {
  stage: string;
  value: number;
}

export interface LeadSummary {
  total_leads: number;
  gathering: number;
  qualified: number;
  converted: number;
  lost: number;
  escalated: number;
}
