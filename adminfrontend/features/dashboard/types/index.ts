export interface DashboardStats {
  total_chats: number;
  total_messages: number;
  total_leads: number;
  qualified_leads: number;
  converted_leads: number;
  lost_leads: number;
  qualification_rate: number;
  conversion_rate: number;
}

export interface LeadSummary {
  total_leads: number;
  gathering: number;
  qualified: number;
  converted: number;
  lost: number;
  escalated: number;
}

// Timeline: { "2024-01-15": { "chat_started": 5, "message_sent": 20 } }
export type AnalyticsTimeline = Record<string, Record<string, number>>;

export interface FunnelStage {
  stage: string;
  value: number;
}

export interface Lead {
  id: string;
  full_name: string | null;
  email: string | null;
  phone: string | null;
  company_name: string | null;
  industry: string | null;
  project_type: string | null;
  status: string;
  created_at: string;
  updated_at: string;
}
