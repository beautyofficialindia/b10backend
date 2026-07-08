import api from '@/lib/axios';
import type { KBListResponse, KBFilters, KnowledgeEntryDetail, KBCreatePayload } from '../types';

export const knowledgeApi = {
  list: async (filters: KBFilters = {}): Promise<KBListResponse> => {
    const params = new URLSearchParams();
    if (filters.search) params.set('search', filters.search);
    if (filters.category) params.set('category', filters.category);
    if (filters.status) params.set('status', filters.status);
    if (filters.ordering) params.set('ordering', filters.ordering);
    if (filters.page) params.set('page', String(filters.page));
    if (filters.page_size) params.set('page_size', String(filters.page_size));
    const res = await api.get(`/admin/kb/entries/?${params.toString()}`);
    return res.data;
  },

  getById: async (id: string): Promise<{ data: KnowledgeEntryDetail }> => {
    const res = await api.get(`/admin/kb/entries/${id}/`);
    return res.data;
  },

  create: async (data: KBCreatePayload): Promise<{ data: KnowledgeEntryDetail }> => {
    const res = await api.post('/admin/kb/entries/', data);
    return res.data;
  },

  update: async (id: string, data: Partial<KBCreatePayload>): Promise<{ data: KnowledgeEntryDetail }> => {
    const res = await api.patch(`/admin/kb/entries/${id}/`, data);
    return res.data;
  },

  delete: async (id: string): Promise<void> => {
    await api.delete(`/admin/kb/entries/${id}/`);
  },

  publish: async (id: string): Promise<{ data: KnowledgeEntryDetail }> => {
    const res = await api.post(`/admin/kb/entries/${id}/publish/`);
    return res.data;
  },

  unpublish: async (id: string): Promise<{ data: KnowledgeEntryDetail }> => {
    const res = await api.post(`/admin/kb/entries/${id}/unpublish/`);
    return res.data;
  },

  archive: async (id: string): Promise<{ data: KnowledgeEntryDetail }> => {
    const res = await api.post(`/admin/kb/entries/${id}/archive/`);
    return res.data;
  },
};
