import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '@/lib/axios';
import type { LeadActivity, LeadStatusHistory } from '../types';

export const crmKeys = {
  all: ['crm'] as const,
  activities: (leadId: string) => [...crmKeys.all, 'activities', leadId] as const,
  statusHistory: (leadId: string) => [...crmKeys.all, 'statusHistory', leadId] as const,
  followUps: (leadId: string) => [...crmKeys.all, 'followUps', leadId] as const,
  notes: (leadId: string) => [...crmKeys.all, 'notes', leadId] as const,
};

export const useLeadActivities = (leadId: string) => {
  return useQuery({
    queryKey: crmKeys.activities(leadId),
    queryFn: async () => {
      const response = await api.get<{ results: LeadActivity[] }>(`/admin/crm/leads/${leadId}/activities/`);
      if (Array.isArray(response.data)) return response.data as LeadActivity[];
      return response.data.results;
    },
    staleTime: 60 * 1000,
  });
};

export const useLeadStatusHistory = (leadId: string) => {
  return useQuery({
    queryKey: crmKeys.statusHistory(leadId),
    queryFn: async () => {
      const response = await api.get<{ results: LeadStatusHistory[] }>(`/admin/crm/leads/${leadId}/status-history/`);
      if (Array.isArray(response.data)) return response.data as LeadStatusHistory[];
      return response.data.results;
    },
    staleTime: 60 * 1000,
  });
};

export * from './followups';
export * from './notes';


export const useAssignLead = (leadId: string) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (assigned_admin: number | null) => {
      const response = await api.patch(`/admin/leads/${leadId}/assign/`, { assigned_admin });
      return response.data;
    },
    onMutate: async (newAssignee) => {
      await queryClient.cancelQueries({ queryKey: ['leads', leadId] });
      const previousLead = queryClient.getQueryData(['leads', leadId]);
      if (previousLead) {
        queryClient.setQueryData(['leads', leadId], {
          ...(previousLead as object),
          assigned_admin: newAssignee,
        });
      }
      return { previousLead };
    },
    onError: (err, newAssigneeId, context) => {
      if (context?.previousLead) {
        queryClient.setQueryData(['leads', leadId], context.previousLead);
      }
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ['leads', leadId] });
      queryClient.invalidateQueries({ queryKey: crmKeys.activities(leadId) });
      queryClient.invalidateQueries({ queryKey: ['leads'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
    },
  });
};
