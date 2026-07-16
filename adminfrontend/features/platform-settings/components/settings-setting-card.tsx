"use client";

import { useState } from "react";
import { PlatformSetting } from "../types";
import { Card, CardContent, CardHeader, CardTitle, CardFooter } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Edit2 } from "lucide-react";
import { SettingValueRenderer } from "./setting-value-renderer";
import { SettingEditDialog } from "./setting-edit-dialog";
import { PermissionGuard } from "@/features/auth/components/permission-guard";

interface SettingsSettingCardProps {
  setting: PlatformSetting;
}

export function SettingsSettingCard({ setting }: SettingsSettingCardProps) {
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);

  const canEdit = setting.is_editable && !setting.is_sensitive;

  return (
    <>
      <Card className="hover:border-primary/30 transition-colors flex flex-col">
        <CardHeader className="pb-2 flex flex-row justify-between items-start">
          <div className="space-y-1">
            <CardTitle className="text-base font-semibold">{setting.display_name}</CardTitle>
            <div className="text-xs text-muted-foreground font-mono bg-muted px-2 py-1 rounded inline-block">
              {setting.key}
            </div>
          </div>
          <div className="flex gap-2 items-center">
            {setting.is_public && <Badge variant="secondary">Public</Badge>}
            {setting.is_editable ? (
              <Badge variant="outline" className="border-green-500 text-green-600">Editable</Badge>
            ) : (
              <Badge variant="outline" className="opacity-50">Read Only</Badge>
            )}
          </div>
        </CardHeader>
        
        <CardContent className="flex-1">
          <p className="text-sm text-muted-foreground mb-4">
            {setting.description || "No description provided."}
          </p>
          
          <div className="bg-muted/50 p-3 rounded-md font-mono text-sm">
            <div className="text-xs text-muted-foreground mb-2 uppercase tracking-wider flex justify-between">
              <span>Current Value ({setting.value_type})</span>
            </div>
            <div className="text-foreground">
              <SettingValueRenderer setting={setting} />
            </div>
          </div>
        </CardContent>

        {canEdit && (
          <PermissionGuard permissions={["platform_settings.change_platformsetting"]}>
            <CardFooter className="pt-0 justify-end">
              <Button variant="outline" size="sm" onClick={() => setIsEditDialogOpen(true)}>
                <Edit2 className="w-4 h-4 mr-2" />
                Edit
              </Button>
            </CardFooter>
          </PermissionGuard>
        )}
      </Card>

      <SettingEditDialog 
        setting={setting} 
        isOpen={isEditDialogOpen} 
        onClose={() => setIsEditDialogOpen(false)} 
      />
    </>
  );
}
