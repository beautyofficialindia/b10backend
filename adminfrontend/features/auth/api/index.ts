import api from '@/lib/axios';
import type { LoginRequest, LoginResponse, User } from '../types';

export const authApi = {
  login: async (data: LoginRequest): Promise<LoginResponse> => {
    const res = await api.post('/auth/login/', data);
    return res.data;
  },

  logout: async (refresh: string): Promise<void> => {
    await api.post('/auth/logout/', { refresh });
  },

  getMe: async (): Promise<User> => {
    const res = await api.get('/auth/me/');
    return res.data;
  },
};
