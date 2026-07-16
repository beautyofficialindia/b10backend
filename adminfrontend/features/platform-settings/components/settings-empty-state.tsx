

import { EmptyState } from "@/components/common/empty-state";
import { Settings2, LucideIcon } from "lucide-react";

interface SettingsEmptyStateProps {
  title?: string;
  description?: string;
  icon?: LucideIcon;
}

export function SettingsEmptyState({ 
  title = "No settings found", 
  description = "There are no settings matching your current filters or search.",
  icon = Settings2 
}: SettingsEmptyStateProps) {
  return (
    <EmptyState
      icon={icon}
      title={title}
      description={description}
    />
  );
}
