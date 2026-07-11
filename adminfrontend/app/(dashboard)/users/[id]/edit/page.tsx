'use client';

import { use } from 'react';
import { useRouter } from 'next/navigation';
import { PageContainer } from '@/components/layout';
import { Button } from '@/components/ui/button';
import { ArrowLeft } from 'lucide-react';
import { useUserDetail, useUpdateUser } from '@/features/users';
import { UserForm, type UserFormData } from '@/features/users/components';
import { ErrorState } from '@/components/common';
import { Skeleton } from '@/components/ui/skeleton';
import { PermissionGuard } from '@/features/auth';
import { AxiosError } from 'axios';

export default function EditUserPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const userId = Number(id);
  const router = useRouter();
  
  const { data, isLoading, isError, refetch } = useUserDetail(userId);
  const updateMutation = useUpdateUser();

  const user = data?.data;

  const onSubmit = (formData: UserFormData) => {
    updateMutation.mutate(
      { id: userId, data: formData },
      { onSuccess: () => router.push(`/users/${userId}`) }
    );
  };

  if (isLoading) {
    return (
      <PermissionGuard permissions={['auth.change_user']}>
        <PageContainer>
          <Skeleton className="h-6 w-32 mb-4" />
          <Skeleton className="h-96 w-full max-w-lg" />
        </PageContainer>
      </PermissionGuard>
    );
  }

  if (isError || !user) {
    return (
      <PermissionGuard permissions={['auth.change_user']}>
        <PageContainer>
          <ErrorState title="User not found" onRetry={() => refetch()} />
        </PageContainer>
      </PermissionGuard>
    );
  }

  const errorMsg = updateMutation.error instanceof AxiosError
    ? updateMutation.error.response?.data?.message || 'Failed to update user'
    : null;

  return (
    <PermissionGuard permissions={['auth.change_user']}>
      <PageContainer>
        <Button variant="ghost" size="sm" className="gap-1.5 -ml-2 mb-2" onClick={() => router.push(`/users/${userId}`)}>
          <ArrowLeft className="h-3.5 w-3.5" />Back to User Profile
        </Button>

        <div className="max-w-lg">
          <h1 className="text-xl font-semibold mb-6">Edit User</h1>
          <UserForm 
            initialData={{
              username: user.username,
              email: user.email,
              first_name: user.first_name || '',
              last_name: user.last_name || '',
              is_staff: user.is_staff,
              is_superuser: user.is_superuser,
              groups: user.groups,
            }}
            onSubmit={onSubmit}
            isSubmitting={updateMutation.isPending}
            isEditMode={true}
            onCancel={() => router.push(`/users/${userId}`)}
            errorMessage={errorMsg}
          />
        </div>
      </PageContainer>
    </PermissionGuard>
  );
}
