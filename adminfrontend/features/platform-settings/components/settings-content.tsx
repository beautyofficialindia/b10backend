"use client";

import { useSearchParams } from "next/navigation";
import { useSettings } from "../hooks";
import { SettingsSettingRow } from "./settings-setting-row";
import { SettingsEmptyState } from "./settings-empty-state";
import { Skeleton } from "@/components/ui/skeleton";
import { ErrorState } from "@/components/common/error-state";
import { Search } from "lucide-react";
import { SettingsManagement } from "./settings-management";
import { PermissionGuard } from "@/features/auth/components/permission-guard";
import {
  CRMPanel,
  AIPanel,
  AnalyticsPanel,
  FeaturesPanel,
  MaintenancePanel,
  GeneralPanel,
} from "./panels";

export function SettingsContent() {
  const searchParams = useSearchParams();
  const currentGroup = searchParams.get("group");
  const currentSearch = searchParams.get("search");

  // Default to GENERAL if nothing is selected
  const activeGroup = currentGroup || (currentSearch ? null : "GENERAL");
  const isSystemManagement = currentGroup === "SYSTEM_MANAGEMENT";
  


  const { 
    data: settingsData, 
    isLoading: isLoadingSettings, 
    isError: isErrorSettings 
  } = useSettings({
    ...(activeGroup && !isSystemManagement ? { group: activeGroup } : {}),
    ...(currentSearch ? { search: currentSearch } : {})
  }, !isSystemManagement);

  // Mode System Management
  if (currentGroup === "SYSTEM_MANAGEMENT") {
    return (
      <PermissionGuard permissions={["platform_settings.can_initialize_settings"]}>
        <SettingsManagement />
      </PermissionGuard>
    );
  }


    if (isLoadingSettings) {
      return (
        <div className="space-y-4">
          {[...Array(5)].map((_, i) => (
            <Skeleton key={i} className="h-40 w-full rounded-xl" />
          ))}
        </div>
      );
    }

    if (isErrorSettings || !settingsData) {
      return <ErrorState title="Failed to load settings" />;
    }

    if (settingsData.data.length === 0) {
      if (currentSearch) {
        return (
          <SettingsEmptyState 
            icon={Search}
            title="No settings found" 
            description={`No settings matched your search "${currentSearch}"${currentGroup ? ` in ${currentGroup}` : ""}.`} 
          />
        );
      }
      return <SettingsEmptyState title="No settings available in this category" />;
    }

    const groupDisplayName = currentGroup 
      ? currentGroup.charAt(0).toUpperCase() + currentGroup.slice(1).toLowerCase()
      : "Search Results";

    // If searching, just show the generic list, or if the group doesn't have a custom panel
    if (currentSearch) {
      return (
        <div className="space-y-6">
          <div>
            <h2 className="text-xl font-semibold tracking-tight">{groupDisplayName} Settings</h2>
            <p className="text-sm text-muted-foreground">
              {settingsData.meta.pagination.total_count} {settingsData.meta.pagination.total_count === 1 ? 'Setting' : 'Settings'} Available
            </p>
          </div>
          
          
          <div className="border rounded-md divide-y bg-card px-4">
            {settingsData.data.map((setting) => (
              <SettingsSettingRow key={setting.id} setting={setting} />
            ))}
          </div>
        </div>
      );
    }

    // Render custom panels for specific groups
    switch (currentGroup) {
      case "CRM":
        return <CRMPanel settings={settingsData.data} />;
      case "AI":
        return <AIPanel settings={settingsData.data} />;
      case "ANALYTICS":
        return <AnalyticsPanel settings={settingsData.data} />;
      case "FEATURES":
        return <FeaturesPanel settings={settingsData.data} />;
      case "MAINTENANCE":
        return <MaintenancePanel settings={settingsData.data} />;
      case "GENERAL":
        return <GeneralPanel settings={settingsData.data} />;
      default:
        // Fallback for unknown groups
        return (
          <div className="space-y-6">
            <div>
              <h2 className="text-xl font-semibold tracking-tight">{groupDisplayName} Settings</h2>
              <p className="text-sm text-muted-foreground">
                {settingsData.meta.pagination.total_count} {settingsData.meta.pagination.total_count === 1 ? 'Setting' : 'Settings'} Available
              </p>
            </div>
            
            <div className="border rounded-md divide-y bg-card px-4">
              {settingsData.data.map((setting) => (
                <SettingsSettingRow key={setting.id} setting={setting} />
              ))}
            </div>
          </div>
        );
    }

  return null;
}
