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

export interface PendingFollowup {
  id: number;
  lead: string;
  followup_type: string;
  scheduled_at: string;
  notes: string | null;
  status: string;
  created_at: string;
}

export interface KnowledgeStatus {
  draft: number;
  published: number;
  archived: number;
}

export interface SystemAlert {
  message: string;
}

export interface SystemHealth {
  critical: SystemAlert[];
  warning: SystemAlert[];
  info: SystemAlert[];
  is_healthy: boolean;
}

