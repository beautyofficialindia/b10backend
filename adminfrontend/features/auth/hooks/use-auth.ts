'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useRouter } from 'next/navigation';
import { useCallback, useMemo } from 'react';
import { authApi } from '../api';
import type { LoginRequest, AuthUser, ChangePasswordRequest, UpdateProfileRequest } from '../types';

export const AUTH_QUERY_KEY = ['auth', 'me'];

function hasAccessToken(): boolean {
  if (typeof window === 'undefined') return false;
  return !!localStorage.getItem('access_token');
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

  const { data: user, isLoading, isError, isFetched } = useQuery<AuthUser>({
    queryKey: AUTH_QUERY_KEY,
    queryFn: authApi.getMe,
    retry: false,
    enabled: hasAccessToken(),
    staleTime: 5 * 60 * 1000, // 5 min
  });

  const loginMutation = useMutation({
    mutationFn: (data: LoginRequest) => authApi.login(data),
    onSuccess: (response) => {
      setTokens(response.access, response.refresh);
      queryClient.invalidateQueries({ queryKey: AUTH_QUERY_KEY });
      router.push('/dashboard');
    },
  });

  const logout = useCallback(async () => {
    const refresh = localStorage.getItem('refresh_token');
    try {
      if (refresh) await authApi.logout(refresh);
    } catch {
      // Ignore logout API errors
    } finally {
      clearTokens();
      queryClient.clear();
      router.push('/login');
    }
  }, [queryClient, router]);

  const isAuthenticated = useMemo(() => !!user && !isError, [user, isError]);
  const isCheckingAuth = isLoading && hasAccessToken();
  const effectiveLoading = hasAccessToken() ? isCheckingAuth : false;

  return {
    user: user ?? null,
    isLoading: effectiveLoading,
    isAuthenticated,
    isFetched,
    login: loginMutation.mutateAsync,
    loginError: loginMutation.error,
    isLoginLoading: loginMutation.isPending,
    logout,
  };
}

export function useChangePassword() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: ChangePasswordRequest) => authApi.changePassword(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: AUTH_QUERY_KEY });
    }
  });
}

export function useUpdateProfile() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: UpdateProfileRequest) => authApi.updateProfile(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: AUTH_QUERY_KEY });
    }
  });
}

export function useHasPermission(permissions: readonly string[] = [], requireAll = true) {
  const { user } = useAuth();
  if (!user) return false;
  if (user.is_superuser) return true;
  if (permissions.length === 0) return true;
  return requireAll
    ? permissions.every((p) => user.permissions?.includes(p))
    : permissions.some((p) => user.permissions?.includes(p));
}