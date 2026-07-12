import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '@/lib/axios';
import { crmKeys } from './index';
import type { LeadNote } from '../types';

export const useLeadNotes = (leadId: string) => {
  return useQuery({
    queryKey: crmKeys.notes(leadId),
    queryFn: async () => {
      const res = await api.get<LeadNote[]>(`/admin/leads/${leadId}/notes/`);
      return res.data;
    },
    enabled: !!leadId,
    staleTime: 60 * 1000,
  });
};

export const useCreateLeadNote = (leadId: string) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: { note: string }) => {
      const res = await api.post<LeadNote>(`/admin/leads/${leadId}/notes/`, data);
      return res.data;
    },
    onMutate: async (newNoteData) => {
      await queryClient.cancelQueries({ queryKey: crmKeys.notes(leadId) });

      const previousNotes = queryClient.getQueryData<LeadNote[]>(crmKeys.notes(leadId));

      const optimisticNote: LeadNote = {
        id: `temp-${Date.now()}`,
        lead: leadId,
        author_id: 'optimistic',
        author: {
          id: -1, 
          username: 'Current User',
          full_name: 'Current User'
        },
        note: newNoteData.note,
        created_at: new Date().toISOString(),
      };

      queryClient.setQueryData<LeadNote[]>(crmKeys.notes(leadId), (old) => {
        if (!old) return [optimisticNote];
        return [optimisticNote, ...old];
      });

      return { previousNotes };
    },
    onError: (err, newNote, context) => {
      if (context?.previousNotes) {
        queryClient.setQueryData(crmKeys.notes(leadId), context.previousNotes);
      }
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: crmKeys.notes(leadId) });
    },
  });
};
