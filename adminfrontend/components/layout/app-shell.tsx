'use client';

import { useState } from 'react';
import { Sidebar } from './sidebar';
import { Header } from './header';

interface AppShellProps {
  children: React.ReactNode;
}

export function AppShell({ children }: AppShellProps) {
  const [collapsed, setCollapsed] = useState(false);

  return (
    <div className="relative flex min-h-screen">
      <Sidebar collapsed={collapsed} onToggle={() => setCollapsed(!collapsed)} />

      <div
        className="flex flex-1 flex-col transition-[margin-left] duration-200 ease-in-out lg:ml-64"
        style={{ marginLeft: undefined }}
        data-collapsed={collapsed}
      >
        <style>{`
          @media (min-width: 1024px) {
            [data-collapsed="true"] { margin-left: 64px !important; }
            [data-collapsed="false"] { margin-left: 256px !important; }
          }
        `}</style>
        <Header />
        <main className="flex-1">{children}</main>
      </div>
    </div>
  );
}
