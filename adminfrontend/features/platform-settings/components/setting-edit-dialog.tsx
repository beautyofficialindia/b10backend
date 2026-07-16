"use client";

import { useState } from "react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { PlatformSetting } from "../types";
import { useUpdateSetting } from "../hooks";
import { SettingTextInput } from "./setting-text-input";
import { SettingNumberInput } from "./setting-number-input";
import { SettingBooleanSwitch } from "./setting-boolean-switch";
import { SettingJsonEditor } from "./setting-json-editor";
import { SettingSelectInput } from "./setting-select-input";

interface SettingEditDialogProps {
  setting: PlatformSetting | null;
  isOpen: boolean;
  onClose: () => void;
}

export function SettingEditDialog({ setting, isOpen, onClose }: SettingEditDialogProps) {
  const initialValue = setting?.value !== null ? String(setting?.value) : "";
  const [value, setValue] = useState(initialValue);
  const [isValid, setIsValid] = useState(true);
  const [prevSettingId, setPrevSettingId] = useState(setting?.id);
  const updateMutation = useUpdateSetting();

  if (setting?.id !== prevSettingId) {
    setPrevSettingId(setting?.id);
    setValue(initialValue);
    setIsValid(true);
  }

  if (!setting) return null;

  const handleSave = () => {
    if (!isValid) return;

    updateMutation.mutate(
      { id: setting.id, payload: { value } },
      {
        onSuccess: () => {
          onClose();
        },
      }
    );
  };

  const renderInput = () => {
    switch (setting.value_type) {
      case "BOOLEAN":
        return <SettingBooleanSwitch value={value} onChange={setValue} />;
      case "INTEGER":
      case "FLOAT":
        return <SettingNumberInput setting={setting} value={value} onChange={setValue} />;
      case "JSON":
        return <SettingJsonEditor value={value} onChange={setValue} setIsValid={setIsValid} />;
      default:
        // STRING, EMAIL, URL
        if (setting.validation_rules?.choices) {
          return <SettingSelectInput setting={setting} value={value} onChange={setValue} />;
        }
        return <SettingTextInput setting={setting} value={value} onChange={setValue} />;
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={(open) => !open && onClose()}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>Edit Setting</DialogTitle>
          <DialogDescription className="font-mono text-xs mt-1">
            {setting.key}
          </DialogDescription>
        </DialogHeader>

        <div className="py-4 space-y-4">
          <div>
            <h4 className="text-sm font-medium mb-1">{setting.display_name}</h4>
            <p className="text-sm text-muted-foreground mb-4">{setting.description}</p>
            {renderInput()}
          </div>
          
          {setting.validation_rules && (
            <div className="text-xs text-muted-foreground bg-muted p-2 rounded">
              <span className="font-semibold">Validation Rules:</span>
              <pre className="mt-1">{JSON.stringify(setting.validation_rules, null, 2)}</pre>
            </div>
          )}
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={onClose} disabled={updateMutation.isPending}>
            Cancel
          </Button>
          <Button 
            onClick={handleSave} 
            disabled={!isValid || updateMutation.isPending || value === setting.value}
          >
            {updateMutation.isPending ? "Saving..." : "Save Changes"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
