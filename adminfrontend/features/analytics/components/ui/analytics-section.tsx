import React from "react";
import { Separator } from "@/components/ui/separator";

interface AnalyticsSectionProps {
  title: string;
  description?: string;
  enabled?: boolean;
  children: React.ReactNode;
}

export function AnalyticsSection({ title, description, enabled = true, children }: AnalyticsSectionProps) {
  return (
    <div className="space-y-4 py-4">
      <div className="flex flex-col space-y-1">
        <h2 className="text-xl font-semibold tracking-tight">{title}</h2>
        {description && <p className="text-sm text-muted-foreground">{description}</p>}
      </div>
      <Separator />
      
      {!enabled ? (
        <div className="p-8 text-center text-sm text-muted-foreground border rounded-lg bg-muted/20">
          {title} Data Disabled
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {children}
        </div>
      )}
    </div>
  );
}
