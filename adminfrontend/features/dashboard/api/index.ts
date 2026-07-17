import api from '@/lib/axios';
import type { Lead, PendingFollowup, KnowledgeStatus, SystemHealth } from '../types';

export const dashboardApi = {
  getRecentLeads: async (): Promise<{ results: Lead[] }> => {
    const res = await api.get('/admin/leads/?page_size=5&ordering=-created_at');
    return res.data;
  },

  getPendingFollowups: async (): Promise<{ results: PendingFollowup[] }> => {
    const res = await api.get('/admin/crm/followups/pending/');
    return res.data;
  },

  getKnowledgeStatus: async (): Promise<{ data: KnowledgeStatus }> => {
    const res = await api.get('/admin/kb/status/');
    return res.data;
  },

  getSystemHealth: async (): Promise<SystemHealth> => {
    const res = await api.get('/admin/settings/health/');
    return res.data;
  },
};
