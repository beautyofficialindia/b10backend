'use client';

import { useQuery } from '@tanstack/react-query';
import { dashboardApi } from '../api';

export function useDashboardStats(enabled: boolean = true) {
  return useQuery({
    queryKey: ['dashboard', 'stats'],
    queryFn: dashboardApi.getStats,
    staleTime: 60 * 1000,
    retry: 1,
    enabled,
  });
}

export function useLeadSummary(enabled: boolean = true) {
  return useQuery({
    queryKey: ['dashboard', 'lead-summary'],
    queryFn: dashboardApi.getLeadSummary,
    staleTime: 60 * 1000,
    retry: 1,
    enabled,
  });
}

export function useAnalyticsTimeline(enabled: boolean = true) {
  return useQuery({
    queryKey: ['dashboard', 'timeline'],
    queryFn: dashboardApi.getTimeline,
    staleTime: 2 * 60 * 1000,
    retry: 1,
    enabled,
  });
}

export function useFunnel(enabled: boolean = true) {
  return useQuery({
    queryKey: ['dashboard', 'funnel'],
    queryFn: dashboardApi.getFunnel,
    staleTime: 2 * 60 * 1000,
    retry: 1,
    enabled,
  });
}

export function useRecentLeads(enabled: boolean = true) {
  return useQuery({
    queryKey: ['dashboard', 'recent-leads'],
    queryFn: dashboardApi.getRecentLeads,
    staleTime: 30 * 1000,
    retry: 1,
    enabled,
  });
}
