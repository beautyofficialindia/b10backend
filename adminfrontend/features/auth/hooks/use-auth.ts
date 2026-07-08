'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useRouter } from 'next/navigation';
import { useCallback, useMemo } from 'react';
import { authApi } from '../api';
import type { LoginRequest, AuthUser } from '../types';

const AUTH_QUERY_KEY = ['auth', 'me'];

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

  // Determine auth state:
  // - If no token exists and query hasn't fetched, user is not authenticated
  // - If query is loading, we're restoring session
  // - If query errored, session is invalid
  const isAuthenticated = useMemo(() => !!user && !isError, [user, isError]);

  // isLoading should be true only while actively checking session
  const isCheckingAuth = isLoading && hasAccessToken();
  // If no token exists, we're not loading — user is simply not authenticated
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
