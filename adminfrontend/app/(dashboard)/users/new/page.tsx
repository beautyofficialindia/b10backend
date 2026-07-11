'use client';

import { useRouter } from 'next/navigation';
import { PageContainer } from '@/components/layout';
import { Button } from '@/components/ui/button';
import { ArrowLeft } from 'lucide-react';
import { useCreateUser } from '@/features/users';
import { UserForm, type UserFormData } from '@/features/users/components';
import { AxiosError } from 'axios';

export default function NewUserPage() {
  const router = useRouter();
  const createMutation = useCreateUser();

  const onSubmit = (data: UserFormData) => {
    createMutation.mutate(
      { ...data, is_active: true },
      { onSuccess: (res) => router.push(`/users/${res.data.id}`) }
    );
  };

  const errorMsg = createMutation.error instanceof AxiosError
    ? createMutation.error.response?.data?.message || 'Failed to create user'
    : null;

  return (
    <PageContainer>
      <Button variant="ghost" size="sm" className="gap-1.5 -ml-2 mb-2" onClick={() => router.push('/users')}>
        <ArrowLeft className="h-3.5 w-3.5" />Back to Users
      </Button>

      <div className="max-w-lg">
        <h1 className="text-xl font-semibold mb-6">Create User</h1>
        <UserForm 
          onSubmit={onSubmit}
          isSubmitting={createMutation.isPending}
          isEditMode={false}
          onCancel={() => router.push('/users')}
          errorMessage={errorMsg}
        />
      </div>
    </PageContainer>
  );
}
