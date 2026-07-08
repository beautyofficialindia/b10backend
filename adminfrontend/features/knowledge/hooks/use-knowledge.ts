'use client';

import { useQuery, useMutation, useQueryClient, keepPreviousData } from '@tanstack/react-query';
import { knowledgeApi } from '../api';
import type { KBFilters, KBCreatePayload } from '../types';

export function useKnowledgeList(filters: KBFilters) {
  return useQuery({
    queryKey: ['knowledge', filters],
    queryFn: () => knowledgeApi.list(filters),
    staleTime: 30 * 1000,
    placeholderData: keepPreviousData,
    retry: 1,
  });
}

export function useKnowledgeDetail(id: string) {
  return useQuery({
    queryKey: ['knowledge', id],
    queryFn: () => knowledgeApi.getById(id),
    staleTime: 60 * 1000,
    enabled: !!id,
    retry: 1,
  });
}

export function useCreateEntry() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: KBCreatePayload) => knowledgeApi.create(data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['knowledge'] }),
  });
}

export function useUpdateEntry() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<KBCreatePayload> }) => knowledgeApi.update(id, data),
    onSuccess: (_, vars) => {
      qc.invalidateQueries({ queryKey: ['knowledge', vars.id] });
      qc.invalidateQueries({ queryKey: ['knowledge'] });
    },
  });
}

export function usePublishEntry() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => knowledgeApi.publish(id),
    onSuccess: (_, id) => {
      qc.invalidateQueries({ queryKey: ['knowledge', id] });
      qc.invalidateQueries({ queryKey: ['knowledge'] });
    },
  });
}

export function useArchiveEntry() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => knowledgeApi.archive(id),
    onSuccess: (_, id) => {
      qc.invalidateQueries({ queryKey: ['knowledge', id] });
      qc.invalidateQueries({ queryKey: ['knowledge'] });
    },
  });
}

export function useDeleteEntry() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => knowledgeApi.delete(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['knowledge'] }),
  });
}
