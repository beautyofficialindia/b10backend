'use client';

import { useQuery, useMutation, useQueryClient, keepPreviousData } from '@tanstack/react-query';
import { rolesApi } from '../api';
import type { RoleFilters } from '../types';
import { useHasPermission } from '@/features/auth';

export function useRolesList(filters: RoleFilters) {
  const hasPerm = useHasPermission(['auth.view_group']);
  return useQuery({
    queryKey: ['roles', filters],
    queryFn: ({ signal }) => rolesApi.list(filters, signal),
    staleTime: 30 * 1000,
    placeholderData: keepPreviousData,
    retry: 1,
    enabled: hasPerm,
  });
}

export function useRoleDetail(id: number) {
  const hasPerm = useHasPermission(['auth.view_group']);
  return useQuery({
    queryKey: ['roles', id],
    queryFn: () => rolesApi.getById(id),
    staleTime: 60 * 1000,
    enabled: !!id && hasPerm,
  });
}

export function useAvailablePermissions() {
  const hasPerm = useHasPermission(['auth.view_permission']);
  return useQuery({
    queryKey: ['roles', 'permissions'],
    queryFn: () => rolesApi.getAvailablePermissions(),
    staleTime: 5 * 60 * 1000,
    enabled: hasPerm,
  });
}

export function useRoleUsers(id: number, search?: string) {
  const hasPerm = useHasPermission(['auth.view_user']);
  return useQuery({
    queryKey: ['roles', id, 'users', search],
    queryFn: ({ signal }) => rolesApi.getRoleUsers(id, search, signal),
    staleTime: 30 * 1000,
    enabled: !!id && hasPerm,
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

// Mock hook since backend doesn't have Role Audit Log API yet
export function useRoleAuditLog(id: number) {
  const hasPerm = useHasPermission(['auth.view_group']);
  return useQuery({
    queryKey: ['roles', id, 'audit'],
    queryFn: async () => {
      // Simulate network delay
      await new Promise(resolve => setTimeout(resolve, 800));
      return {
        data: [
          {
            id: 1,
            description: `Role was created`,
            actor_username: 'admin',
            created_at: new Date(Date.now() - 86400000 * 2).toISOString(),
            action: 'CREATE'
          },
          {
            id: 2,
            description: `Permissions were updated`,
            actor_username: 'admin',
            created_at: new Date(Date.now() - 86400000).toISOString(),
            action: 'UPDATE'
          }
        ]
      };
    },
    staleTime: 60 * 1000,
    enabled: !!id && hasPerm,
  });
}
