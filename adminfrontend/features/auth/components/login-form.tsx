'use client';

import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Button } from '@/components/ui/button';
import { TextField, PasswordField } from '@/components/forms';
import { ErrorAlert } from '@/components/common';
import { loginSchema, type LoginFormData } from '../schemas';
import { useAuth } from '../hooks/use-auth';
import { Loader2 } from 'lucide-react';
import { AxiosError } from 'axios';

export function LoginForm() {
  const { login, isLoginLoading, loginError } = useAuth();

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
  });

  const onSubmit = async (data: LoginFormData) => {
    try {
      await login(data);
    } catch {
      // Error handled by mutation state
    }
  };

  const getErrorMessage = (): string | null => {
    if (!loginError) return null;
    if (loginError instanceof AxiosError) {
      if (loginError.response?.status === 401) return 'Invalid username or password.';
      if (loginError.response?.status === 403) return 'Your account has been deactivated.';
      if (!loginError.response) return 'Unable to connect to server. Please check your connection.';
      return 'An unexpected error occurred. Please try again.';
    }
    return 'An unexpected error occurred.';
  };

  const errorMessage = getErrorMessage();

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
      {errorMessage && <ErrorAlert message={errorMessage} />}

      <TextField
        label="Username"
        placeholder="Enter your username"
        error={errors.username?.message}
        autoComplete="username"
        autoFocus
        {...register('username')}
      />

      <PasswordField
        label="Password"
        placeholder="Enter your password"
        error={errors.password?.message}
        autoComplete="current-password"
        {...register('password')}
      />

      <Button type="submit" className="w-full" disabled={isLoginLoading}>
        {isLoginLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
        {isLoginLoading ? 'Signing in...' : 'Sign in'}
      </Button>
    </form>
  );
}
