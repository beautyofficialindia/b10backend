'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { settingsApi } from '../api';
import type { SettingCategory } from '../types';

export function useSettingsCategory(category: SettingCategory) {
  return useQuery({
    queryKey: ['settings', category],
    queryFn: () => settingsApi.getCategory(category),
    staleTime: 60 * 1000,
    retry: 1,
  });
}

export function useUpdateSettings() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ category, settings }: { category: SettingCategory; settings: Record<string, unknown> }) =>
      settingsApi.updateCategory(category, settings),
    onSuccess: (_, vars) => {
      qc.invalidateQueries({ queryKey: ['settings', vars.category] });
      qc.invalidateQueries({ queryKey: ['settings'] });
    },
  });
}

export function usePublicSettings() {
  return useQuery({
    queryKey: ['settings', 'public'],
    queryFn: () => settingsApi.getPublic(),
    staleTime: 5 * 60 * 1000,
  });
}
