
"use client";

import { useSystemHealth } from "../hooks/use-dashboard";
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from "@/components/ui/card";
import { AlertTriangle, Info, XCircle, CheckCircle2, Loader2 } from "lucide-react";

export function SystemAlerts() {
  const { data: healthData, isLoading, isError } = useSystemHealth();

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>System Alerts</CardTitle>
          <CardDescription>Platform notifications and health warnings.</CardDescription>
        </CardHeader>
        <CardContent className="flex justify-center py-6">
          <Loader2 className="h-5 w-5 animate-spin text-muted-foreground" />
        </CardContent>
      </Card>
    );
  }

  // Fallback if backend failed entirely
  if (isError || !healthData) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>System Alerts</CardTitle>
          <CardDescription>Platform notifications and health warnings.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="flex items-start gap-3 p-3 rounded-md border bg-red-50 text-red-900 border-red-200">
            <XCircle className="h-5 w-5 shrink-0 mt-0.5 text-red-500" />
            <p className="text-sm font-medium leading-relaxed">Failed to load platform health metrics.</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  const hasAlerts = healthData.critical.length > 0 || healthData.warning.length > 0 || healthData.info.length > 0;

  return (
    <Card>
      <CardHeader>
        <CardTitle>System Alerts</CardTitle>
        <CardDescription>Platform notifications and health warnings.</CardDescription>
      </CardHeader>
      <CardContent className="space-y-3">
        {!hasAlerts || healthData.is_healthy && healthData.info.length === 0 ? (
          <div className="flex items-start gap-3 p-3 rounded-md border bg-green-50 text-green-900 border-green-200">
            <CheckCircle2 className="h-5 w-5 shrink-0 mt-0.5 text-green-500" />
            <p className="text-sm font-medium leading-relaxed">No issues detected. Your platform is healthy.</p>
          </div>
        ) : (
          <>
            {healthData.critical.map((alert, index) => (
              <div key={`crit-${index}`} className="flex items-start gap-3 p-3 rounded-md border bg-red-50 text-red-900 border-red-200">
                <XCircle className="h-5 w-5 shrink-0 mt-0.5 text-red-500" />
                <p className="text-sm font-medium leading-relaxed">{alert.message}</p>
              </div>
            ))}
            {healthData.warning.map((alert, index) => (
              <div key={`warn-${index}`} className="flex items-start gap-3 p-3 rounded-md border bg-orange-50 text-orange-900 border-orange-200">
                <AlertTriangle className="h-5 w-5 shrink-0 mt-0.5 text-orange-500" />
                <p className="text-sm font-medium leading-relaxed">{alert.message}</p>
              </div>
            ))}
            {healthData.info.map((alert, index) => (
              <div key={`info-${index}`} className="flex items-start gap-3 p-3 rounded-md border bg-blue-50 text-blue-900 border-blue-200">
                <Info className="h-5 w-5 shrink-0 mt-0.5 text-blue-500" />
                <p className="text-sm font-medium leading-relaxed">{alert.message}</p>
              </div>
            ))}
          </>
        )}
      </CardContent>
    </Card>
  );
}

