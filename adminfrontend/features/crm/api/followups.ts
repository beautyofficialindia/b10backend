import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '@/lib/axios';
import { crmKeys } from './index';
import type { LeadFollowUp } from '../types';

export const useLeadFollowUps = (leadId: string) => {
  return useQuery({
    queryKey: crmKeys.followUps(leadId),
    queryFn: async () => {
      const response = await api.get<{ results: LeadFollowUp[] }>(`/admin/crm/leads/${leadId}/followups/`);
      if (Array.isArray(response.data)) return response.data as LeadFollowUp[];
      return response.data.results;
    },
    staleTime: 60 * 1000,
  });
};

export const useCreateFollowUp = (leadId: string) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: Partial<LeadFollowUp>) => {
      const response = await api.post(`/admin/crm/leads/${leadId}/followups/`, data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: crmKeys.followUps(leadId) });
      queryClient.invalidateQueries({ queryKey: crmKeys.activities(leadId) });
      queryClient.invalidateQueries({ queryKey: ['leads', leadId] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
      queryClient.invalidateQueries({ queryKey: ['crm', 'pipeline'] });
    },
  });
};

export const useUpdateFollowUp = (leadId: string) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ id, data }: { id: string; data: Partial<LeadFollowUp> }) => {
      const response = await api.patch(`/admin/crm/followups/${id}/`, data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: crmKeys.followUps(leadId) });
      queryClient.invalidateQueries({ queryKey: crmKeys.activities(leadId) });
      queryClient.invalidateQueries({ queryKey: ['leads', leadId] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
      queryClient.invalidateQueries({ queryKey: ['crm', 'pipeline'] });
    },
  });
};

export const useCompleteFollowUp = (leadId: string) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: string) => {
      const response = await api.patch(`/admin/crm/followups/${id}/`, { status: 'completed' });
      return response.data;
    },
    onMutate: async (id: string) => {
      await queryClient.cancelQueries({ queryKey: crmKeys.followUps(leadId) });
      const previousFollowUps = queryClient.getQueryData<LeadFollowUp[]>(crmKeys.followUps(leadId));
      if (previousFollowUps) {
        queryClient.setQueryData<LeadFollowUp[]>(crmKeys.followUps(leadId), (old) => {
          if (!old) return old;
          return old.map(f => f.id === id ? { ...f, status: 'completed' } : f);
        });
      }
      return { previousFollowUps };
    },
    onError: (err, id, context) => {
      if (context?.previousFollowUps) {
        queryClient.setQueryData(crmKeys.followUps(leadId), context.previousFollowUps);
      }
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: crmKeys.followUps(leadId) });
      queryClient.invalidateQueries({ queryKey: crmKeys.activities(leadId) });
      queryClient.invalidateQueries({ queryKey: ['leads', leadId] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
      queryClient.invalidateQueries({ queryKey: ['crm', 'pipeline'] });
    },
  });
};

export const useCancelFollowUp = (leadId: string) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: string) => {
      const response = await api.patch(`/admin/crm/followups/${id}/`, { status: 'cancelled' });
      return response.data;
    },
    onMutate: async (id: string) => {
      await queryClient.cancelQueries({ queryKey: crmKeys.followUps(leadId) });
      const previousFollowUps = queryClient.getQueryData<LeadFollowUp[]>(crmKeys.followUps(leadId));
      if (previousFollowUps) {
        queryClient.setQueryData<LeadFollowUp[]>(crmKeys.followUps(leadId), (old) => {
          if (!old) return old;
          return old.map(f => f.id === id ? { ...f, status: 'cancelled' } : f);
        });
      }
      return { previousFollowUps };
    },
    onError: (err, id, context) => {
      if (context?.previousFollowUps) {
        queryClient.setQueryData(crmKeys.followUps(leadId), context.previousFollowUps);
      }
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: crmKeys.followUps(leadId) });
      queryClient.invalidateQueries({ queryKey: crmKeys.activities(leadId) });
      queryClient.invalidateQueries({ queryKey: ['leads', leadId] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
      queryClient.invalidateQueries({ queryKey: ['crm', 'pipeline'] });
    },
  });
};
