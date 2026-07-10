'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { leadsApi } from '@/features/leads/api';
import type { Lead, LeadStatus } from '@/features/leads/types';
import type { PipelineColumn } from '../types';
import { PIPELINE_COLUMNS } from '../types';

export function usePipelineLeads(search?: string) {
  return useQuery({
    queryKey: ['crm', 'pipeline', search],
    queryFn: async ({ signal }) => {
      // Fetch all leads (no status filter, larger page for pipeline view)
      const res = await leadsApi.list({ page_size: 100, search: search || undefined }, signal);
      return res.results;
    },
    staleTime: 30 * 1000,
    retry: 1,
  });
}

export function useMoveLeadStatus() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, status }: { id: string; status: LeadStatus }) =>
      leadsApi.updateStatus(id, status),

    // Optimistic update
    onMutate: async ({ id, status }) => {
      await queryClient.cancelQueries({ queryKey: ['crm', 'pipeline'] });

      const previousLeads = queryClient.getQueryData<Lead[]>(['crm', 'pipeline', undefined]);

      queryClient.setQueriesData<Lead[]>(
        { queryKey: ['crm', 'pipeline'] },
        (old) => old?.map((lead) => (lead.id === id ? { ...lead, status } : lead))
      );

      return { previousLeads };
    },

    onError: (_err, _vars, context) => {
      // Rollback
      if (context?.previousLeads) {
        queryClient.setQueriesData<Lead[]>(
          { queryKey: ['crm', 'pipeline'] },
          () => context.previousLeads
        );
      }
    },

    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ['crm', 'pipeline'] });
      queryClient.invalidateQueries({ queryKey: ['leads'] });
    },
  });
}

export function getColumnLeads(leads: Lead[], column: PipelineColumn): Lead[] {
  return leads.filter((lead) => lead.status === column.id);
}

export { PIPELINE_COLUMNS };
