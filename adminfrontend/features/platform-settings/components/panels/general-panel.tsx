"use client";

import { PlatformSetting } from "../../types";
import { SettingsPanel, SettingsSection } from "./settings-panel";

interface GeneralPanelProps {
  settings: PlatformSetting[];
}

export function GeneralPanel({ settings }: GeneralPanelProps) {
  // Currently defaults.py doesn't seed GENERAL settings, so this will be mostly future-proofing
  // based on the user's requirements: Company Name, Email, etc.
  
  const getSettingsByPrefix = (prefix: string) => settings.filter((s) => s.key.startsWith(prefix));

  const companySettings = getSettingsByPrefix("COMPANY_");
  const brandingSettings = getSettingsByPrefix("BRANDING_");
  const otherSettings = settings.filter(
    (s) => !s.key.startsWith("COMPANY_") && !s.key.startsWith("BRANDING_")
  );

  return (
    <SettingsPanel 
      title="General Settings" 
      description="Company information, branding, and global platform configuration."
    >
      <SettingsSection 
        title="Company Information" 
        settings={companySettings} 
      />
      <SettingsSection 
        title="Branding" 
        settings={brandingSettings} 
      />
      <SettingsSection 
        title="Other General Settings" 
        settings={otherSettings} 
      />
    </SettingsPanel>
  );
}
