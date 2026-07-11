'use client';

import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { TextField, PasswordField, FormSection, CheckboxField } from '@/components/forms';
import { ErrorAlert } from '@/components/common';
import { Button } from '@/components/ui/button';
import { Save, Loader2 } from 'lucide-react';
import { useEffect } from 'react';
import { RoleSelector } from './role-selector';

const baseSchema = z.object({
  username: z.string().min(1, 'Required'),
  email: z.string().email('Invalid email'),
  first_name: z.string().optional(),
  last_name: z.string().optional(),
  is_staff: z.boolean(),
  is_superuser: z.boolean(),
  groups: z.array(z.string()).default([]),
});

const createSchema = baseSchema.extend({
  password: z.string().min(8, 'Min 8 characters'),
});

const editSchema = baseSchema;

export type UserFormData = z.infer<typeof createSchema>;

interface UserFormProps {
  initialData?: Partial<UserFormData>;
  onSubmit: (data: any) => void;
  isSubmitting?: boolean;
  isEditMode?: boolean;
  onCancel: () => void;
  errorMessage?: string | null;
}

export function UserForm({
  initialData,
  onSubmit,
  isSubmitting = false,
  isEditMode = false,
  onCancel,
  errorMessage,
}: UserFormProps) {
  const schema = isEditMode ? editSchema : createSchema;
  
  const { register, handleSubmit, setValue, watch, reset, formState: { errors } } = useForm<UserFormData>({
    resolver: zodResolver(schema) as any,
    defaultValues: {
      username: '',
      email: '',
      password: '',
      first_name: '',
      last_name: '',
      is_staff: true,
      is_superuser: false,
      groups: [],
      ...initialData,
    },
  });

  useEffect(() => {
    if (initialData) {
      reset({
        ...initialData,
        is_staff: initialData.is_staff ?? true,
        is_superuser: initialData.is_superuser ?? false,
      });
    }
  }, [initialData, reset]);

  return (
    <div className="max-w-lg">
      {errorMessage && <ErrorAlert message={errorMessage} className="mb-4" />}

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        <FormSection title="Account">
          <TextField 
            label="Username" 
            required 
            error={errors.username?.message as string} 
            disabled={isEditMode}
            {...register('username')} 
          />
          <TextField 
            label="Email" 
            required 
            error={errors.email?.message as string} 
            {...register('email')} 
          />
          {!isEditMode && (
            <PasswordField 
              label="Password" 
              required 
              error={errors.password?.message as string} 
              {...register('password')} 
            />
          )}
        </FormSection>

        <FormSection title="Profile">
          <TextField label="First Name" error={errors.first_name?.message as string} {...register('first_name')} />
          <TextField label="Last Name" error={errors.last_name?.message as string} {...register('last_name')} />
        </FormSection>

        <FormSection title="Permissions">
          <div className="space-y-1.5 mb-4">
            <label className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">Business Roles</label>
            <RoleSelector 
              value={watch('groups')} 
              onChange={(val) => setValue('groups', val, { shouldDirty: true })} 
            />
          </div>
          <CheckboxField 
            label="Staff" 
            description="Can access admin panel" 
            checked={watch('is_staff')} 
            onCheckedChange={(v) => setValue('is_staff', !!v)} 
          />
          <CheckboxField 
            label="Superuser" 
            description="Full system access" 
            checked={watch('is_superuser')} 
            onCheckedChange={(v) => setValue('is_superuser', !!v)} 
          />
        </FormSection>

        <div className="flex gap-3">
          <Button type="submit" disabled={isSubmitting} className="gap-1.5">
            {isSubmitting ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <Save className="h-3.5 w-3.5" />}
            {isEditMode ? 'Save Changes' : 'Create User'}
          </Button>
          <Button type="button" variant="outline" onClick={onCancel} disabled={isSubmitting}>
            Cancel
          </Button>
        </div>
      </form>
    </div>
  );
}
