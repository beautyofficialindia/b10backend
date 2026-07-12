'use client';

import * as React from 'react';
import { PageContainer } from '@/components/layout';
import { RoleBadge } from '@/components/common';
import { Skeleton } from '@/components/ui/skeleton';
import { Button } from '@/components/ui/button';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs';
import { Shield, Mail, Key, Edit2 } from 'lucide-react';
import { useAuth, ChangePasswordDialog, EditProfileDialog } from '@/features/auth';

export default function ProfilePage() {
  const { user, isLoading } = useAuth();
  const [resetOpen, setResetOpen] = React.useState(false);
  const [editOpen, setEditOpen] = React.useState(false);

  if (isLoading) {
    return (
      <PageContainer>
        <Skeleton className="h-6 w-32 mb-4" />
        <Skeleton className="h-48 w-full" />
      </PageContainer>
    );
  }

  if (!user) return null; // Handled by AuthGuard higher up

  const initials = `${user.first_name?.[0] || user.username[0]}${user.last_name?.[0] || ''}`.toUpperCase();

  return (
    <PageContainer>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold tracking-tight">My Profile</h1>
        <Button onClick={() => setEditOpen(true)} variant="outline" size="sm" className="gap-2">
          <Edit2 className="h-4 w-4" />
          Edit Profile
        </Button>
      </div>

      <div className="rounded-xl border bg-card p-5 shadow-sm mb-6">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-start">
          <Avatar className="h-16 w-16">
            <AvatarFallback className="text-xl">{initials}</AvatarFallback>
          </Avatar>
          <div>
            <div className="flex items-center gap-2 flex-wrap">
              <h2 className="text-xl font-semibold">
                {user.first_name && user.last_name ? `${user.first_name} ${user.last_name}` : user.username}
              </h2>
              {user.is_superuser && <span title="Superuser"><Shield className="h-4 w-4 text-amber-500" /></span>}
            </div>
            <div className="flex items-center gap-3 mt-1 text-sm text-muted-foreground">
              <span>@{user.username}</span>
              <span className="flex items-center gap-1"><Mail className="h-3.5 w-3.5" />{user.email}</span>
            </div>
            <div className="flex gap-1 mt-3 flex-wrap">
              {user.groups.length > 0 ? (
                user.groups.map(g => <RoleBadge key={g.id} role={g.name} />)
              ) : (
                <span className="text-xs text-muted-foreground">No roles assigned</span>
              )}
            </div>
          </div>
        </div>
      </div>

      <Tabs defaultValue="overview">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="security">Security</TabsTrigger>
          <TabsTrigger value="permissions">Permissions</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="mt-4">
          <div className="grid gap-4 sm:grid-cols-2">
            <div className="rounded-lg border p-4 space-y-2.5 text-sm">
              <h3 className="font-medium text-base mb-3">Account Details</h3>
              <div className="flex justify-between"><span className="text-muted-foreground">Username</span><span className="font-medium">{user.username}</span></div>
              <div className="flex justify-between"><span className="text-muted-foreground">Email</span><span className="font-medium">{user.email}</span></div>
              <div className="flex justify-between"><span className="text-muted-foreground">First Name</span><span className="font-medium">{user.first_name || '-'}</span></div>
              <div className="flex justify-between"><span className="text-muted-foreground">Last Name</span><span className="font-medium">{user.last_name || '-'}</span></div>
            </div>
            <div className="rounded-lg border p-4 space-y-2.5 text-sm">
              <h3 className="font-medium text-base mb-3">System Flags</h3>
              <div className="flex justify-between"><span className="text-muted-foreground">Staff Member</span><span className="font-medium">{user.is_staff ? 'Yes' : 'No'}</span></div>
              <div className="flex justify-between"><span className="text-muted-foreground">Superuser</span><span className="font-medium">{user.is_superuser ? 'Yes' : 'No'}</span></div>
            </div>
          </div>
        </TabsContent>

        <TabsContent value="security" className="mt-4">
          <div className="rounded-lg border p-5">
            <div className="flex flex-col sm:flex-row justify-between sm:items-center gap-4">
              <div>
                <h3 className="font-medium text-base">Change Password</h3>
                <p className="text-sm text-muted-foreground mt-1">
                  Ensure your account is using a long, random password to stay secure.
                </p>
              </div>
              <Button onClick={() => setResetOpen(true)} className="gap-2 shrink-0">
                <Key className="h-4 w-4" />
                Change Password
              </Button>
            </div>
            
            {/* Future placeholders exactly as requested */}
            <div className="mt-6 pt-6 border-t opacity-50 select-none">
              <h3 className="font-medium text-base mb-2">Two-Factor Authentication (MFA)</h3>
              <p className="text-sm text-muted-foreground">Coming soon.</p>
            </div>
            <div className="mt-6 pt-6 border-t opacity-50 select-none">
              <h3 className="font-medium text-base mb-2">Active Sessions & Login History</h3>
              <p className="text-sm text-muted-foreground">Coming soon.</p>
            </div>
          </div>
        </TabsContent>

        <TabsContent value="permissions" className="mt-4">
          <div className="rounded-lg border p-5">
            <h3 className="font-medium text-base mb-4">Effective Permissions ({user.permissions.length})</h3>
            {user.permissions.length === 0 ? (
              <p className="text-sm text-muted-foreground">You have no explicit permissions assigned.</p>
            ) : (
              <div className="flex flex-wrap gap-2">
                {user.permissions.map(p => (
                  <span key={p} className="text-xs bg-muted/50 border px-2.5 py-1 rounded-md font-mono text-muted-foreground">
                    {p}
                  </span>
                ))}
              </div>
            )}
          </div>
        </TabsContent>
      </Tabs>

      <ChangePasswordDialog open={resetOpen} onOpenChange={setResetOpen} />
      <EditProfileDialog open={editOpen} onOpenChange={setEditOpen} />
    </PageContainer>
  );
}
