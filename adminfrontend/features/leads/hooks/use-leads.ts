'use client';

import { useQuery, keepPreviousData } from '@tanstack/react-query';
import { leadsApi } from '../api';
import type { LeadFilters } from '../types';

export function useLeads(filters: LeadFilters) {
  return useQuery({
    queryKey: ['leads', filters],
    queryFn: () => leadsApi.list(filters),
    staleTime: 30 * 1000,
    placeholderData: keepPreviousData,
    retry: 1,
  });
}
