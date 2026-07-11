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
import { useResetPassword } from '@/features/users';

const resetSchema = z.object({
  password: z.string().min(8, 'Password must be at least 8 characters').trim(),
  confirm_password: z.string().trim()
}).refine(data => data.password === data.confirm_password, {
  message: "Passwords don't match",
  path: ['confirm_password'],
});

type ResetFormData = z.infer<typeof resetSchema>;

interface ResetPasswordDialogProps {
  userId: number;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function ResetPasswordDialog({ userId, open, onOpenChange }: ResetPasswordDialogProps) {
  const resetMutation = useResetPassword();

  const {
    control,
    handleSubmit,
    reset,
    formState: { errors }
  } = useForm<ResetFormData>({
    resolver: zodResolver(resetSchema),
    defaultValues: { password: '', confirm_password: '' }
  });

  // Security: Clear state on close
  React.useEffect(() => {
    if (!open) {
      reset({ password: '', confirm_password: '' });
      resetMutation.reset();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [open, reset]);

  const onSubmit = (data: ResetFormData) => {
    resetMutation.mutate(
      { id: userId, password: data.password },
      {
        onSuccess: () => {
          toast.success('Password reset successfully');
          onOpenChange(false);
        },
        onError: (error) => {
          let msg = 'Failed to reset password. Please try again.';
          if (error instanceof AxiosError && error.response) {
            const status = error.response.status;
            if (status === 400) msg = 'Invalid password provided.';
            else if (status === 401 || status === 403) msg = 'You do not have permission to perform this action.';
            else if (status === 404) msg = 'User not found.';
            else if (status >= 500) msg = 'An unexpected server error occurred.';
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
          <DialogTitle>Reset Password</DialogTitle>
          <DialogDescription>
            Enter a new password for this user. The password must be at least 8 characters long.
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4 py-2">
          <Controller
            control={control}
            name="password"
            render={({ field }) => (
              <PasswordField 
                label="New Password" 
                placeholder="Enter new password" 
                autoComplete="new-password"
                {...field} 
                error={errors.password?.message}
              />
            )}
          />

          <Controller
            control={control}
            name="confirm_password"
            render={({ field }) => (
              <PasswordField 
                label="Confirm Password" 
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
              disabled={resetMutation.isPending}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={resetMutation.isPending}>
              {resetMutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Reset Password
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
