import axiosInstance from "@/lib/axios";
import {
  PlatformSetting,
  PlatformSettingsGroup,
  PlatformSettingUpdatePayload,
  CachePayload,
  ResetPayload,
  PaginatedResponse,
} from "../types";

export const getSettings = async (params?: Record<string, unknown>): Promise<PaginatedResponse<PlatformSetting>> => {
  const { data } = await axiosInstance.get("/admin/settings/", { params });
  return data;
};

export const getSettingsByGroup = async (group: string, params?: Record<string, unknown>): Promise<PaginatedResponse<PlatformSetting>> => {
  const { data } = await axiosInstance.get(`/admin/settings/${group}/`, { params });
  return data;
};

export const getSetting = async (id: string): Promise<PlatformSetting> => {
  const { data } = await axiosInstance.get(`/admin/settings/detail/${id}/`);
  return data;
};

export const getGroups = async (): Promise<PlatformSettingsGroup[]> => {
  const { data } = await axiosInstance.get("/admin/settings/groups/");
  return data;
};

export const updateSetting = async (id: string, payload: PlatformSettingUpdatePayload): Promise<PlatformSetting> => {
  const { data } = await axiosInstance.patch(`/admin/settings/detail/${id}/`, payload);
  return data;
};

export const initializeSettings = async (): Promise<{ message: string; created: number }> => {
  const { data } = await axiosInstance.post("/admin/settings/initialize/");
  return data;
};

export const resetSettings = async (payload: ResetPayload): Promise<{ message: string; reset_count: number }> => {
  const { data } = await axiosInstance.post("/admin/settings/reset/", payload);
  return data;
};

export const refreshCache = async (payload: CachePayload): Promise<{ message: string; group?: string; key?: string }> => {
  const { data } = await axiosInstance.post("/admin/settings/cache/refresh/", payload);
  return data;
};

export const clearCache = async (payload: CachePayload): Promise<{ message: string; group?: string; key?: string }> => {
  const { data } = await axiosInstance.post("/admin/settings/cache/clear/", payload);
  return data;
};
