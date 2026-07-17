import api from "@/lib/axios";
import { OverviewResponse, LeadAnalyticsResponse, CrmAnalyticsResponse, ChatAnalyticsResponse, KnowledgeAnalyticsResponse, UserAnalyticsResponse } from "../types";

export const getOverviewAnalytics = async (queryString?: string): Promise<OverviewResponse> => {
  const url = queryString ? `/admin/analytics/overview/?${queryString}` : "/admin/analytics/overview/";
  const { data } = await api.get(url);
  return data;
};

export const getLeadAnalytics = async (queryString?: string): Promise<LeadAnalyticsResponse> => {
  const url = queryString ? `/admin/analytics/leads/?${queryString}` : "/admin/analytics/leads/";
  const { data } = await api.get(url);
  return data;
};

export const getCrmAnalytics = async (queryString?: string): Promise<CrmAnalyticsResponse> => {
  const url = queryString ? `/admin/analytics/crm/?${queryString}` : "/admin/analytics/crm/";
  const { data } = await api.get(url);
  return data;
};

export const getChatAnalytics = async (queryString?: string): Promise<ChatAnalyticsResponse> => {
  const url = queryString ? `/admin/analytics/chat/?${queryString}` : "/admin/analytics/chat/";
  const { data } = await api.get(url);
  return data;
};

export const getKnowledgeAnalytics = async (queryString?: string): Promise<KnowledgeAnalyticsResponse> => {
  const url = queryString ? `/admin/analytics/knowledge/?${queryString}` : "/admin/analytics/knowledge/";
  const { data } = await api.get(url);
  return data;
};

export const getUserAnalytics = async (queryString?: string): Promise<UserAnalyticsResponse> => {
  const url = queryString ? `/admin/analytics/users/?${queryString}` : "/admin/analytics/users/";
  const { data } = await api.get(url);
  return data;
};
