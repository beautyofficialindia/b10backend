export interface Lead {
  id: string;
  full_name: string | null;
  company_name: string | null;
  email: string | null;
  phone: string | null;
  industry: string | null;
  project_type: string | null;
  status: LeadStatus;
  priority: LeadPriority;
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
  priority: LeadPriority;
  source: string;
  lead_score: number;
  assigned_admin: number | null;
  notification_sent: boolean;
  qualified_at: string | null;
  last_contacted_at: string | null;
  created_at: string;
  updated_at: string;
  conversation: ConversationSession | null;
  attachments: LeadAttachment[];
}

export interface LeadAttachment {
  id: string;
  file_name: string;
  file_url: string;
  file_size: number;
  mime_type: string;
  uploaded_at: string;
  is_public: boolean;
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

export type LeadPriority = 'low' | 'medium' | 'high' | 'urgent';

export interface LeadListResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: Lead[];
}

export interface LeadFilters {
  search?: string;
  status?: LeadStatus | '';
  source?: string | '';
  ordering?: string;
  page?: number;
  page_size?: number;
}
