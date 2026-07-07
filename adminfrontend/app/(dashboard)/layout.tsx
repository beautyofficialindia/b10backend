'use client';

import { AppShell } from '@/components/layout';
import { AuthGuard } from '@/features/auth';

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <AuthGuard>
      <AppShell>{children}</AppShell>
    </AuthGuard>
  );
}
