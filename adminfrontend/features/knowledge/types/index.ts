export interface KnowledgeEntry {
  id: string;
  category: KBCategory;
  title: string;
  slug: string;
  status: KBStatus;
  source: string;
  sort_order: number;
  published_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface KnowledgeEntryDetail extends KnowledgeEntry {
  content: string;
  structured_data: Record<string, unknown>;
  created_by: string | null;
  updated_by: string | null;
}

export type KBStatus = 'draft' | 'published' | 'archived';
export type KBCategory = 'company' | 'service' | 'industry' | 'faq' | 'contact' | 'technology' | 'general';

export interface KBListResponse {
  success: boolean;
  data: KnowledgeEntry[];
  meta: { pagination: { page: number; page_size: number; total_count: number; total_pages: number } };
}

export interface KBFilters {
  search?: string;
  category?: KBCategory | '';
  status?: KBStatus | '';
  ordering?: string;
  page?: number;
  page_size?: number;
}

export interface KBCreatePayload {
  category: KBCategory;
  title: string;
  content: string;
  sort_order?: number;
}
