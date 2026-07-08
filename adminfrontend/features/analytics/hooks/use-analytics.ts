'use client';

import { useQuery } from '@tanstack/react-query';
import { analyticsApi } from '../api';

export function useAnalyticsStats() {
  return useQuery({
    queryKey: ['analytics', 'stats'],
    queryFn: analyticsApi.getStats,
    staleTime: 60 * 1000,
    retry: 1,
  });
}

export function useAnalyticsTimeline() {
  return useQuery({
    queryKey: ['analytics', 'timeline'],
    queryFn: analyticsApi.getTimeline,
    staleTime: 2 * 60 * 1000,
    retry: 1,
  });
}

export function useAnalyticsFunnel() {
  return useQuery({
    queryKey: ['analytics', 'funnel'],
    queryFn: analyticsApi.getFunnel,
    staleTime: 2 * 60 * 1000,
    retry: 1,
  });
}

export function useLeadSummary() {
  return useQuery({
    queryKey: ['analytics', 'lead-summary'],
    queryFn: analyticsApi.getLeadSummary,
    staleTime: 60 * 1000,
    retry: 1,
  });
}
