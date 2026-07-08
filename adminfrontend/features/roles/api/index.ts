import api from '@/lib/axios';
import type { Role, RoleDetail, Permission, RoleUser, RoleFilters } from '../types';

interface PaginatedResponse<T> { success: boolean; data: T[]; meta: { pagination: { page: number; page_size: number; total_count: number; total_pages: number } } }

export const rolesApi = {
  list: async (filters: RoleFilters = {}): Promise<PaginatedResponse<Role>> => {
    const params = new URLSearchParams();
    if (filters.search) params.set('search', filters.search);
    if (filters.ordering) params.set('ordering', filters.ordering);
    if (filters.page) params.set('page', String(filters.page));
    if (filters.page_size) params.set('page_size', String(filters.page_size));
    const res = await api.get(`/admin/roles/?${params.toString()}`);
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

  getRoleUsers: async (id: number, search?: string): Promise<PaginatedResponse<RoleUser>> => {
    const params = search ? `?search=${search}` : '';
    const res = await api.get(`/admin/roles/${id}/users/${params}`);
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
