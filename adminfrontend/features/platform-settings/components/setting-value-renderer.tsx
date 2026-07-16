"use client";

import { PlatformSetting } from "../types";
import { Switch } from "@/components/ui/switch";

interface SettingValueRendererProps {
  setting: PlatformSetting;
}

export function SettingValueRenderer({ setting }: SettingValueRendererProps) {
  if (setting.is_sensitive) {
    return (
      <div className="flex items-center gap-2">
        <span className="font-mono">********</span>
        <span className="text-xs text-muted-foreground italic">(This value is managed securely)</span>
      </div>
    );
  }

  if (setting.value === null || setting.value === undefined || setting.value === "") {
    return <span className="text-muted-foreground italic">Empty</span>;
  }

  switch (setting.value_type) {
    case 'BOOLEAN':
      const isTrue = setting.value.toLowerCase() === 'true';
      return (
        <div className="flex items-center space-x-2">
          <Switch checked={isTrue} disabled />
          <span className="text-sm text-muted-foreground">{isTrue ? "ON" : "OFF"}</span>
        </div>
      );
      
    case 'INTEGER':
    case 'FLOAT':
      return (
        <div className="bg-secondary/50 px-3 py-1 rounded-md inline-block">
          <span className="font-mono text-sm">[ {setting.value} ]</span>
        </div>
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
        return <span className="text-destructive font-mono">{setting.value} (Invalid JSON)</span>;
      }
      
      return (
        <pre className="text-xs overflow-x-auto p-2 bg-background rounded border">
          {JSON.stringify(parsedJson, null, 2)}
        </pre>
      );
      
    default:
      return <span className="break-all">{setting.value}</span>;
  }
}
