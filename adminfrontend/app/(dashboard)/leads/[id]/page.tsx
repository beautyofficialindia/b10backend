'use client';

import { use } from 'react';

import { PageContainer, PageBreadcrumbs } from '@/components/layout';
import { StatusBadge, ErrorState, CopyButton } from '@/components/common';
import { Skeleton } from '@/components/ui/skeleton';
import { Button } from '@/components/ui/button';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs';
import { Mail, Phone, Building2, Clock, Target, Briefcase, DollarSign, Edit3 } from 'lucide-react';
import { useLeadDetail, useUpdateLeadStatus, type LeadStatus } from '@/features/leads';
import { getStatusVariant } from '@/features/leads/utils';
import { UnifiedTimeline, useUnifiedTimeline, LeadAssignmentWidget, LeadFollowUpWidget, PendingFollowUpBanner, FollowupsTab, NotesTab, ConversationTab } from '@/features/crm';
import { PermissionGuard } from '@/features/auth/components/permission-guard';

const statusActions: { value: LeadStatus; label: string }[] = [
  { value: 'gathering', label: 'Gathering' },
  { value: 'qualified', label: 'Qualified' },
  { value: 'converted', label: 'Converted' },
  { value: 'escalated', label: 'Escalated' },
  { value: 'lost', label: 'Lost' },
];

function InfoRow({ icon: Icon, label, value, copyable }: { icon: React.ElementType; label: string; value: string | null | undefined; copyable?: boolean }) {
  if (!value) return null;
  return (
    <div className="flex items-start gap-3 py-2.5">
      <Icon className="h-4 w-4 text-muted-foreground mt-0.5 shrink-0" />
      <div className="flex-1 min-w-0">
        <p className="text-xs text-muted-foreground">{label}</p>
        <div className="flex items-center gap-1">
          <p className="text-sm font-medium break-words">{value}</p>
          {copyable && <CopyButton value={value} />}
        </div>
      </div>
    </div>
  );
}

function ScoreBar({ score }: { score: number }) {
  const color = score >= 70 ? 'bg-emerald-500' : score >= 40 ? 'bg-amber-500' : 'bg-red-400';
  return (
    <div className="space-y-1">
      <div className="flex justify-between text-xs">
        <span className="text-muted-foreground">Lead Score</span>
        <span className="font-semibold">{score}/100</span>
      </div>
      <div className="h-2 rounded-full bg-muted overflow-hidden">
        <div className={`h-full rounded-full transition-all ${color}`} style={{ width: `${score}%` }} />
      </div>
    </div>
  );
}

export default function LeadDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const { data: lead, isLoading, isError, refetch } = useLeadDetail(id);
  const updateStatus = useUpdateLeadStatus();
  const timeline = useUnifiedTimeline(id);

  if (isLoading) {
    return (
      <PageContainer>
        <Skeleton className="h-6 w-32 mb-4" />
        <div className="rounded-xl border bg-card p-6 space-y-4">
          <Skeleton className="h-7 w-64" />
          <Skeleton className="h-4 w-48" />
          <Skeleton className="h-4 w-32" />
        </div>
        <div className="grid gap-6 lg:grid-cols-3 mt-6">
          <div className="lg:col-span-2 space-y-4">
            <Skeleton className="h-10 w-full" />
            <Skeleton className="h-48 w-full" />
          </div>
          <div className="space-y-4">
            <Skeleton className="h-32 w-full" />
            <Skeleton className="h-48 w-full" />
          </div>
        </div>
      </PageContainer>
    );
  }

  if (isError || !lead) {
    return (
      <PageContainer>
        <ErrorState title="Lead not found" message="This lead may have been deleted or you don't have access." onRetry={() => refetch()} />
      </PageContainer>
    );
  }

  return (
    <PageContainer>
      <div className="mb-4">
        <PageBreadcrumbs items={[
          { label: 'CRM', href: '/crm' },
          { label: 'Leads', href: '/leads' },
          { label: lead.full_name || 'Anonymous Lead', href: `/leads/${lead.id}` }
        ]} />
      </div>

      {/* Pending Follow Up Banner */}
      <PendingFollowUpBanner leadId={lead.id} />

      {/* Summary Cards Row */}
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-4 mb-6">
        <div className="rounded-xl border bg-card p-4 shadow-sm flex flex-col items-center justify-center text-center">
          <p className="text-[10px] uppercase text-muted-foreground font-semibold mb-1">Status</p>
          <StatusBadge status={getStatusVariant(lead.status)} label={lead.status} />
        </div>
        <div className="rounded-xl border bg-card p-4 shadow-sm flex flex-col items-center justify-center text-center">
          <p className="text-[10px] uppercase text-muted-foreground font-semibold mb-1">Assigned</p>
          <p className="text-sm font-medium">{lead.assigned_admin_id ? 'Assigned' : 'Unassigned'}</p>
        </div>
        <div className="rounded-xl border bg-card p-4 shadow-sm flex flex-col items-center justify-center text-center">
          <p className="text-[10px] uppercase text-muted-foreground font-semibold mb-1">Priority</p>
          <p className="text-sm font-medium capitalize">{lead.priority || 'Normal'}</p>
        </div>
        <div className="rounded-xl border bg-card p-4 shadow-sm flex flex-col items-center justify-center text-center">
          <p className="text-[10px] uppercase text-muted-foreground font-semibold mb-1">Source</p>
          <p className="text-sm font-medium capitalize truncate w-full">{lead.source}</p>
        </div>
        <div className="rounded-xl border bg-card p-4 shadow-sm flex flex-col items-center justify-center text-center">
          <p className="text-[10px] uppercase text-muted-foreground font-semibold mb-1">Created</p>
          <p className="text-sm font-medium">{new Date(lead.created_at).toLocaleDateString()}</p>
        </div>
        <div className="rounded-xl border bg-card p-4 shadow-sm flex flex-col items-center justify-center text-center">
          <p className="text-[10px] uppercase text-muted-foreground font-semibold mb-1">Activity</p>
          <p className="text-sm font-medium">{lead.last_contacted_at ? new Date(lead.last_contacted_at).toLocaleDateString() : 'None'}</p>
        </div>
        <div className="rounded-xl border bg-card p-4 shadow-sm flex flex-col items-center justify-center text-center">
          <p className="text-[10px] uppercase text-muted-foreground font-semibold mb-1">Score</p>
          <p className={`text-sm font-bold ${lead.lead_score >= 70 ? 'text-emerald-500' : lead.lead_score >= 40 ? 'text-amber-500' : 'text-red-400'}`}>
            {lead.lead_score}/100
          </p>
        </div>
        <div className="rounded-xl border bg-card p-4 shadow-sm flex flex-col items-center justify-center text-center">
          <p className="text-[10px] uppercase text-muted-foreground font-semibold mb-1">Qualified</p>
          <p className="text-sm font-medium">{lead.qualified_at ? new Date(lead.qualified_at).toLocaleDateString() : 'Pending'}</p>
        </div>
      </div>

      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between mb-6">
        <div className="min-w-0">
          <div className="flex items-center gap-3 flex-wrap">
            <h1 className="text-2xl font-semibold truncate">
              {lead.full_name || 'Anonymous Lead'}
            </h1>
          </div>
          <div className="flex flex-wrap items-center gap-x-4 gap-y-1 mt-2 text-sm text-muted-foreground">
            {lead.email && (
              <span className="flex items-center gap-1.5">
                <Mail className="h-3.5 w-3.5" />{lead.email}
                <CopyButton value={lead.email} />
              </span>
            )}
            {lead.phone && (
              <span className="flex items-center gap-1.5">
                <Phone className="h-3.5 w-3.5" />{lead.phone}
                <CopyButton value={lead.phone} />
              </span>
            )}
            {lead.company_name && (
              <span className="flex items-center gap-1.5"><Building2 className="h-3.5 w-3.5" />{lead.company_name}</span>
            )}
          </div>
        </div>
      </div>

      {/* Two column layout */}
      <div className="grid gap-6 lg:grid-cols-3">
        {/* Main content */}
        <div className="lg:col-span-2">
          <Tabs defaultValue="overview">
            <TabsList>
              <TabsTrigger value="overview">Overview</TabsTrigger>
              <TabsTrigger value="conversation">Conversation</TabsTrigger>
              <TabsTrigger value="timeline">Timeline</TabsTrigger>
              <TabsTrigger value="followups">Follow Ups</TabsTrigger>
              <TabsTrigger value="notes">Notes</TabsTrigger>
            </TabsList>

            <TabsContent value="overview" className="mt-4 space-y-4">
              {/* Project Info */}
              {(lead.project_type || lead.industry || lead.budget_range || lead.timeline) && (
                <div className="rounded-lg border p-4">
                  <h3 className="text-sm font-medium mb-2">Project Details</h3>
                  <div className="grid sm:grid-cols-2 gap-x-6">
                    <InfoRow icon={Briefcase} label="Project Type" value={lead.project_type} />
                    <InfoRow icon={Building2} label="Industry" value={lead.industry} />
                    <InfoRow icon={DollarSign} label="Budget" value={lead.budget_range} />
                    <InfoRow icon={Clock} label="Timeline" value={lead.timeline} />
                  </div>
                </div>
              )}

              {/* Requirements */}
              {lead.requirements && (
                <div className="rounded-lg border p-4">
                  <h3 className="text-sm font-medium mb-2">Requirements</h3>
                  <p className="text-sm text-muted-foreground whitespace-pre-wrap leading-relaxed">{lead.requirements}</p>
                </div>
              )}

              {/* Contact */}
              <div className="rounded-lg border p-4">
                <h3 className="text-sm font-medium mb-2">Contact Information</h3>
                <div className="grid sm:grid-cols-2 gap-x-6">
                  <InfoRow icon={Mail} label="Email" value={lead.email} copyable />
                  <InfoRow icon={Phone} label="Phone" value={lead.phone} copyable />
                  <InfoRow icon={Building2} label="Company" value={lead.company_name} />
                  <InfoRow icon={Target} label="Source" value={lead.source} />
                </div>
              </div>
            </TabsContent>

            <TabsContent value="conversation" className="mt-4">
              <ConversationTab conversation={lead.conversation} />
            </TabsContent>

            <TabsContent value="timeline" className="mt-4">
              <UnifiedTimeline 
                items={timeline.items}
                isLoading={timeline.isLoading}
                isError={timeline.isError}
                onRetry={timeline.refetch}
              />
            </TabsContent>

            <TabsContent value="followups" className="mt-4">
              <FollowupsTab leadId={lead.id} />
            </TabsContent>

            <TabsContent value="notes" className="mt-4">
              <NotesTab leadId={lead.id} />
            </TabsContent>
          </Tabs>
        </div>

        {/* Sidebar */}
        <div className="space-y-4 lg:sticky lg:top-6 lg:self-start">
          {/* Status */}
          <PermissionGuard permissions={['leads.change_lead']}>
            <div className="rounded-lg border p-4">
              <h3 className="text-sm font-medium mb-3">Change Status</h3>
              <div className="flex flex-wrap gap-1.5">
                {statusActions.map((s) => (
                  <Button
                    key={s.value}
                    variant={lead.status === s.value ? 'default' : 'outline'}
                    size="sm"
                    className="text-xs"
                    disabled={updateStatus.isPending}
                    onClick={() => {
                      if (lead.status !== s.value) {
                        updateStatus.mutate({ id: lead.id, status: s.value });
                      }
                    }}
                  >
                    {s.label}
                  </Button>
                ))}
              </div>
            </div>
          </PermissionGuard>

          {/* Score */}
          <div className="rounded-lg border p-4">
            <ScoreBar score={lead.lead_score} />
          </div>

          {/* Meta */}
          <div className="rounded-lg border p-4 space-y-3">
            <h3 className="text-sm font-medium">Details</h3>
            <div className="space-y-2.5 text-sm">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Source</span>
                <span className="font-medium capitalize">{lead.source}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Created</span>
                <span className="font-medium">{new Date(lead.created_at).toLocaleDateString()}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Updated</span>
                <span className="font-medium">{new Date(lead.updated_at).toLocaleDateString()}</span>
              </div>
              {lead.qualified_at && (
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Qualified</span>
                  <span className="font-medium">{new Date(lead.qualified_at).toLocaleDateString()}</span>
                </div>
              )}
              {lead.last_contacted_at && (
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Last Contact</span>
                  <span className="font-medium">{new Date(lead.last_contacted_at).toLocaleDateString()}</span>
                </div>
              )}
            </div>
          </div>

          {/* Actions */}
          <div className="rounded-lg border p-4 space-y-4">
            <div>
              <h3 className="text-sm font-medium mb-2 text-muted-foreground uppercase text-[11px] tracking-wider">Communication</h3>
              <div className="space-y-2">
                <Button variant="outline" size="sm" className="w-full justify-start gap-2" disabled={!lead.email}>
                  <Mail className="h-3.5 w-3.5" />Send Email
                </Button>
                <Button variant="outline" size="sm" className="w-full justify-start gap-2" disabled={!lead.phone}>
                  <Phone className="h-3.5 w-3.5" />Call
                </Button>
              </div>
            </div>
            <div>
              <h3 className="text-sm font-medium mb-2 text-muted-foreground uppercase text-[11px] tracking-wider">CRM</h3>
              <div className="space-y-4">
                <LeadAssignmentWidget leadId={lead.id} assignedAdminId={lead.assigned_admin_id} />
                <LeadFollowUpWidget leadId={lead.id} />
                <div className="space-y-2">
                  <Button variant="outline" size="sm" className="w-full justify-start gap-2">
                    <Edit3 className="h-3.5 w-3.5" />Edit Details
                  </Button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </PageContainer>
  );
}
