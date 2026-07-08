'use client';

import { useQuery } from '@tanstack/react-query';
import { analyticsApi } from '../api';

// Share query keys with dashboard to avoid duplicate requests for the same endpoints.
// Both dashboard and analytics fetch from the same backend endpoints.

export function useAnalyticsStats() {
  return useQuery({
    queryKey: ['dashboard', 'stats'],
    queryFn: analyticsApi.getStats,
    staleTime: 60 * 1000,
    retry: 1,
  });
}

export function useAnalyticsTimeline() {
  return useQuery({
    queryKey: ['dashboard', 'timeline'],
    queryFn: analyticsApi.getTimeline,
    staleTime: 2 * 60 * 1000,
    retry: 1,
  });
}

export function useAnalyticsFunnel() {
  return useQuery({
    queryKey: ['dashboard', 'funnel'],
    queryFn: analyticsApi.getFunnel,
    staleTime: 2 * 60 * 1000,
    retry: 1,
  });
}

export function useLeadSummary() {
  return useQuery({
    queryKey: ['dashboard', 'lead-summary'],
    queryFn: analyticsApi.getLeadSummary,
    staleTime: 60 * 1000,
    retry: 1,
  });
}
