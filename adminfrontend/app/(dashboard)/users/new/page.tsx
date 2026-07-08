'use client';

import { useRouter } from 'next/navigation';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { PageContainer } from '@/components/layout';
import { TextField, PasswordField, FormSection, CheckboxField } from '@/components/forms';
import { ErrorAlert } from '@/components/common';
import { Button } from '@/components/ui/button';
import { ArrowLeft, Save, Loader2 } from 'lucide-react';
import { useCreateUser } from '@/features/users';
import { AxiosError } from 'axios';

const schema = z.object({
  username: z.string().min(1, 'Required'),
  email: z.string().email('Invalid email'),
  password: z.string().min(8, 'Min 8 characters'),
  first_name: z.string().optional(),
  last_name: z.string().optional(),
  is_staff: z.boolean(),
  is_superuser: z.boolean(),
});
type FormData = z.infer<typeof schema>;

export default function NewUserPage() {
  const router = useRouter();
  const createMutation = useCreateUser();
  const { register, handleSubmit, setValue, watch, formState: { errors } } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: { username: '', email: '', password: '', first_name: '', last_name: '', is_staff: true, is_superuser: false },
  });

  const onSubmit = (data: FormData) => {
    createMutation.mutate(
      { ...data, groups: [], is_active: true },
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
        {errorMsg && <ErrorAlert message={errorMsg} className="mb-4" />}

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
          <FormSection title="Account">
            <TextField label="Username" required error={errors.username?.message} {...register('username')} />
            <TextField label="Email" required error={errors.email?.message} {...register('email')} />
            <PasswordField label="Password" required error={errors.password?.message} {...register('password')} />
          </FormSection>

          <FormSection title="Profile">
            <TextField label="First Name" {...register('first_name')} />
            <TextField label="Last Name" {...register('last_name')} />
          </FormSection>

          <FormSection title="Permissions">
            <CheckboxField label="Staff" description="Can access admin panel" checked={watch('is_staff')} onCheckedChange={(v) => setValue('is_staff', v)} />
            <CheckboxField label="Superuser" description="Full system access" checked={watch('is_superuser')} onCheckedChange={(v) => setValue('is_superuser', v)} />
          </FormSection>

          <div className="flex gap-3">
            <Button type="submit" disabled={createMutation.isPending} className="gap-1.5">
              {createMutation.isPending ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <Save className="h-3.5 w-3.5" />}
              Create User
            </Button>
            <Button type="button" variant="outline" onClick={() => router.push('/users')}>Cancel</Button>
          </div>
        </form>
      </div>
    </PageContainer>
  );
}
