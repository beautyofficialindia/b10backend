"use client";

import { useFeatureFlags } from "@/features/platform-settings/providers";
import { useAuth } from "@/features/auth";
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from "@/components/ui/card";
import { buttonVariants } from "@/components/ui/button";
import Link from "next/link";
import { UserPlus, BookOpen, Settings, BarChart, Shield, Target } from "lucide-react";
import { cn } from "@/lib/utils";

export function QuickActions() {
  const { flags } = useFeatureFlags();
  const { user } = useAuth();

  const hasPerm = (perm: string) => {
    if (user?.is_superuser) return true;
    return user?.permissions?.includes(perm);
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Quick Actions</CardTitle>
        <CardDescription>Shortcuts to common operational tasks.</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 lg:grid-cols-3 gap-3">
          {flags["ENABLE_CRM"] && (
            <Link href="/leads" className={cn(buttonVariants({ variant: "outline" }), "h-20 flex flex-col items-center justify-center gap-2")}>
              <Target className="h-5 w-5" />
              <span>Create Lead</span>
            </Link>
          )}

          {flags["ENABLE_KNOWLEDGE_BASE"] && (
            <Link href="/knowledge/new" className={cn(buttonVariants({ variant: "outline" }), "h-20 flex flex-col items-center justify-center gap-2")}>
              <BookOpen className="h-5 w-5" />
              <span>Write Article</span>
            </Link>
          )}

          {flags["ENABLE_ANALYTICS"] && (
            <Link href="/analytics" className={cn(buttonVariants({ variant: "outline" }), "h-20 flex flex-col items-center justify-center gap-2")}>
              <BarChart className="h-5 w-5" />
              <span>View Analytics</span>
            </Link>
          )}

          {hasPerm("user_management.add_user") && (
            <Link href="/users/new" className={cn(buttonVariants({ variant: "outline" }), "h-20 flex flex-col items-center justify-center gap-2")}>
              <UserPlus className="h-5 w-5" />
              <span>Add User</span>
            </Link>
          )}

          {hasPerm("role_management.view_group") && (
            <Link href="/roles" className={cn(buttonVariants({ variant: "outline" }), "h-20 flex flex-col items-center justify-center gap-2")}>
              <Shield className="h-5 w-5" />
              <span>Manage Roles</span>
            </Link>
          )}

          {hasPerm("platform_settings.change_platformsetting") && (
            <Link href="/settings" className={cn(buttonVariants({ variant: "outline" }), "h-20 flex flex-col items-center justify-center gap-2")}>
              <Settings className="h-5 w-5" />
              <span>Settings</span>
            </Link>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
