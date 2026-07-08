'use client';

import { use, useState, useMemo } from 'react';
import { useRouter } from 'next/navigation';
import { PageContainer } from '@/components/layout';
import { ErrorState } from '@/components/common';
import { Skeleton } from '@/components/ui/skeleton';
import { Button } from '@/components/ui/button';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs';
import { Checkbox } from '@/components/ui/checkbox';
import { ArrowLeft, Edit, Save, Loader2, Users, Key } from 'lucide-react';
import { useRoleDetail, useAvailablePermissions, useSetPermissions, useRoleUsers, type Permission } from '@/features/roles';

export default function RoleDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const roleId = Number(id);
  const router = useRouter();
  const { data, isLoading, isError, refetch } = useRoleDetail(roleId);
  const availablePerms = useAvailablePermissions();
  const roleUsers = useRoleUsers(roleId);
  const setPermsMutation = useSetPermissions();

  const role = data?.data;

  // Group permissions by app
  const currentPermCodes = useMemo(() => new Set(role?.permissions.map(p => `${p.content_type.split('.')[0]}.${p.codename}`) || []), [role]);
  const [selectedPerms, setSelectedPerms] = useState<Set<string> | null>(null);

  const activePerms = selectedPerms ?? currentPermCodes;
  const isDirty = selectedPerms !== null && (
    selectedPerms.size !== currentPermCodes.size ||
    [...selectedPerms].some(p => !currentPermCodes.has(p))
  );

  const groupedPerms = useMemo(() => {
    if (!availablePerms.data?.data) return {};
    const groups: Record<string, Permission[]> = {};
    for (const p of availablePerms.data.data) {
      const app = p.content_type.split('.')[0];
      if (!groups[app]) groups[app] = [];
      groups[app].push(p);
    }
    return groups;
  }, [availablePerms.data]);

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

  if (isLoading) return <PageContainer><Skeleton className="h-6 w-32 mb-4" /><Skeleton className="h-48 w-full" /></PageContainer>;
  if (isError || !role) return <PageContainer><ErrorState title="Role not found" onRetry={() => refetch()} /></PageContainer>;

  return (
    <PageContainer>
      <Button variant="ghost" size="sm" className="gap-1.5 -ml-2 mb-2" onClick={() => router.push('/roles')}>
        <ArrowLeft className="h-3.5 w-3.5" />Back to Roles
      </Button>

      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-xl font-semibold">{role.name}</h1>
          <p className="text-sm text-muted-foreground mt-0.5">{role.users_count} user{role.users_count !== 1 ? 's' : ''} · {role.permissions.length} permission{role.permissions.length !== 1 ? 's' : ''}</p>
        </div>
        <Button variant="outline" size="sm" className="gap-1.5" onClick={() => router.push(`/roles/${id}/edit`)}>
          <Edit className="h-3.5 w-3.5" />Edit Name
        </Button>
      </div>

      <Tabs defaultValue="permissions">
        <TabsList>
          <TabsTrigger value="permissions"><Key className="h-3.5 w-3.5 mr-1.5" />Permissions</TabsTrigger>
          <TabsTrigger value="users"><Users className="h-3.5 w-3.5 mr-1.5" />Users</TabsTrigger>
        </TabsList>

        <TabsContent value="permissions" className="mt-4 space-y-4">
          {isDirty && (
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
            <div className="space-y-6">
              {Object.entries(groupedPerms).sort().map(([app, perms]) => (
                <div key={app} className="rounded-lg border p-4">
                  <h3 className="text-sm font-medium capitalize mb-3">{app}</h3>
                  <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-2">
                    {perms.map(p => {
                      const code = `${p.content_type.split('.')[0]}.${p.codename}`;
                      return (
                        <label key={p.id} className="flex items-center gap-2 cursor-pointer text-sm">
                          <Checkbox checked={activePerms.has(code)} onCheckedChange={() => togglePerm(code)} />
                          <span className="truncate" title={p.name}>{p.codename}</span>
                        </label>
                      );
                    })}
                  </div>
                </div>
              ))}
            </div>
          )}
        </TabsContent>

        <TabsContent value="users" className="mt-4">
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
                  <span className={`text-xs px-2 py-0.5 rounded ${u.is_active ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400' : 'bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400'}`}>
                    {u.is_active ? 'Active' : 'Inactive'}
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <div className="rounded-lg border p-8 text-center text-sm text-muted-foreground">No users assigned to this role</div>
          )}
        </TabsContent>
      </Tabs>
    </PageContainer>
  );
}
