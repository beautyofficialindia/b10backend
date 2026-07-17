'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { notificationsApi } from '../api';
import type { NotificationCategory } from '../types';

const NOTIFICATIONS_KEY = 'notifications';
const UNREAD_COUNT_KEY = ['notifications', 'unread-count'];

export function useNotifications(category?: NotificationCategory | 'ALL', page = 1) {
  return useQuery({
    queryKey: [NOTIFICATIONS_KEY, { category, page }],
    queryFn: ({ signal }) => notificationsApi.list(category, page, 20, signal),
    staleTime: 60_000,
    placeholderData: (prev) => prev,
    retry: 1,
  });
}

export function useNotificationById(id: string) {
  return useQuery({
    queryKey: [NOTIFICATIONS_KEY, id],
    queryFn: () => notificationsApi.getById(id),
    staleTime: 60_000,
    enabled: !!id,
  });
}

export function useUnreadCount() {
  return useQuery({
    queryKey: UNREAD_COUNT_KEY,
    queryFn: notificationsApi.unreadCount,
    staleTime: 30_000,
    refetchInterval: 60_000,
    retry: 1,
  });
}

export function useMarkRead() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => notificationsApi.markRead(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [NOTIFICATIONS_KEY] });
      queryClient.invalidateQueries({ queryKey: UNREAD_COUNT_KEY });
    },
  });
}

export function useMarkUnread() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => notificationsApi.markUnread(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [NOTIFICATIONS_KEY] });
      queryClient.invalidateQueries({ queryKey: UNREAD_COUNT_KEY });
    },
  });
}

export function useMarkAllRead() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: notificationsApi.markAllRead,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [NOTIFICATIONS_KEY] });
      queryClient.invalidateQueries({ queryKey: UNREAD_COUNT_KEY });
    },
  });
}

export function useDeleteAllRead() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: notificationsApi.deleteAllRead,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [NOTIFICATIONS_KEY] });
      queryClient.invalidateQueries({ queryKey: UNREAD_COUNT_KEY });
    },
  });
}
