"use client";

import { PlatformSettingsGroup } from "../types";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Settings2, Edit3 } from "lucide-react";
import { usePathname, useRouter, useSearchParams } from "next/navigation";

interface SettingsGroupCardProps {
  group: PlatformSettingsGroup;
}

export function SettingsGroupCard({ group }: SettingsGroupCardProps) {
  const router = useRouter();
  const searchParams = useSearchParams();
  const pathname = usePathname();

  const handleSelect = () => {
    const params = new URLSearchParams(searchParams);
    params.set("group", group.name);
    params.delete("page");
    router.push(`${pathname}?${params.toString()}`);
  };

  return (
    <Card 
      className="hover:border-primary/50 transition-colors cursor-pointer"
      onClick={handleSelect}
    >
      <CardHeader className="pb-2">
        <CardTitle className="text-lg font-semibold flex items-center gap-2">
          {group.display_name}
        </CardTitle>
      </CardHeader>
      <CardContent className="text-sm text-muted-foreground flex flex-col gap-1">
        <div className="flex items-center gap-2">
          <Settings2 className="h-4 w-4" />
          <span>{group.count} Settings Available</span>
        </div>
        <div className="flex items-center gap-2">
          <Edit3 className="h-4 w-4" />
          <span>{group.editable_count} Editable</span>
        </div>
      </CardContent>
    </Card>
  );
}
