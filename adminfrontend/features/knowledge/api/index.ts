import api from '@/lib/axios';
import { buildQueryParams } from '@/lib/utils/build-query-params';
import type { KBListResponse, KBFilters, KnowledgeEntryDetail, KBCreatePayload, Category, Tag, KnowledgeVersion, KnowledgeVersionDetail } from '../types';

export const knowledgeApi = {
  list: async (filters: KBFilters = {}, signal?: AbortSignal): Promise<KBListResponse> => {
    const params = buildQueryParams(filters);
    const res = await api.get(`/admin/kb/entries/?${params.toString()}`, { signal });
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

  restore: async (id: string): Promise<{ data: KnowledgeEntryDetail }> => {
    const res = await api.post(`/admin/kb/entries/${id}/restore/`);
    return res.data;
  },

  getCategories: async (): Promise<{ data: Category[] }> => {
    const res = await api.get('/admin/kb/categories/');
    return res.data;
  },

  getTags: async (): Promise<{ data: Tag[] }> => {
    const res = await api.get('/admin/kb/tags/');
    return res.data;
  },

  createTag: async (data: { name: string; slug: string }): Promise<{ data: Tag }> => {
    const res = await api.post('/admin/kb/tags/', data);
    return res.data;
  },

  getVersions: async (entryId: string): Promise<{ data: KnowledgeVersion[] }> => {
    const res = await api.get(`/admin/kb/entries/${entryId}/versions/`);
    return res.data;
  },

  getVersion: async (versionId: string): Promise<{ data: KnowledgeVersionDetail }> => {
    const res = await api.get(`/admin/kb/versions/${versionId}/`);
    return res.data;
  },

  restoreVersion: async (versionId: string): Promise<{ data: KnowledgeEntryDetail }> => {
    const res = await api.post(`/admin/kb/versions/${versionId}/restore/`);
    return res.data;
  }
};
