import api from '@/lib/axios';
import type { UserListResponse, UserFilters, UserDetail, UserCreatePayload, UserUpdatePayload, AuditLogEntry, BulkResult } from '../types';

export const usersApi = {
  list: async (filters: UserFilters = {}): Promise<UserListResponse> => {
    const params = new URLSearchParams();
    if (filters.search) params.set('search', filters.search);
    if (filters.is_active) params.set('is_active', filters.is_active);
    if (filters.is_superuser) params.set('is_superuser', filters.is_superuser);
    if (filters.group) params.set('group', filters.group);
    if (filters.ordering) params.set('ordering', filters.ordering);
    if (filters.page) params.set('page', String(filters.page));
    if (filters.page_size) params.set('page_size', String(filters.page_size));
    const res = await api.get(`/admin/users/?${params.toString()}`);
    return res.data;
  },

  getById: async (id: number): Promise<{ data: UserDetail }> => {
    const res = await api.get(`/admin/users/${id}/`);
    return res.data;
  },

  create: async (data: UserCreatePayload): Promise<{ data: UserDetail }> => {
    const res = await api.post('/admin/users/', data);
    return res.data;
  },

  update: async (id: number, data: UserUpdatePayload): Promise<{ data: UserDetail }> => {
    const res = await api.patch(`/admin/users/${id}/`, data);
    return res.data;
  },

  activate: async (id: number): Promise<{ data: UserDetail }> => {
    const res = await api.post(`/admin/users/${id}/activate/`);
    return res.data;
  },

  deactivate: async (id: number): Promise<{ data: UserDetail }> => {
    const res = await api.post(`/admin/users/${id}/deactivate/`);
    return res.data;
  },

  resetPassword: async (id: number, password: string): Promise<void> => {
    await api.post(`/admin/users/${id}/reset-password/`, { password });
  },

  bulkActivate: async (user_ids: number[]): Promise<{ data: BulkResult }> => {
    const res = await api.post('/admin/users/bulk-activate/', { user_ids });
    return res.data;
  },

  bulkDeactivate: async (user_ids: number[]): Promise<{ data: BulkResult }> => {
    const res = await api.post('/admin/users/bulk-deactivate/', { user_ids });
    return res.data;
  },

  getAuditLog: async (id: number, page = 1): Promise<{ data: AuditLogEntry[]; meta: { pagination: { total_count: number; total_pages: number; page: number; page_size: number } } }> => {
    const res = await api.get(`/admin/users/${id}/audit-log/?page=${page}`);
    return res.data;
  },
};
