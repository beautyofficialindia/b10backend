import api from '@/lib/axios';
import type { Setting, SettingCategory } from '../types';

export const settingsApi = {
  listAll: async (search?: string, category?: string): Promise<{ data: Setting[] }> => {
    const params = new URLSearchParams();
    if (search) params.set('search', search);
    if (category) params.set('category', category);
    const res = await api.get(`/admin/settings/?${params.toString()}`);
    return res.data;
  },

  getCategory: async (category: SettingCategory): Promise<{ data: Setting[] }> => {
    const res = await api.get(`/admin/settings/${category}/`);
    return res.data;
  },

  updateCategory: async (category: SettingCategory, settings: Record<string, unknown>): Promise<{ data: Setting[] }> => {
    const res = await api.patch(`/admin/settings/${category}/`, { settings });
    return res.data;
  },

  getPublic: async (): Promise<{ data: { category: string; key: string; value: unknown }[] }> => {
    const res = await api.get('/settings/public/');
    return res.data;
  },
};
