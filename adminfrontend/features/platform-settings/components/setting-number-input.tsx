"use client";

import { Input } from "@/components/ui/input";
import { PlatformSetting } from "../types";

interface SettingNumberInputProps {
  setting: PlatformSetting;
  value: string;
  onChange: (value: string) => void;
}

export function SettingNumberInput({ setting, value, onChange }: SettingNumberInputProps) {
  const step = setting.value_type === "FLOAT" ? "0.01" : "1";
  
  // Extract min/max from validation rules if available
  const min = setting.validation_rules?.min as number | string | undefined;
  const max = setting.validation_rules?.max as number | string | undefined;

  return (
    <Input
      type="number"
      step={step}
      min={min}
      max={max}
      value={value}
      onChange={(e) => onChange(e.target.value)}
      placeholder={`Enter ${setting.display_name.toLowerCase()}...`}
      className="font-mono text-sm"
    />
  );
}
