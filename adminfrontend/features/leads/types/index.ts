export interface Lead {
  id: string;
  full_name: string | null;
  company_name: string | null;
  email: string | null;
  phone: string | null;
  industry: string | null;
  project_type: string | null;
  status: LeadStatus;
  created_at: string;
}

export interface LeadDetail {
  id: string;
  full_name: string | null;
  company_name: string | null;
  email: string | null;
  phone: string | null;
  industry: string | null;
  project_type: string | null;
  budget_range: string | null;
  timeline: string | null;
  requirements: string | null;
  status: LeadStatus;
  source: string;
  lead_score: number;
  assigned_admin_id: string | null;
  notification_sent: boolean;
  qualified_at: string | null;
  last_contacted_at: string | null;
  created_at: string;
  updated_at: string;
  conversation: ConversationSession | null;
}

export interface ConversationSession {
  session_id: string;
  is_active: boolean;
  created_at: string;
  last_message_at: string | null;
  messages: Message[];
}

export interface Message {
  role: 'user' | 'assistant' | 'system';
  content: string;
  created_at: string;
}

export type LeadStatus = 'gathering' | 'qualified' | 'disqualified' | 'escalated' | 'converted' | 'lost';

export interface LeadListResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: Lead[];
}

export interface LeadFilters {
  search?: string;
  status?: LeadStatus | '';
  ordering?: string;
  page?: number;
  page_size?: number;
}
