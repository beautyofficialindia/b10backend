'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { PageContainer, PageHeader } from '@/components/layout';
import {
  StatCard, MetricCard, InfoCard, ActionCard,
  SuccessAlert, ErrorAlert, WarningAlert, InfoAlert,
  StatusBadge, RoleBadge, PriorityBadge,
  SkeletonCard, SkeletonTable,
  EmptyState, ErrorState, CopyButton,
  ConfirmDialog, DeleteDialog,
} from '@/components/common';
import { DataTable, TableToolbar, TablePagination, type Column } from '@/components/tables';
import { TextField, PasswordField, SearchField, TextAreaField, CheckboxField, SwitchField, FormSection } from '@/components/forms';
import { LineChartCard, BarChartCard } from '@/components/charts';
import { Users, TrendingUp, DollarSign, Activity, Inbox, Loader2, Plus } from 'lucide-react';

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="space-y-4">
      <h2 className="text-lg font-semibold border-b pb-2">{title}</h2>
      {children}
    </section>
  );
}

export default function ShowcasePage() {
  const [confirmOpen, setConfirmOpen] = useState(false);
  const [deleteOpen, setDeleteOpen] = useState(false);
  const [switchVal, setSwitchVal] = useState(true);
  const [checkVal, setCheckVal] = useState(false);

  const sampleData = [
    { id: 1, name: 'John Doe', email: 'john@test.com', status: 'active', role: 'Admin' },
    { id: 2, name: 'Jane Smith', email: 'jane@test.com', status: 'inactive', role: 'Support' },
    { id: 3, name: 'Bob Wilson', email: 'bob@test.com', status: 'active', role: 'Sales' },
  ];

  const columns: Column<typeof sampleData[0]>[] = [
    { key: 'name', header: 'Name' },
    { key: 'email', header: 'Email' },
    { key: 'status', header: 'Status', render: (row) => <StatusBadge status={row.status as 'active' | 'inactive'} /> },
    { key: 'role', header: 'Role', render: (row) => <RoleBadge role={row.role} /> },
  ];

  return (
    <PageContainer>
      <PageHeader title="UI Showcase" description="Design system component library" />

      {/* Typography */}
      <Section title="1. Typography">
        <div className="space-y-3">
          <h1 className="text-4xl font-bold tracking-tight">Display — 4xl Bold</h1>
          <h1 className="text-3xl font-semibold tracking-tight">Heading 1 — 3xl Semibold</h1>
          <h2 className="text-2xl font-semibold tracking-tight">Heading 2 — 2xl Semibold</h2>
          <h3 className="text-xl font-semibold">Heading 3 — xl Semibold</h3>
          <h4 className="text-lg font-medium">Heading 4 — lg Medium</h4>
          <p className="text-base">Body — base regular. The quick brown fox jumps over the lazy dog.</p>
          <p className="text-sm text-muted-foreground">Small — sm muted. Secondary information.</p>
          <p className="text-xs text-muted-foreground">Caption — xs muted. Timestamps and metadata.</p>
          <label className="text-sm font-medium">Label — sm medium</label>
        </div>
      </Section>

      {/* Buttons */}
      <Section title="2. Buttons">
        <div className="flex flex-wrap gap-3">
          <Button>Primary</Button>
          <Button variant="secondary">Secondary</Button>
          <Button variant="outline">Outline</Button>
          <Button variant="ghost">Ghost</Button>
          <Button variant="destructive">Destructive</Button>
          <Button disabled>Disabled</Button>
          <Button disabled><Loader2 className="mr-2 h-4 w-4 animate-spin" />Loading</Button>
          <Button size="icon"><Plus className="h-4 w-4" /></Button>
          <Button size="sm">Small</Button>
          <Button size="lg">Large</Button>
        </div>
      </Section>

      {/* Cards */}
      <Section title="3. Cards">
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <StatCard title="Total Users" value="1,234" change="+12% from last month" changeType="positive" icon={Users} />
          <StatCard title="Revenue" value="$45,231" change="-3.2% from last month" changeType="negative" icon={DollarSign} />
          <MetricCard title="Active Sessions" value="89" subtitle="Real-time" icon={Activity} />
          <MetricCard title="Conversion Rate" value="23.5%" subtitle="Last 30 days" icon={TrendingUp} />
        </div>
        <div className="grid gap-4 sm:grid-cols-2">
          <InfoCard title="System Status" description="All systems operational. Last checked 2 minutes ago." />
          <ActionCard title="Quick Action" description="Perform a common task" action={<Button size="sm">Execute</Button>} />
        </div>
      </Section>

      {/* Forms */}
      <Section title="4. Forms">
        <div className="max-w-md space-y-4">
          <FormSection title="Account Information" description="Basic fields">
            <TextField label="Full Name" placeholder="Enter name" required />
            <TextField label="Email" placeholder="email@example.com" error="This email is already taken" />
            <PasswordField label="Password" placeholder="Enter password" required />
            <SearchField placeholder="Search users..." />
            <TextAreaField label="Description" placeholder="Enter description..." description="Max 500 characters" />
            <CheckboxField label="Accept Terms" description="You agree to our terms of service" checked={checkVal} onCheckedChange={setCheckVal} />
            <SwitchField label="Enable Notifications" description="Receive email notifications" checked={switchVal} onCheckedChange={setSwitchVal} />
          </FormSection>
        </div>
      </Section>

      {/* Badges */}
      <Section title="5. Badges">
        <div className="flex flex-wrap gap-3">
          <StatusBadge status="active" />
          <StatusBadge status="inactive" />
          <StatusBadge status="pending" />
          <StatusBadge status="error" label="Failed" />
          <RoleBadge role="Admin" />
          <RoleBadge role="Sales" />
          <RoleBadge role="Support" />
          <PriorityBadge priority="low" />
          <PriorityBadge priority="medium" />
          <PriorityBadge priority="high" />
          <PriorityBadge priority="critical" />
        </div>
      </Section>

      {/* Alerts */}
      <Section title="6. Alerts">
        <div className="space-y-3 max-w-lg">
          <SuccessAlert title="Success" message="Settings saved successfully." />
          <ErrorAlert title="Error" message="Failed to process request. Please try again." />
          <WarningAlert title="Warning" message="Your trial expires in 3 days." />
          <InfoAlert title="Info" message="A new version is available." />
        </div>
      </Section>

      {/* Dialogs */}
      <Section title="7. Dialogs">
        <div className="flex gap-3">
          <Button variant="outline" onClick={() => setConfirmOpen(true)}>Open Confirm</Button>
          <Button variant="destructive" onClick={() => setDeleteOpen(true)}>Open Delete</Button>
        </div>
        <ConfirmDialog
          open={confirmOpen}
          onOpenChange={setConfirmOpen}
          title="Confirm Action"
          description="Are you sure you want to proceed?"
          onConfirm={() => setConfirmOpen(false)}
        />
        <DeleteDialog
          open={deleteOpen}
          onOpenChange={setDeleteOpen}
          itemName="Test Item"
          onConfirm={() => setDeleteOpen(false)}
        />
      </Section>

      {/* Table */}
      <Section title="8. Tables">
        <TableToolbar searchPlaceholder="Search users...">
          <Button size="sm"><Plus className="mr-1.5 h-3.5 w-3.5" />Add User</Button>
        </TableToolbar>
        <DataTable columns={columns} data={sampleData} />
        <TablePagination page={1} totalPages={5} totalCount={47} pageSize={10} onPageChange={() => {}} />
      </Section>

      {/* Empty & Error States */}
      <Section title="9. Empty & Error States">
        <div className="grid gap-4 sm:grid-cols-2">
          <div className="rounded-lg border p-4">
            <EmptyState icon={Inbox} title="No data yet" description="Get started by creating your first item." >
              <Button size="sm">Create</Button>
            </EmptyState>
          </div>
          <div className="rounded-lg border p-4">
            <ErrorState onRetry={() => {}} />
          </div>
        </div>
      </Section>

      {/* Skeletons */}
      <Section title="10. Skeleton Loaders">
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <SkeletonCard />
          <SkeletonCard />
          <SkeletonCard />
          <SkeletonCard />
        </div>
        <SkeletonTable rows={3} cols={4} />
      </Section>

      {/* Charts */}
      <Section title="11. Chart Wrappers">
        <div className="grid gap-4 sm:grid-cols-2">
          <LineChartCard title="Revenue Over Time" description="Monthly revenue">
            <div className="flex items-center justify-center h-full text-sm text-muted-foreground">
              Chart placeholder
            </div>
          </LineChartCard>
          <BarChartCard title="Leads by Source" description="This month">
            <div className="flex items-center justify-center h-full text-sm text-muted-foreground">
              Chart placeholder
            </div>
          </BarChartCard>
        </div>
      </Section>

      {/* Utility */}
      <Section title="12. Utilities">
        <div className="flex items-center gap-2">
          <code className="text-sm bg-muted px-2 py-1 rounded">sk-abc123xyz</code>
          <CopyButton value="sk-abc123xyz" />
        </div>
      </Section>
    </PageContainer>
  );
}
