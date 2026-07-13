export interface Category {
  id: number;
  name: string;
  slug: string;
  description: string;
  color: string;
  icon: string;
  sort_order: number;
  is_active: boolean;
}

export interface Tag {
  id: number;
  name: string;
  slug: string;
  is_active: boolean;
}

export interface KnowledgeEntry {
  id: string;
  category: {
    id: number;
    name: string;
    slug: string;
    color: string;
  } | null;
  tags: {
    id: number;
    name: string;
    slug: string;
  }[];
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
// Deprecated: Used only for backward compatibility if needed, prefer `Category` interface
export type KBCategory = 'company' | 'service' | 'industry' | 'faq' | 'contact' | 'technology' | 'general';

export interface KBListResponse {
  success: boolean;
  data: KnowledgeEntry[];
  meta: { pagination: { page: number; page_size: number; total_count: number; total_pages: number } };
}

export interface KBFilters {
  search?: string;
  category?: string; // category slug
  status?: KBStatus | '';
  ordering?: string;
  page?: number;
  page_size?: number;
}

export interface KBCreatePayload {
  category: number; // category ID
  tags?: number[]; // array of tag IDs
  title: string;
  content: string;
  sort_order?: number;
  status?: KBStatus;
}
