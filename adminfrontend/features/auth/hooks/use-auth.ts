'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useRouter } from 'next/navigation';
import { authApi } from '../api';
import type { LoginRequest, User } from '../types';

const AUTH_QUERY_KEY = ['auth', 'me'];

function getTokens() {
  if (typeof window === 'undefined') return { access: null, refresh: null };
  return {
    access: localStorage.getItem('access_token'),
    refresh: localStorage.getItem('refresh_token'),
  };
}

function setTokens(access: string, refresh: string) {
  localStorage.setItem('access_token', access);
  localStorage.setItem('refresh_token', refresh);
}

function clearTokens() {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
}

export function useAuth() {
  const queryClient = useQueryClient();
  const router = useRouter();

  const { data: user, isLoading, isError } = useQuery<User>({
    queryKey: AUTH_QUERY_KEY,
    queryFn: authApi.getMe,
    retry: false,
    enabled: !!getTokens().access,
  });

  const loginMutation = useMutation({
    mutationFn: (data: LoginRequest) => authApi.login(data),
    onSuccess: (response) => {
      setTokens(response.access, response.refresh);
      queryClient.invalidateQueries({ queryKey: AUTH_QUERY_KEY });
      router.push('/dashboard');
    },
  });

  const logout = async () => {
    const { refresh } = getTokens();
    try {
      if (refresh) await authApi.logout(refresh);
    } catch {
      // Ignore logout errors
    } finally {
      clearTokens();
      queryClient.clear();
      router.push('/login');
    }
  };

  const isAuthenticated = !!user && !isError;

  return {
    user,
    isLoading,
    isAuthenticated,
    login: loginMutation.mutateAsync,
    loginError: loginMutation.error,
    isLoginLoading: loginMutation.isPending,
    logout,
  };
}
