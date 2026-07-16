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
  
  const currentGroup = searchParams.get("group");

  const handleGroupSelect = (groupName: string | null) => {
    if (!groupName) return;
    const params = new URLSearchParams(searchParams);
    if (groupName === "ALL") {
      params.delete("group");
    } else {
      params.set("group", groupName);
    }
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
    <div className="w-full md:w-64 shrink-0 flex flex-col gap-4">
      {/* Mobile Select */}
      <div className="md:hidden">
        <Select 
          value={currentGroup || "ALL"} 
          onValueChange={handleGroupSelect}
        >
          <SelectTrigger className="w-full">
            <SelectValue placeholder="Select a category" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="ALL">All Categories</SelectItem>
            {groups.map((group) => (
              <SelectItem key={group.name} value={group.name}>
                {group.display_name} ({group.count})
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
      <div className="hidden md:flex flex-col gap-1">
        <button
          onClick={() => handleGroupSelect("ALL")}
          className={cn(
            "w-full text-left px-4 py-2.5 rounded-md text-sm font-medium transition-all duration-200 flex justify-between items-center group",
            !currentGroup
              ? "bg-primary/10 text-primary"
              : "text-muted-foreground hover:bg-muted hover:text-foreground"
          )}
        >
          <span>All Categories</span>
        </button>
        {groups.map((group) => (
          <button
            key={group.name}
            onClick={() => handleGroupSelect(group.name)}
            className={cn(
              "w-full text-left px-4 py-2.5 rounded-md text-sm font-medium transition-all duration-200 flex flex-col group",
              currentGroup === group.name
                ? "bg-primary/10 text-primary border-l-2 border-primary"
                : "text-muted-foreground hover:bg-muted hover:text-foreground border-l-2 border-transparent"
            )}
          >
            <div className="flex justify-between items-center w-full">
              <span>{group.display_name}</span>
              <span className="text-xs opacity-60">({group.count})</span>
            </div>
            <span className="text-[10px] opacity-50 font-normal">
              editable {group.editable_count}/{group.count}
            </span>
          </button>
        ))}
        {canManageSystem && (
          <>
            <div className="h-px bg-border my-2 w-full mx-4" style={{ width: 'calc(100% - 2rem)' }} />
            <button
              onClick={() => handleGroupSelect("SYSTEM_MANAGEMENT")}
              className={cn(
                "w-full text-left px-4 py-2.5 rounded-md text-sm font-medium transition-all duration-200 flex flex-col group mt-2",
                currentGroup === "SYSTEM_MANAGEMENT"
                  ? "bg-destructive/10 text-destructive border-l-2 border-destructive"
                  : "text-muted-foreground hover:bg-muted hover:text-foreground border-l-2 border-transparent"
              )}
            >
              <div className="flex justify-between items-center w-full">
                <span>System Management</span>
              </div>
            </button>
          </>
        )}
      </div>
    </div>
  );
}
