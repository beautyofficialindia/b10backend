import { useQuery } from "@tanstack/react-query";
import { getOverviewAnalytics, getLeadAnalytics, getCrmAnalytics, getChatAnalytics, getKnowledgeAnalytics, getUserAnalytics } from "../api";
import { OverviewResponse, LeadAnalyticsResponse, CrmAnalyticsResponse, ChatAnalyticsResponse, KnowledgeAnalyticsResponse, UserAnalyticsResponse } from "../types";

export const useOverviewAnalytics = (queryString?: string) => {
  return useQuery<OverviewResponse>({
    queryKey: ["analytics", "overview", queryString],
    queryFn: () => getOverviewAnalytics(queryString),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

export const useLeadAnalytics = (queryString?: string) => {
  return useQuery<LeadAnalyticsResponse>({
    queryKey: ["analytics", "leads", queryString],
    queryFn: () => getLeadAnalytics(queryString),
    staleTime: 5 * 60 * 1000,
  });
};

export const useCrmAnalytics = (queryString?: string) => {
  return useQuery<CrmAnalyticsResponse>({
    queryKey: ["analytics", "crm", queryString],
    queryFn: () => getCrmAnalytics(queryString),
    staleTime: 5 * 60 * 1000,
  });
};

export const useChatAnalytics = (queryString?: string) => {
  return useQuery<ChatAnalyticsResponse>({
    queryKey: ["analytics", "chat", queryString],
    queryFn: () => getChatAnalytics(queryString),
    staleTime: 5 * 60 * 1000,
  });
};

export const useKnowledgeAnalytics = (queryString?: string) => {
  return useQuery<KnowledgeAnalyticsResponse>({
    queryKey: ["analytics", "knowledge", queryString],
    queryFn: () => getKnowledgeAnalytics(queryString),
    staleTime: 5 * 60 * 1000,
  });
};

export const useUserAnalytics = (queryString?: string) => {
  return useQuery<UserAnalyticsResponse>({
    queryKey: ["analytics", "users", queryString],
    queryFn: () => getUserAnalytics(queryString),
    staleTime: 5 * 60 * 1000,
  });
};
