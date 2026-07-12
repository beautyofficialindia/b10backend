'use client';

import { use, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { PageContainer, PageHeader, PageBreadcrumbs } from '@/components/layout';
import { TextField, FormSection } from '@/components/forms';
import { ErrorState, ErrorAlert } from '@/components/common';
import { Skeleton } from '@/components/ui/skeleton';
import { Button } from '@/components/ui/button';
import { Save, Loader2 } from 'lucide-react';
import { useRoleDetail, useUpdateRole } from '@/features/roles';
import { AxiosError } from 'axios';
import { PermissionGuard } from '@/features/auth';

const schema = z.object({ name: z.string().min(1, 'Required') });
type FormData = z.infer<typeof schema>;

export default function EditRolePage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const roleId = Number(id);
  const router = useRouter();
  const { data, isLoading, isError, refetch } = useRoleDetail(roleId);
  const updateMutation = useUpdateRole();
  const { register, handleSubmit, reset, formState: { errors, isDirty } } = useForm<FormData>({ resolver: zodResolver(schema) });

  const role = data?.data;
  useEffect(() => { if (role) reset({ name: role.name }); }, [role, reset]);

  const onSubmit = (formData: FormData) => {
    updateMutation.mutate({ id: roleId, name: formData.name }, { onSuccess: () => router.push(`/roles/${id}`) });
  };

  const errorMsg = updateMutation.error instanceof AxiosError
    ? updateMutation.error.response?.data?.message || 'Failed to update'
    : null;

  if (isLoading) return <PermissionGuard permissions={['auth.change_group']}><PageContainer><Skeleton className="h-6 w-32 mb-4" /><Skeleton className="h-32 w-full" /></PageContainer></PermissionGuard>;
  if (isError || !role) return <PermissionGuard permissions={['auth.change_group']}><PageContainer><ErrorState title="Role not found" onRetry={() => refetch()} /></PageContainer></PermissionGuard>;

  return (
    <PermissionGuard permissions={['auth.change_group']}>
      <PageContainer>
        <PageHeader 
          title="Edit Role" 
          breadcrumbs={<PageBreadcrumbs items={[{ label: 'Roles', href: '/roles' }, { label: role.name, href: `/roles/${id}` }, { label: 'Edit' }]} />}
          className="mb-6"
        />
        <div className="max-w-md">
          {errorMsg && <ErrorAlert message={errorMsg} className="mb-4" />}
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            <FormSection title="Role Details">
              <TextField label="Role Name" required error={errors.name?.message} {...register('name')} />
            </FormSection>
            <div className="flex gap-3">
              <Button type="submit" disabled={updateMutation.isPending || !isDirty} className="gap-1.5">
                {updateMutation.isPending ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <Save className="h-3.5 w-3.5" />}
                Save
              </Button>
              <Button type="button" variant="outline" onClick={() => router.push(`/roles/${id}`)}>Cancel</Button>
            </div>
          </form>
        </div>
      </PageContainer>
    </PermissionGuard>
  );
}
