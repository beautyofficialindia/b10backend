"use client";

import { useSettingsGroups } from "../hooks";
import { useRouter, useSearchParams, usePathname } from "next/navigation";
import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/lib/utils";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { AlertCircle } from "lucide-react";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { useHasPermission } from "@/features/auth/hooks/use-auth";

export function SettingsSidebar() {
  const { data: groups, isLoading, isError } = useSettingsGroups();
  const router = useRouter();
  const searchParams = useSearchParams();
  const pathname = usePathname();
  const canManageSystem = useHasPermission(["platform_settings.can_initialize_settings"]);
  
  // Default to GENERAL if no group is selected
  const currentGroup = searchParams.get("group") || "GENERAL";

  const handleGroupSelect = (groupName: string | null) => {
    if (!groupName) return;
    const params = new URLSearchParams(searchParams);
    params.set("group", groupName);
    // Maintain search term but reset page
    params.delete("page");
    router.push(`${pathname}?${params.toString()}`);
  };

  if (isLoading) {
    return (
      <div className="w-full md:w-64 space-y-2 shrink-0">
        <Skeleton className="h-10 w-full rounded-md" />
        <Skeleton className="h-10 w-full rounded-md" />
        <Skeleton className="h-10 w-full rounded-md" />
        <Skeleton className="h-10 w-full rounded-md" />
      </div>
    );
  }

  if (isError || !groups) {
    return (
      <Alert variant="destructive" className="w-full md:w-64 shrink-0">
        <AlertCircle className="h-4 w-4" />
        <AlertDescription>Failed to load groups.</AlertDescription>
      </Alert>
    );
  }

  return (
    <div className="w-full md:w-64 shrink-0 flex flex-col gap-8">
      {/* Mobile Select */}
      <div className="md:hidden">
        <Select 
          value={currentGroup} 
          onValueChange={handleGroupSelect}
        >
          <SelectTrigger className="w-full">
            <SelectValue placeholder="Select a category" />
          </SelectTrigger>
          <SelectContent>
            {groups.map((group) => (
              <SelectItem key={group.name} value={group.name}>
                {group.display_name}
              </SelectItem>
            ))}
            {canManageSystem && (
              <>
                <div className="h-px bg-border my-2" />
                <SelectItem value="SYSTEM_MANAGEMENT">System Management</SelectItem>
              </>
            )}
          </SelectContent>
        </Select>
      </div>

      {/* Desktop Sidebar */}
      <div className="hidden md:flex flex-col gap-6">
        <div>
          <h4 className="px-4 text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2">Platform Settings</h4>
          <div className="flex flex-col gap-1">
            {groups.map((group) => (
              <button
                key={group.name}
                onClick={() => handleGroupSelect(group.name)}
                className={cn(
                  "w-full text-left px-4 py-2 rounded-md text-sm font-medium transition-all duration-200",
                  currentGroup === group.name
                    ? "bg-primary/10 text-primary"
                    : "text-muted-foreground hover:bg-muted hover:text-foreground"
                )}
              >
                {group.display_name}
              </button>
            ))}
          </div>
        </div>

        {canManageSystem && (
          <div>
            <h4 className="px-4 text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2">Advanced</h4>
            <div className="flex flex-col gap-1">
              <button
                onClick={() => handleGroupSelect("SYSTEM_MANAGEMENT")}
                className={cn(
                  "w-full text-left px-4 py-2 rounded-md text-sm font-medium transition-all duration-200",
                  currentGroup === "SYSTEM_MANAGEMENT"
                    ? "bg-primary/10 text-primary"
                    : "text-muted-foreground hover:bg-muted hover:text-foreground"
                )}
              >
                System Management
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
