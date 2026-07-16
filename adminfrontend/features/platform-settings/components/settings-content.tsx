"use client";

import { useSearchParams } from "next/navigation";
import { useSettings, useSettingsGroups } from "../hooks";
import { SettingsGroupCard } from "./settings-group-card";
import { SettingsSettingCard } from "./settings-setting-card";
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

  // Mode 1: No group, no search -> Show Groups
  const isMode1 = !currentGroup && !currentSearch && currentGroup !== "SYSTEM_MANAGEMENT";
  
  // Mode 2 & 3: Group selected OR Search active -> Show Settings
  const isMode2Or3 = (!!currentGroup || !!currentSearch) && currentGroup !== "SYSTEM_MANAGEMENT";

  const { 
    data: groupsData, 
    isLoading: isLoadingGroups, 
    isError: isErrorGroups 
  } = useSettingsGroups(true);

  const { 
    data: settingsData, 
    isLoading: isLoadingSettings, 
    isError: isErrorSettings 
  } = useSettings({
    ...(currentGroup && currentGroup !== "SYSTEM_MANAGEMENT" ? { group: currentGroup } : {}),
    ...(currentSearch ? { search: currentSearch } : {})
  }, isMode2Or3);

  // Mode System Management
  if (currentGroup === "SYSTEM_MANAGEMENT") {
    return (
      <PermissionGuard permissions={["platform_settings.can_initialize_settings"]}>
        <SettingsManagement />
      </PermissionGuard>
    );
  }

  if (isMode1) {
    if (isLoadingGroups) {
      return (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[...Array(6)].map((_, i) => (
            <Skeleton key={i} className="h-28 w-full rounded-xl" />
          ))}
        </div>
      );
    }

    if (isErrorGroups || !groupsData) {
      return <ErrorState title="Failed to load settings categories" />;
    }

    if (groupsData.length === 0) {
      return <SettingsEmptyState title="No categories available" />;
    }

    return (
      <div className="space-y-6">
        <div>
          <h2 className="text-xl font-semibold tracking-tight">Platform Settings</h2>
          <p className="text-sm text-muted-foreground">Select a category to begin managing platform configuration.</p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {groupsData.map((group) => (
            <SettingsGroupCard key={group.name} group={group} />
          ))}
        </div>
      </div>
    );
  }

  if (isMode2Or3) {
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
      ? groupsData?.find(g => g.name === currentGroup)?.display_name || currentGroup
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
          
          <div className="grid grid-cols-1 gap-4">
            {settingsData.data.map((setting) => (
              <SettingsSettingCard key={setting.id} setting={setting} />
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
            
            <div className="grid grid-cols-1 gap-4">
              {settingsData.data.map((setting) => (
                <SettingsSettingCard key={setting.id} setting={setting} />
              ))}
            </div>
          </div>
        );
    }
  }

  return null;
}
