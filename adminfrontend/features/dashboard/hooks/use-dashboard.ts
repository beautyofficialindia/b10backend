'use client';

import { useQuery } from '@tanstack/react-query';
import { dashboardApi } from '../api';

export function useDashboardStats() {
  return useQuery({
    queryKey: ['dashboard', 'stats'],
    queryFn: dashboardApi.getStats,
    staleTime: 60 * 1000,
    retry: 1,
  });
}

export function useLeadSummary() {
  return useQuery({
    queryKey: ['dashboard', 'lead-summary'],
    queryFn: dashboardApi.getLeadSummary,
    staleTime: 60 * 1000,
    retry: 1,
  });
}

export function useAnalyticsTimeline() {
  return useQuery({
    queryKey: ['dashboard', 'timeline'],
    queryFn: dashboardApi.getTimeline,
    staleTime: 2 * 60 * 1000,
    retry: 1,
  });
}

export function useFunnel() {
  return useQuery({
    queryKey: ['dashboard', 'funnel'],
    queryFn: dashboardApi.getFunnel,
    staleTime: 2 * 60 * 1000,
    retry: 1,
  });
}

export function useRecentLeads() {
  return useQuery({
    queryKey: ['dashboard', 'recent-leads'],
    queryFn: dashboardApi.getRecentLeads,
    staleTime: 30 * 1000,
    retry: 1,
  });
}
