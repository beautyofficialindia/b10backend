import api from '@/lib/axios';
import { buildQueryParams } from '@/lib/utils/build-query-params';
import type { LeadListResponse, LeadFilters, LeadDetail } from '../types';

export const leadsApi = {
  list: async (filters: LeadFilters = {}, signal?: AbortSignal): Promise<LeadListResponse> => {
    const params = buildQueryParams(filters);
    const res = await api.get(`/admin/leads/?${params.toString()}`, { signal });
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
