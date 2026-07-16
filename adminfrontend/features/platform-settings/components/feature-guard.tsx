"use client";

import { ReactNode } from "react";
import { useFeatureFlags } from "../providers";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { ShieldAlert, Loader2 } from "lucide-react";

interface FeatureGuardProps {
  feature: string;
  children: ReactNode;
  fallback?: ReactNode;
}

export function FeatureGuard({ feature, children, fallback }: FeatureGuardProps) {
  const { flags, isLoading } = useFeatureFlags();

  if (isLoading) {
    return (
      <div className="flex items-center justify-center p-12">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  // If the flag is strictly false, deny access
  if (flags[feature] === false) {
    if (fallback !== undefined) {
      return fallback;
    }

    return (
      <div className="p-6">
        <Card className="max-w-md mx-auto border-dashed">
          <CardHeader className="text-center pb-2">
            <ShieldAlert className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
            <CardTitle className="text-xl">Module Disabled</CardTitle>
            <CardDescription>
              This feature is currently disabled by the platform administrator.
            </CardDescription>
          </CardHeader>
          <CardContent className="text-center">
            <p className="text-sm text-muted-foreground">
              Contact your system administrator to enable {feature}.
            </p>
          </CardContent>
        </Card>
      </div>
    );
  }

  // If flag is true (or undefined/not yet fetched but not explicitly disabled), allow access
  return <>{children}</>;
}
