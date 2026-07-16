"use client";

import { SettingsSidebar } from "./settings-sidebar";
import { SettingsSearch } from "./settings-search";
import { SettingsContent } from "./settings-content";

export function SettingsLayout() {
  return (
    <div className="flex flex-col h-full gap-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Settings</h1>
          <p className="text-muted-foreground text-sm mt-1">
            Manage your platform configuration, integrations, and preferences.
          </p>
        </div>
        <SettingsSearch />
      </div>

      <div className="flex flex-col md:flex-row gap-8 flex-1 pb-10">
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
