"use client";

import { PlatformSetting } from "../../types";
import { SettingsPanel, SettingsSection } from "./settings-panel";

interface AnalyticsPanelProps {
  settings: PlatformSetting[];
}

export function AnalyticsPanel({ settings }: AnalyticsPanelProps) {
  const getSetting = (key: string) => settings.find((s) => s.key === key);

  const trackingSettings = [
    getSetting("TRACK_CONVERSATIONS"), 
    getSetting("TRACK_LEADS"),
    getSetting("TRACK_CRM_ACTIONS")
  ].filter(Boolean) as PlatformSetting[];
  
  const aggregationSettings = [
    getSetting("ENABLE_ANALYTICS")
  ].filter(Boolean) as PlatformSetting[];

  const mappedKeys = new Set([
    "TRACK_CONVERSATIONS", 
    "TRACK_LEADS", 
    "TRACK_CRM_ACTIONS", 
    "ENABLE_ANALYTICS"
  ]);
  const otherSettings = settings.filter((s) => !mappedKeys.has(s.key));

  return (
    <SettingsPanel 
      title="Analytics Configuration" 
      description="Control data collection, tracking, and aggregation rules."
    >
      <SettingsSection 
        title="Aggregation" 
        description="Global analytics engine settings."
        settings={aggregationSettings} 
      />
      <SettingsSection 
        title="Tracking" 
        description="Configure which user actions are logged."
        settings={trackingSettings} 
      />
      <SettingsSection 
        title="Other Analytics Settings" 
        settings={otherSettings} 
      />
    </SettingsPanel>
  );
}
