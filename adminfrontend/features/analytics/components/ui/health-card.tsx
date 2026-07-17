import React from "react";
import { Health } from "../../types";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

interface HealthCardProps {
  health?: Health;
}

export function HealthCard({ health }: HealthCardProps) {
  if (!health) return null;

  const variantMap = {
    healthy: "default",
    warning: "destructive", 
    error: "destructive",
    disabled: "secondary",
  } as const;

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">{health.module}</CardTitle>
        <Badge variant={variantMap[health.status]}>{health.status}</Badge>
      </CardHeader>
      <CardContent>
        {health.message ? (
          <p className="text-xs text-muted-foreground mt-1">{health.message}</p>
        ) : (
          <p className="text-xs text-muted-foreground mt-1">
            {health.enabled 
              ? (health.tracking_enabled ? "Module enabled and tracking." : "Module enabled, tracking disabled.")
              : "Module disabled."}
          </p>
        )}
      </CardContent>
    </Card>
  );
}
