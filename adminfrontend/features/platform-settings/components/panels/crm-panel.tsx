"use client";

import { PlatformSetting } from "../../types";
import { SettingsPanel, SettingsSection } from "./settings-panel";

interface CRMPanelProps {
  settings: PlatformSetting[];
}

export function CRMPanel({ settings }: CRMPanelProps) {
  const getSetting = (key: string) => settings.find((s) => s.key === key);

  const leadQualSettings = [getSetting("AUTO_QUALIFICATION_ENABLED"), getSetting("LEAD_SCORE_THRESHOLD")].filter(Boolean) as PlatformSetting[];
  const leadMgmtSettings = [getSetting("DEFAULT_LEAD_PRIORITY")].filter(Boolean) as PlatformSetting[];
  const pipelineSettings = [getSetting("PIPELINE_SETTINGS")].filter(Boolean) as PlatformSetting[];

  // Any other CRM settings not mapped above
  const mappedKeys = new Set([
    "AUTO_QUALIFICATION_ENABLED", 
    "LEAD_SCORE_THRESHOLD", 
    "DEFAULT_LEAD_PRIORITY", 
    "PIPELINE_SETTINGS"
  ]);
  const otherSettings = settings.filter((s) => !mappedKeys.has(s.key));

  return (
    <SettingsPanel 
      title="CRM Settings" 
      description="Manage lead qualification, pipeline rules, and overall CRM behavior."
    >
      <SettingsSection 
        title="Lead Qualification" 
        description="Settings for AI-driven lead scoring and qualification."
        settings={leadQualSettings} 
      />
      <SettingsSection 
        title="Lead Management" 
        description="Default behaviors for newly acquired leads."
        settings={leadMgmtSettings} 
      />
      <SettingsSection 
        title="Pipeline Configuration" 
        description="Advanced JSON configuration for pipeline automations."
        settings={pipelineSettings} 
      />
      <SettingsSection 
        title="Other CRM Settings" 
        settings={otherSettings} 
      />
    </SettingsPanel>
  );
}
