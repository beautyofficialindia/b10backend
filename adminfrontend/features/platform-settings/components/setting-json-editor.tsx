"use client";

import { useState } from "react";
import { Textarea } from "@/components/ui/textarea";

interface SettingJsonEditorProps {
  value: string;
  onChange: (value: string) => void;
  setIsValid?: (isValid: boolean) => void;
}

export function SettingJsonEditor({ value, onChange, setIsValid }: SettingJsonEditorProps) {
  const initialFormattedValue = (() => {
    try {
      if (!value) return "";
      const parsed = JSON.parse(value);
      return JSON.stringify(parsed, null, 2);
    } catch {
      return value;
    }
  })();

  const [localValue, setLocalValue] = useState(initialFormattedValue);
  const [error, setError] = useState<string | null>(null);

  // Sync value if parent changes it
  const [prevValue, setPrevValue] = useState(value);
  if (value !== prevValue) {
    setPrevValue(value);
    setLocalValue(initialFormattedValue);
    if (setIsValid) {
      try {
        JSON.parse(value);
        setIsValid(true);
      } catch {
        setIsValid(false);
      }
    }
  }

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const val = e.target.value;
    setLocalValue(val);
    
    try {
      if (val.trim() === "") {
        setError(null);
        onChange(val);
        if (setIsValid) setIsValid(true);
        return;
      }
      JSON.parse(val);
      setError(null);
      onChange(val); // pass raw string up, will be formatted on save or can just save raw
      if (setIsValid) setIsValid(true);
    } catch {
      setError("Invalid JSON format");
      onChange(val);
      if (setIsValid) setIsValid(false);
    }
  };

  const handleBlur = () => {
    try {
      if (localValue.trim() !== "") {
        const parsed = JSON.parse(localValue);
        const formatted = JSON.stringify(parsed, null, 2);
        setLocalValue(formatted);
        onChange(formatted);
      }
    } catch {
      // ignore, let error show
    }
  };

  return (
    <div className="space-y-2">
      <Textarea
        value={localValue}
        onChange={handleChange}
        onBlur={handleBlur}
        className={`font-mono text-xs min-h-[200px] ${error ? 'border-destructive' : ''}`}
        placeholder="Enter JSON here..."
      />
      {error && <p className="text-xs text-destructive">{error}</p>}
    </div>
  );
}
