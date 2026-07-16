"use client";

import { Switch } from "@/components/ui/switch";


interface SettingBooleanSwitchProps {
  value: string;
  onChange: (value: string) => void;
}

export function SettingBooleanSwitch({ value, onChange }: SettingBooleanSwitchProps) {
  const isTrue = value.toLowerCase() === "true";

  return (
    <div className="flex items-center space-x-2">
      <Switch
        checked={isTrue}
        onCheckedChange={(checked) => onChange(checked ? "true" : "false")}
        id="boolean-switch"
      />
      <label htmlFor="boolean-switch" className="font-mono text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
        {isTrue ? "True" : "False"}
      </label>
    </div>
  );
}
