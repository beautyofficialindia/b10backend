"use client";

import { useState } from "react";
import { PlatformSetting } from "../types";
import { Button } from "@/components/ui/button";
import { SettingValueRenderer } from "./setting-value-renderer";
import { SettingEditDialog } from "./setting-edit-dialog";
import { PermissionGuard } from "@/features/auth/components/permission-guard";
import { Badge } from "@/components/ui/badge";

interface SettingsSettingRowProps {
  setting: PlatformSetting;
}

export function SettingsSettingRow({ setting }: SettingsSettingRowProps) {
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);

  const canEdit = setting.is_editable && !setting.is_sensitive;

  return (
    <>
      <div className="flex flex-col sm:flex-row sm:items-center justify-between py-4 group">
        <div className="space-y-1 pr-4 max-w-[60%]">
          <div className="flex items-center gap-2">
            <h4 className="text-sm font-medium text-foreground">{setting.display_name}</h4>
            {!setting.is_editable && (
              <Badge variant="secondary" className="text-[10px] px-1.5 py-0 font-normal">Read Only</Badge>
            )}
          </div>
          <p className="text-sm text-muted-foreground leading-relaxed">
            {setting.description || "No description provided."}
          </p>
        </div>
        
        <div className="flex items-center gap-6 mt-4 sm:mt-0">
          <div className="flex-1 sm:text-right">
            <SettingValueRenderer setting={setting} />
          </div>
          
          <div className="w-[80px] flex justify-end shrink-0 opacity-0 group-hover:opacity-100 transition-opacity focus-within:opacity-100">
            {canEdit && (
              <PermissionGuard permissions={["platform_settings.change_platformsetting"]}>
                <Button variant="outline" size="sm" onClick={() => setIsEditDialogOpen(true)}>
                  Edit
                </Button>
              </PermissionGuard>
            )}
          </div>
        </div>
      </div>

      <SettingEditDialog 
        setting={setting} 
        isOpen={isEditDialogOpen} 
        onClose={() => setIsEditDialogOpen(false)} 
      />
    </>
  );
}
