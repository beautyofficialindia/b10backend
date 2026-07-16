import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  getSettings,
  getSettingsByGroup,
  getSetting,
  getGroups,
  updateSetting,
  initializeSettings,
  resetSettings,
  refreshCache,
  clearCache,
} from "../api";
import {
  PlatformSettingUpdatePayload,
  CachePayload,
  ResetPayload,
} from "../types";

export const platformSettingsKeys = {
  all: ["platformSettings"] as const,
  lists: () => [...platformSettingsKeys.all, "list"] as const,
  list: (filters: string | Record<string, unknown>) => [...platformSettingsKeys.lists(), { filters }] as const,
  groups: () => [...platformSettingsKeys.all, "groups"] as const,
  groupLists: (group: string) => [...platformSettingsKeys.groups(), group, "list"] as const,
  groupList: (group: string, filters: string | Record<string, unknown>) => [...platformSettingsKeys.groupLists(group), { filters }] as const,
  details: () => [...platformSettingsKeys.all, "detail"] as const,
  detail: (id: string) => [...platformSettingsKeys.details(), id] as const,
};

export const useSettings = (params?: Record<string, unknown>, enabled: boolean = true) => {
  return useQuery({
    queryKey: platformSettingsKeys.list(params || {}),
    queryFn: () => getSettings(params),
    enabled,
  });
};

export const useSettingsByGroup = (group: string, params?: Record<string, unknown>, enabled: boolean = true) => {
  return useQuery({
    queryKey: platformSettingsKeys.groupList(group, params || {}),
    queryFn: () => getSettingsByGroup(group, params),
    enabled: !!group && enabled,
  });
};

export const useSetting = (id: string, enabled: boolean = true) => {
  return useQuery({
    queryKey: platformSettingsKeys.detail(id),
    queryFn: () => getSetting(id),
    enabled: !!id && enabled,
  });
};

export const useSettingsGroups = (enabled: boolean = true) => {
  return useQuery({
    queryKey: platformSettingsKeys.groups(),
    queryFn: () => getGroups(),
    enabled,
  });
};

export const useUpdateSetting = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: PlatformSettingUpdatePayload }) => updateSetting(id, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: platformSettingsKeys.all });
    },
  });
};

export const useInitializeSettings = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: initializeSettings,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: platformSettingsKeys.all });
    },
  });
};

export const useResetSettings = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: ResetPayload) => resetSettings(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: platformSettingsKeys.all });
    },
  });
};

export const useRefreshSettingsCache = () => {
  return useMutation({
    mutationFn: (payload: CachePayload) => refreshCache(payload),
  });
};

export const useClearSettingsCache = () => {
  return useMutation({
    mutationFn: (payload: CachePayload) => clearCache(payload),
  });
};
