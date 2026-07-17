"use client";

import { PageContainer, PageHeader } from "@/components/layout";
import { PermissionGuard } from "@/features/auth";
import { FeatureGuard } from "@/features/platform-settings/components/feature-guard";
import { AnalyticsNavigation } from "@/features/analytics/components/ui/analytics-navigation";
import React from "react";

export default function AnalyticsLayout({ children }: { children: React.ReactNode }) {
  return (
    <FeatureGuard feature="ENABLE_ANALYTICS">
      <PermissionGuard permissions={["analytics.view_analyticsevent"]}>
        <PageContainer>
          <PageHeader 
            title="Analytics" 
            description="Overview of your business performance."
          />
          <AnalyticsNavigation />
          {children}
        </PageContainer>
      </PermissionGuard>
    </FeatureGuard>
  );
}
