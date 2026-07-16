"use client";

import { useFeatureFlags } from "@/features/platform-settings/providers";
import { AlertTriangle } from "lucide-react";

export function MaintenanceBanner() {
  const { flags, strings, isLoading } = useFeatureFlags();

  if (isLoading) return null;

  const isBannerEnabled = flags["MAINTENANCE_BANNER_ENABLED"];
  const message = strings["MAINTENANCE_MESSAGE"] || "The platform is currently undergoing maintenance.";

  if (!isBannerEnabled) return null;

  return (
    <div className="bg-destructive/15 text-destructive px-4 py-2 flex items-center justify-center gap-2 text-sm font-medium border-b border-destructive/20">
      <AlertTriangle className="h-4 w-4" />
      <span>{message}</span>
    </div>
  );
}
