"use client";

import { PlatformSetting } from "../../types";
import { SettingsPanel, SettingsSection } from "./settings-panel";

interface FeaturesPanelProps {
  settings: PlatformSetting[];
}

export function FeaturesPanel({ settings }: FeaturesPanelProps) {
  const getSetting = (key: string) => settings.find((s) => s.key === key);

  const coreModules = [
    getSetting("ENABLE_ANALYTICS"),
    getSetting("ENABLE_AI_CHATBOT"),
    getSetting("ENABLE_LEAD_QUALIFICATION")
  ].filter(Boolean) as PlatformSetting[];

  const publicFeatures = [
    getSetting("ENABLE_PUBLIC_CONTACT_FORM"),
    getSetting("ENABLE_EMAIL_NOTIFICATIONS")
  ].filter(Boolean) as PlatformSetting[];

  const mappedKeys = new Set([
    "ENABLE_ANALYTICS",
    "ENABLE_AI_CHATBOT",
    "ENABLE_LEAD_QUALIFICATION",
    "ENABLE_PUBLIC_CONTACT_FORM",
    "ENABLE_EMAIL_NOTIFICATIONS"
  ]);
  const otherSettings = settings.filter((s) => !mappedKeys.has(s.key));

  return (
    <SettingsPanel 
      title="Feature Flags" 
      description="Toggle major platform modules and public features."
    >
      <SettingsSection 
        title="Core Modules" 
        description="Enable or disable entire functional areas of the platform."
        settings={coreModules} 
      />
      <SettingsSection 
        title="Public Features" 
        description="Features exposed to external users or customers."
        settings={publicFeatures} 
      />
      <SettingsSection 
        title="Other Features" 
        settings={otherSettings} 
      />
    </SettingsPanel>
  );
}
