"use client";

import { PlatformSetting } from "../../types";
import { SettingsPanel, SettingsSection } from "./settings-panel";

interface AIPanelProps {
  settings: PlatformSetting[];
}

export function AIPanel({ settings }: AIPanelProps) {
  const getSetting = (key: string) => settings.find((s) => s.key === key);

  const modelSettings = [getSetting("DEFAULT_MODEL")].filter(Boolean) as PlatformSetting[];
  const generationSettings = [getSetting("TEMPERATURE"), getSetting("MAX_TOKENS")].filter(Boolean) as PlatformSetting[];
  const knowledgeSettings = [getSetting("KNOWLEDGE_SOURCE"), getSetting("CONTEXT_LIMITS")].filter(Boolean) as PlatformSetting[];

  const mappedKeys = new Set([
    "DEFAULT_MODEL", 
    "TEMPERATURE", 
    "MAX_TOKENS", 
    "KNOWLEDGE_SOURCE",
    "CONTEXT_LIMITS"
  ]);
  const otherSettings = settings.filter((s) => !mappedKeys.has(s.key));

  return (
    <SettingsPanel 
      title="AI Configuration" 
      description="Configure core AI models, generation parameters, and knowledge boundaries."
    >
      <SettingsSection 
        title="Models" 
        settings={modelSettings} 
      />
      <SettingsSection 
        title="Generation" 
        description="Adjust how the AI generates responses."
        settings={generationSettings} 
      />
      <SettingsSection 
        title="Knowledge Source" 
        description="Configure what context the AI has access to."
        settings={knowledgeSettings} 
      />
      <SettingsSection 
        title="Other AI Settings" 
        settings={otherSettings} 
      />
    </SettingsPanel>
  );
}
