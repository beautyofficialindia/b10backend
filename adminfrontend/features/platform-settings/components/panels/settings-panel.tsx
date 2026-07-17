"use client";

import { ReactNode } from "react";
import { PlatformSetting } from "../../types";
import { SettingsSettingRow } from "../settings-setting-row";

interface SettingsSectionProps {
  title: string;
  description?: string;
  settings: PlatformSetting[];
}

export function SettingsSection({ title, description, settings }: SettingsSectionProps) {
  if (settings.length === 0) return null;
  
  return (
    <div className="mb-10">
      <div className="mb-4">
        <h3 className="text-lg font-medium">{title}</h3>
        {description && <p className="text-sm text-muted-foreground">{description}</p>}
      </div>
      <div className="border rounded-md divide-y bg-card px-4">
        {settings.map((setting) => (
          <SettingsSettingRow key={setting.id} setting={setting} />
        ))}
      </div>
    </div>
  );
}

interface SettingsPanelProps {
  title: string;
  description: string;
  children: ReactNode;
}

export function SettingsPanel({ title, description, children }: SettingsPanelProps) {
  return (
    <div className="space-y-6">
      <div className="pb-4 border-b">
        <h2 className="text-2xl font-semibold tracking-tight">{title}</h2>
        <p className="text-sm text-muted-foreground mt-1">{description}</p>
      </div>
      <div>
        {children}
      </div>
    </div>
  );
}
