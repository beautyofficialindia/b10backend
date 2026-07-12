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
import { PasswordField } from '@/components/forms';
import { useChangePassword } from '@/features/auth';

const changePasswordSchema = z.object({
  old_password: z.string().min(1, 'Current password is required').trim(),
  new_password: z.string().min(8, 'Password must be at least 8 characters').trim(),
  confirm_password: z.string().min(1, 'Please confirm your new password').trim()
}).refine(data => data.new_password === data.confirm_password, {
  message: "Passwords don't match",
  path: ['confirm_password'],
});

type ChangePasswordFormData = z.infer<typeof changePasswordSchema>;

interface ChangePasswordDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function ChangePasswordDialog({ open, onOpenChange }: ChangePasswordDialogProps) {
  const changePasswordMutation = useChangePassword();

  const {
    control,
    handleSubmit,
    reset,
    formState: { errors }
  } = useForm<ChangePasswordFormData>({
    resolver: zodResolver(changePasswordSchema),
    defaultValues: { old_password: '', new_password: '', confirm_password: '' }
  });

  // Security: Clear state on close
  React.useEffect(() => {
    if (!open) {
      reset({ old_password: '', new_password: '', confirm_password: '' });
      changePasswordMutation.reset();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [open, reset]);

  const onSubmit = (data: ChangePasswordFormData) => {
    changePasswordMutation.mutate(
      { old_password: data.old_password, new_password: data.new_password },
      {
        onSuccess: () => {
          toast.success('Password changed successfully.');
          onOpenChange(false);
        },
        onError: (error) => {
          let msg = 'Failed to change password. Please try again.';
          if (error instanceof AxiosError && error.response) {
            const resData = error.response.data;
            if (resData?.old_password) msg = resData.old_password[0];
            else if (resData?.new_password) msg = resData.new_password[0];
            else if (error.response.status === 401 || error.response.status === 403) {
              msg = 'Your session has expired. Please log in again.';
            }
          }
          toast.error(msg);
        }
      }
    );
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Change Password</DialogTitle>
          <DialogDescription>
            Enter your current password and a new password. The new password must be at least 8 characters long.
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4 py-2">
          <Controller
            control={control}
            name="old_password"
            render={({ field }) => (
              <PasswordField 
                label="Current Password" 
                placeholder="Enter current password" 
                autoComplete="current-password"
                {...field} 
                error={errors.old_password?.message}
              />
            )}
          />

          <Controller
            control={control}
            name="new_password"
            render={({ field }) => (
              <PasswordField 
                label="New Password" 
                placeholder="Enter new password" 
                autoComplete="new-password"
                {...field} 
                error={errors.new_password?.message}
              />
            )}
          />

          <Controller
            control={control}
            name="confirm_password"
            render={({ field }) => (
              <PasswordField 
                label="Confirm New Password" 
                placeholder="Confirm new password" 
                autoComplete="new-password"
                {...field} 
                error={errors.confirm_password?.message}
              />
            )}
          />

          <DialogFooter className="pt-4">
            <Button 
              type="button" 
              variant="outline" 
              onClick={() => onOpenChange(false)}
              disabled={changePasswordMutation.isPending}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={changePasswordMutation.isPending}>
              {changePasswordMutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Change Password
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
