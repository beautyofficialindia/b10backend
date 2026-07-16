"use client";

import { PlatformSetting } from "../types";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

interface SettingSelectInputProps {
  setting: PlatformSetting;
  value: string;
  onChange: (value: string) => void;
}

export function SettingSelectInput({ setting, value, onChange }: SettingSelectInputProps) {
  // Extract choices from validation rules
  const choices = (setting.validation_rules?.choices as string[]) || [];

  return (
    <Select value={value} onValueChange={(val) => val && onChange(val)}>
      <SelectTrigger className="w-full">
        <SelectValue placeholder={`Select ${setting.display_name.toLowerCase()}...`} />
      </SelectTrigger>
      <SelectContent>
        {choices.map((choice) => (
          <SelectItem key={choice} value={choice}>
            {choice}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
}
