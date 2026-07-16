"use client";

import { Input } from "@/components/ui/input";
import { PlatformSetting } from "../types";

interface SettingTextInputProps {
  setting: PlatformSetting;
  value: string;
  onChange: (value: string) => void;
}

export function SettingTextInput({ setting, value, onChange }: SettingTextInputProps) {
  const type = setting.value_type === "EMAIL" ? "email" : 
               setting.value_type === "URL" ? "url" : "text";

  return (
    <Input
      type={type}
      value={value}
      onChange={(e) => onChange(e.target.value)}
      placeholder={`Enter ${setting.display_name.toLowerCase()}...`}
      className="font-mono text-sm"
    />
  );
}
