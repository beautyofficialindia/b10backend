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
