import api from '@/lib/axios';
import type { AnalyticsStats, AnalyticsTimeline, FunnelStage, LeadSummary } from '../types';

export const analyticsApi = {
  getStats: async (): Promise<AnalyticsStats> => {
    const res = await api.get('/admin/analytics/');
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

  getLeadSummary: async (): Promise<LeadSummary> => {
    const res = await api.get('/admin/dashboard/');
    return res.data;
  },
};
