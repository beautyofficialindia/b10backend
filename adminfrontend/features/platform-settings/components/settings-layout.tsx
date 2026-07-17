"use client";

import { SettingsSidebar } from "./settings-sidebar";
import { SettingsSearch } from "./settings-search";
import { SettingsContent } from "./settings-content";

export function SettingsLayout() {
  return (
    <div className="flex flex-col h-full gap-6">
      <div className="flex flex-col gap-1">
        <h1 className="text-3xl font-bold tracking-tight">Settings</h1>
        <p className="text-muted-foreground text-sm">
          Manage your platform configuration, integrations, and preferences.
        </p>
      </div>

      <div className="pb-4 border-b">
        <div className="max-w-md">
          <SettingsSearch />
        </div>
      </div>

      <div className="flex flex-col md:flex-row gap-8 flex-1 pb-10 mt-2">
        <SettingsSidebar />
        
        <div className="flex-1 w-full min-w-0">
          {/* Reserved space for future tabs like General, Cache, Maintenance */}
          <div className="hidden mb-6 border-b">
            {/* Future Navigation Menu / Tabs */}
          </div>
          
          <SettingsContent />
        </div>
      </div>
    </div>
  );
}
