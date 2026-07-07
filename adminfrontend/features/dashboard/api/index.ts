import api from '@/lib/axios';
import type { DashboardStats, AnalyticsTimeline, FunnelStage, LeadSummary, Lead } from '../types';

export const dashboardApi = {
  getStats: async (): Promise<DashboardStats> => {
    const res = await api.get('/admin/analytics/');
    return res.data;
  },

  getLeadSummary: async (): Promise<LeadSummary> => {
    const res = await api.get('/admin/dashboard/');
    return res.data;
  },

  getTimeline: async (): Promise<AnalyticsTimeline> => {
    const res = await api.get('/admin/analytics/timeline/');
    return res.data;
  },

  getFunnel: async (): Promise<FunnelStage[]> => {
    const res = await api.get('/admin/analytics/funnel/');
    return res.data;
  },

  getRecentLeads: async (): Promise<{ results: Lead[] }> => {
    const res = await api.get('/admin/leads/?page_size=5&ordering=-created_at');
    return res.data;
  },
};
