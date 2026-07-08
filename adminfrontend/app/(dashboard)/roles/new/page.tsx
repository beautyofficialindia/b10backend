'use client';

import { useRouter } from 'next/navigation';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { PageContainer } from '@/components/layout';
import { TextField, FormSection } from '@/components/forms';
import { ErrorAlert } from '@/components/common';
import { Button } from '@/components/ui/button';
import { ArrowLeft, Save, Loader2 } from 'lucide-react';
import { useCreateRole } from '@/features/roles';
import { AxiosError } from 'axios';

const schema = z.object({ name: z.string().min(1, 'Role name is required') });
type FormData = z.infer<typeof schema>;

export default function NewRolePage() {
  const router = useRouter();
  const createMutation = useCreateRole();
  const { register, handleSubmit, formState: { errors } } = useForm<FormData>({
    resolver: zodResolver(schema),
  });

  const onSubmit = (data: FormData) => {
    createMutation.mutate(data, { onSuccess: (res) => router.push(`/roles/${res.data.id}`) });
  };

  const errorMsg = createMutation.error instanceof AxiosError
    ? createMutation.error.response?.data?.message || 'Failed to create role'
    : null;

  return (
    <PageContainer>
      <Button variant="ghost" size="sm" className="gap-1.5 -ml-2 mb-2" onClick={() => router.push('/roles')}>
        <ArrowLeft className="h-3.5 w-3.5" />Back to Roles
      </Button>
      <div className="max-w-md">
        <h1 className="text-xl font-semibold mb-6">Create Role</h1>
        {errorMsg && <ErrorAlert message={errorMsg} className="mb-4" />}
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
          <FormSection title="Role Details">
            <TextField label="Role Name" required placeholder="e.g. Marketing" error={errors.name?.message} {...register('name')} />
          </FormSection>
          <div className="flex gap-3">
            <Button type="submit" disabled={createMutation.isPending} className="gap-1.5">
              {createMutation.isPending ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <Save className="h-3.5 w-3.5" />}
              Create Role
            </Button>
            <Button type="button" variant="outline" onClick={() => router.push('/roles')}>Cancel</Button>
          </div>
        </form>
      </div>
    </PageContainer>
  );
}
