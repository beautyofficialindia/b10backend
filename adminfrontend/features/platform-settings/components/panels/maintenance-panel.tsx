"use client";

import { PlatformSetting } from "../../types";
import { SettingsPanel, SettingsSection } from "./settings-panel";

interface MaintenancePanelProps {
  settings: PlatformSetting[];
}

export function MaintenancePanel({ settings }: MaintenancePanelProps) {
  const getSetting = (key: string) => settings.find((s) => s.key === key);

  const modeSettings = [getSetting("MAINTENANCE_MODE")].filter(Boolean) as PlatformSetting[];
  const restrictionsSettings = [getSetting("READ_ONLY_MODE")].filter(Boolean) as PlatformSetting[];
  const messagesSettings = [
    getSetting("MAINTENANCE_BANNER_ENABLED"), 
    getSetting("MAINTENANCE_MESSAGE")
  ].filter(Boolean) as PlatformSetting[];

  const mappedKeys = new Set([
    "MAINTENANCE_MODE", 
    "READ_ONLY_MODE", 
    "MAINTENANCE_BANNER_ENABLED", 
    "MAINTENANCE_MESSAGE"
  ]);
  const otherSettings = settings.filter((s) => !mappedKeys.has(s.key));

  return (
    <SettingsPanel 
      title="Maintenance & Restrictions" 
      description="Manage platform downtime and access restrictions."
    >
      <SettingsSection 
        title="Maintenance Mode" 
        description="Global kill-switches for platform access."
        settings={modeSettings} 
      />
      <SettingsSection 
        title="Restrictions" 
        description="Fine-grained access controls."
        settings={restrictionsSettings} 
      />
      <SettingsSection 
        title="Messages" 
        description="Banners and notices displayed to users."
        settings={messagesSettings} 
      />
      <SettingsSection 
        title="Other Maintenance Settings" 
        settings={otherSettings} 
      />
    </SettingsPanel>
  );
}
