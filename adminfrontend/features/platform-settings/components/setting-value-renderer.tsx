"use client";

import { PlatformSetting } from "../types";
import { Switch } from "@/components/ui/switch";

interface SettingValueRendererProps {
  setting: PlatformSetting;
}

function formatStringValue(val: string): string {
  if (!val) return val;
  // If it's a choice like "MEDIUM", "HIGH", "AUTO_ASSIGN" -> "Medium", "High", "Auto Assign"
  if (/^[A-Z0-9_]+$/.test(val)) {
    return val
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
      .join(' ');
  }
  return val;
}

export function SettingValueRenderer({ setting }: SettingValueRendererProps) {
  if (setting.is_sensitive) {
    return (
      <div className="flex items-center gap-2">
        <span className="font-mono">********</span>
      </div>
    );
  }

  if (setting.value === null || setting.value === undefined || setting.value === "") {
    return <span className="text-muted-foreground italic text-sm">Not configured</span>;
  }

  switch (setting.value_type) {
    case 'BOOLEAN':
      const isTrue = setting.value.toLowerCase() === 'true';
      return (
        <div className="flex items-center space-x-2">
          <span className="text-sm font-medium">{isTrue ? "ON" : "OFF"}</span>
          <Switch checked={isTrue} disabled />
        </div>
      );
      
    case 'INTEGER':
    case 'FLOAT':
      return (
        <span className="text-sm font-medium">
          {setting.value}
        </span>
      );
      
    case 'JSON':
      let parsedJson = setting.value;
      let isValidJson = true;
      try {
        parsedJson = JSON.parse(setting.value);
      } catch {
        isValidJson = false;
      }
      
      if (!isValidJson) {
        return <span className="text-destructive font-mono text-sm">{setting.value} (Invalid JSON)</span>;
      }
      
      if (typeof parsedJson === "object" && parsedJson !== null) {
        // Render as a clean list
        const entries = Object.entries(parsedJson);
        if (entries.length === 0) return <span className="text-muted-foreground text-sm italic">Empty Configuration</span>;
        
        return (
          <div className="space-y-1">
            {entries.slice(0, 3).map(([k, v]) => (
              <div key={k} className="text-sm">
                <span className="text-muted-foreground capitalize">{k.replace(/_/g, ' ')}</span>
                <span className="text-muted-foreground mx-1">:</span>
                <span className="font-medium">{String(v)}</span>
              </div>
            ))}
            {entries.length > 3 && (
              <div className="text-xs text-muted-foreground italic">
                + {entries.length - 3} more
              </div>
            )}
          </div>
        );
      }
      
      return (
        <span className="text-sm font-medium">{String(parsedJson)}</span>
      );
      
    default:
      return <span className="text-sm font-medium">{formatStringValue(setting.value)}</span>;
  }
}
