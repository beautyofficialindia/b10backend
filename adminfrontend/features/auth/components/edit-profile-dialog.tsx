'use client';

import * as React from 'react';
import { z } from 'zod';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { AxiosError } from 'axios';
import { toast } from 'sonner';
import { Loader2 } from 'lucide-react';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { useUpdateProfile, useAuth } from '@/features/auth';

const updateProfileSchema = z.object({
  first_name: z.string().min(1, 'First name is required').trim(),
  last_name: z.string().min(1, 'Last name is required').trim(),
  email: z.string().email('Invalid email address').trim(),
  username: z.string().min(3, 'Username must be at least 3 characters').trim(),
});

type UpdateProfileFormData = z.infer<typeof updateProfileSchema>;

interface EditProfileDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function EditProfileDialog({ open, onOpenChange }: EditProfileDialogProps) {
  const { user } = useAuth();
  const updateProfileMutation = useUpdateProfile();

  const {
    control,
    handleSubmit,
    reset,
    setError,
    formState: { errors }
  } = useForm<UpdateProfileFormData>({
    resolver: zodResolver(updateProfileSchema),
    defaultValues: { 
      first_name: user?.first_name || '', 
      last_name: user?.last_name || '', 
      email: user?.email || '', 
      username: user?.username || '' 
    }
  });

  // Pre-fill when dialog opens or user data loads
  React.useEffect(() => {
    if (open && user) {
      reset({ 
        first_name: user.first_name || '', 
        last_name: user.last_name || '', 
        email: user.email || '', 
        username: user.username || '' 
      });
      updateProfileMutation.reset();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [open, user, reset]);

  const onSubmit = (data: UpdateProfileFormData) => {
    updateProfileMutation.mutate(data, {
      onSuccess: () => {
        toast.success('Profile updated successfully.');
        onOpenChange(false);
      },
      onError: (error) => {
        if (error instanceof AxiosError && error.response) {
          const resData = error.response.data;
          let handledField = false;

          ['username', 'email', 'first_name', 'last_name'].forEach((field) => {
            if (resData?.[field]) {
              setError(field as keyof UpdateProfileFormData, {
                type: 'server',
                message: Array.isArray(resData[field]) ? resData[field][0] : resData[field]
              });
              handledField = true;
            }
          });

          if (handledField) return;

          let msg = 'Failed to update profile. Please try again.';
          if (resData?.detail) {
            msg = Array.isArray(resData.detail) ? resData.detail[0] : resData.detail;
          } else if (error.response.status === 401 || error.response.status === 403) {
            msg = 'Your session has expired. Please log in again.';
          }
          toast.error(msg);
        } else {
          toast.error('Network error. Please try again.');
        }
      }
    });
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Edit Profile</DialogTitle>
          <DialogDescription>
            Update your personal account details.
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4 py-2">
          <div className="grid grid-cols-2 gap-4">
            <Controller
              control={control}
              name="first_name"
              render={({ field }) => (
                <div className="space-y-2">
                  <label htmlFor="first_name" className="text-sm font-medium leading-none">First Name</label>
                  <Input id="first_name" placeholder="John" {...field} />
                  {errors.first_name && <p className="text-[0.8rem] font-medium text-destructive">{errors.first_name.message}</p>}
                </div>
              )}
            />
            <Controller
              control={control}
              name="last_name"
              render={({ field }) => (
                <div className="space-y-2">
                  <label htmlFor="last_name" className="text-sm font-medium leading-none">Last Name</label>
                  <Input id="last_name" placeholder="Doe" {...field} />
                  {errors.last_name && <p className="text-[0.8rem] font-medium text-destructive">{errors.last_name.message}</p>}
                </div>
              )}
            />
          </div>

          <Controller
            control={control}
            name="username"
            render={({ field }) => (
              <div className="space-y-2">
                <label htmlFor="username" className="text-sm font-medium leading-none">Username</label>
                <Input id="username" placeholder="johndoe" {...field} />
                {errors.username && <p className="text-[0.8rem] font-medium text-destructive">{errors.username.message}</p>}
              </div>
            )}
          />

          <Controller
            control={control}
            name="email"
            render={({ field }) => (
              <div className="space-y-2">
                <label htmlFor="email" className="text-sm font-medium leading-none">Email</label>
                <Input id="email" type="email" placeholder="john@example.com" {...field} />
                {errors.email && <p className="text-[0.8rem] font-medium text-destructive">{errors.email.message}</p>}
              </div>
            )}
          />

          <DialogFooter className="pt-4">
            <Button 
              type="button" 
              variant="outline" 
              onClick={() => onOpenChange(false)}
              disabled={updateProfileMutation.isPending}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={updateProfileMutation.isPending}>
              {updateProfileMutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Save Changes
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
