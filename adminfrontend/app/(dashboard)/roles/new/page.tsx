'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { PageContainer, PageHeader, PageBreadcrumbs } from '@/components/layout';
import { TextField, FormSection } from '@/components/forms';
import { ErrorAlert } from '@/components/common';
import { Skeleton } from '@/components/ui/skeleton';
import { Button } from '@/components/ui/button';
import { Save, Loader2 } from 'lucide-react';
import { useCreateRole, useAvailablePermissions, PermissionTree } from '@/features/roles';
import { AxiosError } from 'axios';
import { PermissionGuard } from '@/features/auth';

const schema = z.object({ name: z.string().min(1, 'Role name is required') });
type FormData = z.infer<typeof schema>;

export default function NewRolePage() {
  const router = useRouter();
  const createMutation = useCreateRole();
  const availablePerms = useAvailablePermissions();
  const [selectedPerms, setSelectedPerms] = useState<Set<string>>(new Set());

  const { register, handleSubmit, formState: { errors } } = useForm<FormData>({
    resolver: zodResolver(schema),
  });

  const togglePerm = (code: string) => {
    const next = new Set(selectedPerms);
    if (next.has(code)) next.delete(code);
    else next.add(code);
    setSelectedPerms(next);
  };

  const onSubmit = (data: FormData) => {
    const payload = { ...data, permissions: [...selectedPerms] };
    createMutation.mutate(payload, { onSuccess: (res) => router.push(`/roles/${res.data.id}`) });
  };

  const errorMsg = createMutation.error instanceof AxiosError
    ? createMutation.error.response?.data?.message || 'Failed to create role'
    : null;

  return (
    <PermissionGuard permissions={['auth.add_group']}>
      <PageContainer>
        <PageHeader 
          title="Create Role" 
          breadcrumbs={<PageBreadcrumbs items={[{ label: 'Roles', href: '/roles' }, { label: 'Create Role' }]} />}
          className="mb-6"
        />
        <div className="max-w-4xl">
          {errorMsg && <ErrorAlert message={errorMsg} className="mb-4 max-w-md" />}
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-8">
            <div className="max-w-md">
              <FormSection title="Role Details">
                <TextField label="Role Name" required placeholder="e.g. Marketing" error={errors.name?.message} {...register('name')} />
              </FormSection>
            </div>

            <FormSection title="Permissions" description="Select the permissions this role will grant to assigned users.">
              {availablePerms.isLoading ? (
                <Skeleton className="h-64 w-full mt-4" />
              ) : (
                <div className="mt-4">
                  <PermissionTree 
                    permissions={availablePerms.data?.data || []} 
                    activePerms={selectedPerms} 
                    onTogglePerm={togglePerm} 
                  />
                </div>
              )}
            </FormSection>

            <div className="flex gap-3 pt-4 border-t">
              <Button type="submit" disabled={createMutation.isPending} className="gap-1.5">
                {createMutation.isPending ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <Save className="h-3.5 w-3.5" />}
                Create Role
              </Button>
              <Button type="button" variant="outline" onClick={() => router.push('/roles')}>Cancel</Button>
            </div>
          </form>
        </div>
      </PageContainer>
    </PermissionGuard>
  );
}
