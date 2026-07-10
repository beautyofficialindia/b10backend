'use client';

import { useQuery, useMutation, useQueryClient, keepPreviousData } from '@tanstack/react-query';
import { rolesApi } from '../api';
import type { RoleFilters } from '../types';

export function useRolesList(filters: RoleFilters) {
  return useQuery({
    queryKey: ['roles', filters],
    queryFn: ({ signal }) => rolesApi.list(filters, signal),
    staleTime: 30 * 1000,
    placeholderData: keepPreviousData,
    retry: 1,
  });
}

export function useRoleDetail(id: number) {
  return useQuery({
    queryKey: ['roles', id],
    queryFn: () => rolesApi.getById(id),
    staleTime: 60 * 1000,
    enabled: !!id,
  });
}

export function useAvailablePermissions() {
  return useQuery({
    queryKey: ['roles', 'permissions'],
    queryFn: () => rolesApi.getAvailablePermissions(),
    staleTime: 5 * 60 * 1000,
  });
}

export function useRoleUsers(id: number, search?: string) {
  return useQuery({
    queryKey: ['roles', id, 'users', search],
    queryFn: ({ signal }) => rolesApi.getRoleUsers(id, search, signal),
    staleTime: 30 * 1000,
    enabled: !!id,
  });
}

export function useCreateRole() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: { name: string; permissions?: string[] }) => rolesApi.create(data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['roles'] }),
  });
}

export function useUpdateRole() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, name }: { id: number; name: string }) => rolesApi.update(id, { name }),
    onSuccess: (_, vars) => {
      qc.invalidateQueries({ queryKey: ['roles', vars.id] });
      qc.invalidateQueries({ queryKey: ['roles'] });
    },
  });
}

export function useDeleteRole() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => rolesApi.delete(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['roles'] }),
  });
}

export function useSetPermissions() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, permissions }: { id: number; permissions: string[] }) => rolesApi.setPermissions(id, permissions),
    onSuccess: (_, vars) => {
      qc.invalidateQueries({ queryKey: ['roles', vars.id] });
      qc.invalidateQueries({ queryKey: ['roles'] });
    },
  });
}

export function useAssignUsers() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, user_ids }: { id: number; user_ids: number[] }) => rolesApi.assignUsers(id, user_ids),
    onSuccess: (_, vars) => {
      qc.invalidateQueries({ queryKey: ['roles', vars.id] });
      qc.invalidateQueries({ queryKey: ['roles'] });
    },
  });
}

export function useRemoveUsers() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, user_ids }: { id: number; user_ids: number[] }) => rolesApi.removeUsers(id, user_ids),
    onSuccess: (_, vars) => {
      qc.invalidateQueries({ queryKey: ['roles', vars.id] });
      qc.invalidateQueries({ queryKey: ['roles'] });
    },
  });
}
