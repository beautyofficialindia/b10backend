'use client';

import { useAuth, useHasPermission } from '../hooks/use-auth';

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
  const { isAuthenticated, isLoading } = useAuth();
  const hasAccess = useHasPermission(permissions, requireAll);

  // If auth is still loading, return fallback to prevent flashes of unauthorized content
  if (isLoading) {
    return <>{fallback}</>;
  }

  // Must be authenticated
  if (!isAuthenticated) {
    return <>{fallback}</>;
  }

  if (!hasAccess) {
    return <>{fallback}</>;
  }

  return <>{children}</>;
}
