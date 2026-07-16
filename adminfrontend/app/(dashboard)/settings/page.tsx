"use client";

import { SettingsLayout, SettingsEmptyState } from "@/features/platform-settings";
import { PermissionGuard } from "@/features/auth/components/permission-guard";
import { ShieldAlert } from "lucide-react";

export default function SettingsPage() {
  return (
    <div className="flex-1 space-y-4 p-8 pt-6 h-full">
      <PermissionGuard 
        permissions={["platform_settings.view_platformsetting"]}
        fallback={
          <div className="h-[60vh] flex items-center justify-center">
            <SettingsEmptyState 
              icon={ShieldAlert}
              title="Access Denied" 
              description="You do not have permission to view platform settings. Please contact your system administrator." 
            />
          </div>
        }
      >
        <SettingsLayout />
      </PermissionGuard>
    </div>
  );
}
