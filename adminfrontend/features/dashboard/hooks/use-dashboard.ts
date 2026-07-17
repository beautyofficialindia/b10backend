'use client';

import { useQuery } from '@tanstack/react-query';
import { dashboardApi } from '../api';

export function useRecentLeads(enabled: boolean = true) {
  return useQuery({
    queryKey: ['dashboard', 'recent-leads'],
    queryFn: dashboardApi.getRecentLeads,
    staleTime: 30 * 1000,
    retry: 1,
    enabled,
  });
}

export function usePendingFollowups(enabled: boolean = true) {
  return useQuery({
    queryKey: ['dashboard', 'pending-followups'],
    queryFn: dashboardApi.getPendingFollowups,
    staleTime: 30 * 1000,
    retry: 1,
    enabled,
  });
}

export function useKnowledgeStatus(enabled: boolean = true) {
  return useQuery({
    queryKey: ['dashboard', 'knowledge-status'],
    queryFn: dashboardApi.getKnowledgeStatus,
    staleTime: 60 * 1000,
    retry: 1,
    enabled,
  });
}

export function useSystemHealth(enabled: boolean = true) {
  return useQuery({
    queryKey: ['dashboard', 'system-health'],
    queryFn: dashboardApi.getSystemHealth,
    staleTime: 60 * 1000,
    retry: 1,
    enabled,
  });
}
