import api from '@/lib/axios';
import type {
  Notification,
  NotificationListResponse,
  NotificationCategory,
  UnreadCountResponse,
} from '../types';

export const notificationsApi = {
  list: async (
    category?: NotificationCategory | 'ALL',
    page = 1,
    pageSize = 20,
    signal?: AbortSignal,
  ): Promise<NotificationListResponse> => {
    const params = new URLSearchParams();
    if (category && category !== 'ALL') params.set('category', category);
    params.set('page', String(page));
    params.set('page_size', String(pageSize));
    const res = await api.get(`/admin/notifications/?${params.toString()}`, { signal });
    return res.data;
  },

  getById: async (id: string): Promise<Notification> => {
    const res = await api.get(`/admin/notifications/${id}/`);
    return res.data;
  },

  unreadCount: async (): Promise<UnreadCountResponse> => {
    const res = await api.get('/admin/notifications/unread-count/');
    return res.data;
  },

  markRead: async (id: string): Promise<Notification> => {
    const res = await api.patch(`/admin/notifications/${id}/read/`);
    return res.data;
  },

  markUnread: async (id: string): Promise<Notification> => {
    const res = await api.patch(`/admin/notifications/${id}/unread/`);
    return res.data;
  },

  markAllRead: async (): Promise<{ marked_read: number }> => {
    const res = await api.patch('/admin/notifications/read-all/');
    return res.data;
  },

  deleteAllRead: async (): Promise<{ deleted: number }> => {
    const res = await api.delete('/admin/notifications/read/');
    return res.data;
  },
};
