import api from '@/lib/axios';
import type { LoginRequest, LoginResponse, AuthUser, ChangePasswordRequest, UpdateProfileRequest } from '../types';

export const authApi = {
  login: async (data: LoginRequest): Promise<LoginResponse> => {
    const res = await api.post('/auth/login/', data);
    return res.data;
  },

  logout: async (refresh: string): Promise<void> => {
    await api.post('/auth/logout/', { refresh });
  },

  getMe: async (): Promise<AuthUser> => {
    const res = await api.get('/auth/me/');
    return res.data;
  },

  changePassword: async (data: ChangePasswordRequest): Promise<{ success: boolean; message: string }> => {
    const res = await api.post('/auth/change-password/', data);
    return res.data;
  },

  updateProfile: async (data: UpdateProfileRequest): Promise<AuthUser> => {
    const res = await api.patch('/auth/me/', data);
    return res.data;
  },
};
