'use client';

import { useQuery, useMutation, useQueryClient, keepPreviousData } from '@tanstack/react-query';
import { usersApi } from '../api';
import type { UserFilters, UserCreatePayload, UserUpdatePayload } from '../types';

export function useUsersList(filters: UserFilters) {
  return useQuery({
    queryKey: ['users', filters],
    queryFn: ({ signal }) => usersApi.list(filters, signal),
    staleTime: 30 * 1000,
    placeholderData: keepPreviousData,
    retry: 1,
  });
}

export function useUserDetail(id: number) {
  return useQuery({
    queryKey: ['users', id],
    queryFn: () => usersApi.getById(id),
    staleTime: 60 * 1000,
    enabled: !!id,
    retry: 1,
  });
}

export function useCreateUser() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: UserCreatePayload) => usersApi.create(data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['users'] }),
  });
}

export function useUpdateUser() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: UserUpdatePayload }) => usersApi.update(id, data),
    onSuccess: (_, vars) => {
      qc.invalidateQueries({ queryKey: ['users', vars.id] });
      qc.invalidateQueries({ queryKey: ['users'] });
    },
  });
}

export function useActivateUser() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => usersApi.activate(id),
    onSuccess: (_, id) => {
      qc.invalidateQueries({ queryKey: ['users', id] });
      qc.invalidateQueries({ queryKey: ['users'] });
    },
  });
}

export function useDeactivateUser() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => usersApi.deactivate(id),
    onSuccess: (_, id) => {
      qc.invalidateQueries({ queryKey: ['users', id] });
      qc.invalidateQueries({ queryKey: ['users'] });
    },
  });
}

export function useResetPassword() {
  return useMutation({
    mutationFn: ({ id, password }: { id: number; password: string }) => usersApi.resetPassword(id, password),
  });
}

export function useBulkActivate() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (ids: number[]) => usersApi.bulkActivate(ids),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['users'] }),
  });
}

export function useBulkDeactivate() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (ids: number[]) => usersApi.bulkDeactivate(ids),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['users'] }),
  });
}

export function useUserAuditLog(id: number, page = 1) {
  return useQuery({
    queryKey: ['users', id, 'audit', page],
    queryFn: () => usersApi.getAuditLog(id, page),
    staleTime: 60 * 1000,
    enabled: !!id,
    retry: 1,
  });
}
