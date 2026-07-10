import api from '@/lib/axios';
import { buildQueryParams } from '@/lib/utils/build-query-params';
import type { Role, RoleDetail, Permission, RoleUser, RoleFilters } from '../types';

interface PaginatedResponse<T> { success: boolean; data: T[]; meta: { pagination: { page: number; page_size: number; total_count: number; total_pages: number } } }

export const rolesApi = {
  list: async (filters: RoleFilters = {}, signal?: AbortSignal): Promise<PaginatedResponse<Role>> => {
    const params = buildQueryParams(filters);
    const res = await api.get(`/admin/roles/?${params.toString()}`, { signal });
    return res.data;
  },

  getById: async (id: number): Promise<{ data: RoleDetail }> => {
    const res = await api.get(`/admin/roles/${id}/`);
    return res.data;
  },

  create: async (data: { name: string; permissions?: string[] }): Promise<{ data: RoleDetail }> => {
    const res = await api.post('/admin/roles/', data);
    return res.data;
  },

  update: async (id: number, data: { name: string }): Promise<{ data: RoleDetail }> => {
    const res = await api.patch(`/admin/roles/${id}/`, data);
    return res.data;
  },

  delete: async (id: number): Promise<void> => {
    await api.delete(`/admin/roles/${id}/`);
  },

  getAvailablePermissions: async (): Promise<{ data: Permission[] }> => {
    const res = await api.get('/admin/roles/permissions/');
    return res.data;
  },

  setPermissions: async (id: number, permissions: string[]): Promise<{ data: RoleDetail }> => {
    const res = await api.put(`/admin/roles/${id}/set-permissions/`, { permissions });
    return res.data;
  },

  getRoleUsers: async (id: number, search?: string, signal?: AbortSignal): Promise<PaginatedResponse<RoleUser>> => {
    const params = buildQueryParams({ search });
    const queryString = params.toString() ? `?${params.toString()}` : '';
    const res = await api.get(`/admin/roles/${id}/users/${queryString}`, { signal });
    return res.data;
  },

  assignUsers: async (id: number, user_ids: number[]): Promise<{ data: { added_count: number; skipped: { id: number; reason: string }[] } }> => {
    const res = await api.post(`/admin/roles/${id}/assign-users/`, { user_ids });
    return res.data;
  },

  removeUsers: async (id: number, user_ids: number[]): Promise<{ data: { removed_count: number; skipped: { id: number; reason: string }[] } }> => {
    const res = await api.post(`/admin/roles/${id}/remove-users/`, { user_ids });
    return res.data;
  },
};
