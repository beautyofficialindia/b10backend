import api from '@/lib/axios';
import type { LeadListResponse, LeadFilters, LeadDetail } from '../types';

export const leadsApi = {
  list: async (filters: LeadFilters = {}): Promise<LeadListResponse> => {
    const params = new URLSearchParams();

    if (filters.search) params.set('search', filters.search);
    if (filters.status) params.set('status', filters.status);
    if (filters.ordering) params.set('ordering', filters.ordering);
    if (filters.page) params.set('page', String(filters.page));
    if (filters.page_size) params.set('page_size', String(filters.page_size));

    const res = await api.get(`/admin/leads/?${params.toString()}`);
    return res.data;
  },

  getById: async (id: string): Promise<LeadDetail> => {
    const res = await api.get(`/admin/leads/${id}/`);
    return res.data;
  },

  updateStatus: async (id: string, status: string): Promise<LeadDetail> => {
    const res = await api.patch(`/admin/leads/${id}/`, { status });
    return res.data;
  },
};
