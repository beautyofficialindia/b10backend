'use client';

import { use, useState, useMemo } from 'react';
import { useRouter } from 'next/navigation';
import { PageContainer, PageHeader, PageBreadcrumbs } from '@/components/layout';
import { ErrorState } from '@/components/common';
import { AuditTimeline } from '@/components/common';
import { Skeleton } from '@/components/ui/skeleton';
import { Button } from '@/components/ui/button';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs';
import { Edit, Save, Loader2, Users, Key, UserPlus, X } from 'lucide-react';
import { useRoleDetail, useAvailablePermissions, useSetPermissions, useRoleUsers, useRemoveUsers, RoleUserAssignmentDialog, PermissionTree, useRoleAuditLog } from '@/features/roles';
import { PermissionGuard, useHasPermission } from '@/features/auth';

export default function RoleDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const roleId = Number(id);
  const router = useRouter();
  const [assignDialogOpen, setAssignDialogOpen] = useState(false);
  const removeMutation = useRemoveUsers();
  
  const { data, isLoading, isError, refetch } = useRoleDetail(roleId);
  const availablePerms = useAvailablePermissions();
  const roleUsers = useRoleUsers(roleId);
  const setPermsMutation = useSetPermissions();
  const auditLog = useRoleAuditLog(roleId);

  const hasChangeGroup = useHasPermission(['auth.change_group']);

  const role = data?.data;

  // Group permissions by app
  const currentPermCodes = useMemo(() => new Set(role?.permissions.map(p => `${p.content_type.split('.')[0]}.${p.codename}`) || []), [role]);
  const [selectedPerms, setSelectedPerms] = useState<Set<string> | null>(null);

  const activePerms = selectedPerms ?? currentPermCodes;
  const isDirty = selectedPerms !== null && (
    selectedPerms.size !== currentPermCodes.size ||
    [...selectedPerms].some(p => !currentPermCodes.has(p))
  );

  const togglePerm = (code: string) => {
    const next = new Set(activePerms);
    if (next.has(code)) next.delete(code);
    else next.add(code);
    setSelectedPerms(next);
  };

  const savePermissions = () => {
    if (selectedPerms) {
      setPermsMutation.mutate(
        { id: roleId, permissions: [...selectedPerms] },
        { onSuccess: () => setSelectedPerms(null) }
      );
    }
  };

  if (isLoading) return <PermissionGuard permissions={['auth.view_group']}><PageContainer><Skeleton className="h-6 w-32 mb-4" /><Skeleton className="h-48 w-full" /></PageContainer></PermissionGuard>;
  if (isError || !role) return <PermissionGuard permissions={['auth.view_group']}><PageContainer><ErrorState title="Role not found" onRetry={() => refetch()} /></PageContainer></PermissionGuard>;

  return (
    <PermissionGuard permissions={['auth.view_group']}>
      <PageContainer>
      <PageHeader 
        title={role.name}
        description={`${role.users_count} user${role.users_count !== 1 ? 's' : ''} · ${role.permissions.length} permission${role.permissions.length !== 1 ? 's' : ''}`}
        breadcrumbs={<PageBreadcrumbs items={[{ label: 'Roles', href: '/roles' }, { label: role.name }]} />}
        className="mb-6"
      >
        {hasChangeGroup && (
          <Button variant="outline" size="sm" className="gap-1.5" onClick={() => router.push(`/roles/${id}/edit`)}>
            <Edit className="h-3.5 w-3.5" />Edit Name
          </Button>
        )}
      </PageHeader>

      <Tabs defaultValue="permissions">
        <TabsList>
          <TabsTrigger value="permissions"><Key className="h-3.5 w-3.5 mr-1.5" />Permissions</TabsTrigger>
          <TabsTrigger value="users"><Users className="h-3.5 w-3.5 mr-1.5" />Users</TabsTrigger>
          <TabsTrigger value="audit">Audit Log</TabsTrigger>
        </TabsList>

        <TabsContent value="permissions" className="mt-4 space-y-4">
          {isDirty && hasChangeGroup && (
            <div className="flex items-center gap-2 p-3 rounded-lg bg-muted">
              <span className="text-sm">Unsaved changes</span>
              <Button size="sm" onClick={savePermissions} disabled={setPermsMutation.isPending} className="gap-1.5">
                {setPermsMutation.isPending ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <Save className="h-3.5 w-3.5" />}
                Save
              </Button>
              <Button size="sm" variant="ghost" onClick={() => setSelectedPerms(null)}>Discard</Button>
            </div>
          )}

          {availablePerms.isLoading ? (
            <Skeleton className="h-48 w-full" />
          ) : (
            <PermissionTree 
              permissions={availablePerms.data?.data || []} 
              activePerms={activePerms} 
              onTogglePerm={togglePerm} 
              disabled={!hasChangeGroup} 
            />
          )}
        </TabsContent>

        <TabsContent value="users" className="mt-4">
          {hasChangeGroup && (
            <div className="flex justify-end mb-4">
              <Button size="sm" className="gap-1.5" onClick={() => setAssignDialogOpen(true)}>
                <UserPlus className="h-3.5 w-3.5" />Add Users
              </Button>
            </div>
          )}
          {roleUsers.isLoading ? (
            <Skeleton className="h-32 w-full" />
          ) : roleUsers.data?.data && roleUsers.data.data.length > 0 ? (
            <div className="rounded-lg border divide-y">
              {roleUsers.data.data.map(u => (
                <div key={u.id} className="flex items-center justify-between p-3">
                  <div>
                    <p className="text-sm font-medium">{u.first_name && u.last_name ? `${u.first_name} ${u.last_name}` : u.username}</p>
                    <p className="text-xs text-muted-foreground">{u.email}</p>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className={`text-xs px-2 py-0.5 rounded ${u.is_active ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400' : 'bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400'}`}>
                      {u.is_active ? 'Active' : 'Inactive'}
                    </span>
                    {hasChangeGroup && (
                      <Button 
                        variant="ghost" 
                        size="icon" 
                        className="h-7 w-7 text-muted-foreground hover:text-destructive"
                        onClick={() => removeMutation.mutate({ id: roleId, user_ids: [u.id] })}
                        disabled={removeMutation.isPending}
                      >
                        <X className="h-4 w-4" />
                      </Button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="rounded-lg border p-8 text-center text-sm text-muted-foreground">No users assigned to this role</div>
          )}
        </TabsContent>

        <TabsContent value="audit" className="mt-4">
          <AuditTimeline entries={auditLog.data?.data || []} isLoading={auditLog.isLoading} />
        </TabsContent>
      </Tabs>

      <RoleUserAssignmentDialog
        roleId={roleId}
        open={assignDialogOpen}
        onOpenChange={setAssignDialogOpen}
        existingUsers={roleUsers.data?.data || []}
      />
      </PageContainer>
    </PermissionGuard>
  );
}
