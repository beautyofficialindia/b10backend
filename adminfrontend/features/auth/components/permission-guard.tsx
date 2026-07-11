'use client';

import { useAuth } from '../hooks/use-auth';

interface PermissionGuardProps {
  permissions?: readonly string[];
  requireAll?: boolean;
  children: React.ReactNode;
  fallback?: React.ReactNode;
}

export function PermissionGuard({
  permissions = [],
  requireAll = true,
  children,
  fallback = null,
}: PermissionGuardProps) {
  const { user, isAuthenticated, isLoading } = useAuth();

  // If auth is still loading, return fallback to prevent flashes of unauthorized content
  if (isLoading) {
    return <>{fallback}</>;
  }

  // Must be authenticated
  if (!isAuthenticated || !user) {
    return <>{fallback}</>;
  }

  // Superusers bypass all permission checks
  if (user.is_superuser) {
    return <>{children}</>;
  }

  // If no specific permissions are required, just being authenticated is enough
  if (permissions.length === 0) {
    return <>{children}</>;
  }

  // Check permissions
  const hasAccess = requireAll
    ? permissions.every((p) => user.permissions?.includes(p))
    : permissions.some((p) => user.permissions?.includes(p));

  if (!hasAccess) {
    return <>{fallback}</>;
  }

  return <>{children}</>;
}
