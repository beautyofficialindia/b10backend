'use client';

import { use, useState } from 'react';
import { useRouter } from 'next/navigation';
import { PageContainer } from '@/components/layout';
import { StatusBadge, RoleBadge, ErrorState, CopyButton, AuditTimeline } from '@/components/common';
import { Skeleton } from '@/components/ui/skeleton';
import { Button } from '@/components/ui/button';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs';
import { ArrowLeft, Edit, Shield, Mail, Key, UserCheck, UserX } from 'lucide-react';
import { useUserDetail, useActivateUser, useDeactivateUser, useUserAuditLog, ResetPasswordDialog } from '@/features/users';

export default function UserDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const userId = Number(id);
  const router = useRouter();
  const { data, isLoading, isError, refetch } = useUserDetail(userId);
  const activateMutation = useActivateUser();
  const deactivateMutation = useDeactivateUser();
  const auditLog = useUserAuditLog(userId);

  const [resetOpen, setResetOpen] = useState(false);

  const user = data?.data;

  if (isLoading) return <PageContainer><Skeleton className="h-6 w-32 mb-4" /><Skeleton className="h-48 w-full" /></PageContainer>;
  if (isError || !user) return <PageContainer><ErrorState title="User not found" onRetry={() => refetch()} /></PageContainer>;

  const initials = `${user.first_name?.[0] || user.username[0]}${user.last_name?.[0] || ''}`.toUpperCase();

  return (
    <PageContainer>
      <Button variant="ghost" size="sm" className="gap-1.5 -ml-2 mb-2" onClick={() => router.push('/users')}>
        <ArrowLeft className="h-3.5 w-3.5" />Back to Users
      </Button>

      {/* Header */}
      <div className="rounded-xl border bg-card p-5 shadow-sm">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
          <div className="flex items-start gap-4">
            <Avatar className="h-14 w-14">
              <AvatarFallback className="text-lg">{initials}</AvatarFallback>
            </Avatar>
            <div>
              <div className="flex items-center gap-2 flex-wrap">
                <h1 className="text-xl font-semibold">{user.first_name && user.last_name ? `${user.first_name} ${user.last_name}` : user.username}</h1>
                <StatusBadge status={user.is_active ? 'active' : 'inactive'} label={user.is_active ? 'Active' : 'Inactive'} />
                {user.is_superuser && <Shield className="h-4 w-4 text-amber-500" />}
              </div>
              <div className="flex items-center gap-3 mt-1 text-sm text-muted-foreground">
                <span>@{user.username}</span>
                <span className="flex items-center gap-1"><Mail className="h-3.5 w-3.5" />{user.email}<CopyButton value={user.email} /></span>
              </div>
              <div className="flex gap-1 mt-2">{user.groups.map(g => <RoleBadge key={g} role={g} />)}</div>
            </div>
          </div>

          <div className="flex gap-2 shrink-0 flex-wrap">
            <Button variant="outline" size="sm" className="gap-1.5" onClick={() => router.push(`/users/${id}/edit`)}>
              <Edit className="h-3.5 w-3.5" />Edit
            </Button>
            {user.is_active ? (
              <Button variant="outline" size="sm" className="gap-1.5" disabled={deactivateMutation.isPending} onClick={() => deactivateMutation.mutate(userId)}>
                <UserX className="h-3.5 w-3.5" />Deactivate
              </Button>
            ) : (
              <Button size="sm" className="gap-1.5" disabled={activateMutation.isPending} onClick={() => activateMutation.mutate(userId)}>
                <UserCheck className="h-3.5 w-3.5" />Activate
              </Button>
            )}
            <Button variant="outline" size="sm" className="gap-1.5" onClick={() => setResetOpen(true)}>
              <Key className="h-3.5 w-3.5" />Reset Password
            </Button>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <Tabs defaultValue="overview">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="permissions">Permissions</TabsTrigger>
          <TabsTrigger value="audit">Audit Log</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="mt-4">
          <div className="grid gap-4 sm:grid-cols-2">
            <div className="rounded-lg border p-4 space-y-2.5 text-sm">
              <h3 className="font-medium">Account</h3>
              <div className="flex justify-between"><span className="text-muted-foreground">Username</span><span className="font-medium">{user.username}</span></div>
              <div className="flex justify-between"><span className="text-muted-foreground">Email</span><span className="font-medium">{user.email}</span></div>
              <div className="flex justify-between"><span className="text-muted-foreground">Staff</span><span className="font-medium">{user.is_staff ? 'Yes' : 'No'}</span></div>
              <div className="flex justify-between"><span className="text-muted-foreground">Superuser</span><span className="font-medium">{user.is_superuser ? 'Yes' : 'No'}</span></div>
            </div>
            <div className="rounded-lg border p-4 space-y-2.5 text-sm">
              <h3 className="font-medium">Dates</h3>
              <div className="flex justify-between"><span className="text-muted-foreground">Joined</span><span className="font-medium">{new Date(user.date_joined).toLocaleDateString()}</span></div>
              <div className="flex justify-between"><span className="text-muted-foreground">Last Login</span><span className="font-medium">{user.last_login ? new Date(user.last_login).toLocaleString() : 'Never'}</span></div>
            </div>
          </div>
        </TabsContent>

        <TabsContent value="permissions" className="mt-4">
          <div className="rounded-lg border p-4">
            <h3 className="text-sm font-medium mb-3">Effective Permissions ({user.permissions.length})</h3>
            {user.permissions.length === 0 ? (
              <p className="text-sm text-muted-foreground">No permissions assigned.</p>
            ) : (
              <div className="flex flex-wrap gap-1.5">
                {user.permissions.map(p => (
                  <span key={p} className="text-xs bg-muted px-2 py-0.5 rounded font-mono">{p}</span>
                ))}
              </div>
            )}
          </div>
        </TabsContent>

        <TabsContent value="audit" className="mt-4">
          <AuditTimeline entries={auditLog.data?.data || []} isLoading={auditLog.isLoading} />
        </TabsContent>
      </Tabs>

      {/* Reset Password Dialog */}
      <ResetPasswordDialog
        open={resetOpen}
        onOpenChange={setResetOpen}
        userId={userId}
      />
    </PageContainer>
  );
}
