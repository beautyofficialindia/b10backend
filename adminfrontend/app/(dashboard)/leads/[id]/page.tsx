'use client';

import { use } from 'react';
import { useRouter } from 'next/navigation';
import { PageContainer } from '@/components/layout';
import { StatusBadge, ErrorState } from '@/components/common';
import { Skeleton } from '@/components/ui/skeleton';
import { Button } from '@/components/ui/button';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs';
import { ArrowLeft, Mail, Phone, Building2, Clock, Target, Briefcase, DollarSign, FileText, MessageSquare } from 'lucide-react';
import { useLeadDetail, useUpdateLeadStatus, type LeadStatus } from '@/features/leads';

function getStatusVariant(status: string): 'active' | 'inactive' | 'pending' | 'error' {
  switch (status) {
    case 'qualified': case 'converted': return 'active';
    case 'lost': case 'disqualified': return 'error';
    case 'escalated': return 'pending';
    default: return 'inactive';
  }
}

const statusActions: { value: LeadStatus; label: string }[] = [
  { value: 'gathering', label: 'Gathering' },
  { value: 'qualified', label: 'Qualified' },
  { value: 'converted', label: 'Converted' },
  { value: 'escalated', label: 'Escalated' },
  { value: 'lost', label: 'Lost' },
];

function InfoRow({ icon: Icon, label, value }: { icon: React.ElementType; label: string; value: string | null | undefined }) {
  if (!value) return null;
  return (
    <div className="flex items-start gap-3 py-2.5">
      <Icon className="h-4 w-4 text-muted-foreground mt-0.5 shrink-0" />
      <div className="min-w-0">
        <p className="text-xs text-muted-foreground">{label}</p>
        <p className="text-sm font-medium break-words">{value}</p>
      </div>
    </div>
  );
}

export default function LeadDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const router = useRouter();
  const { data: lead, isLoading, isError, refetch } = useLeadDetail(id);
  const updateStatus = useUpdateLeadStatus();

  if (isLoading) {
    return (
      <PageContainer>
        <Skeleton className="h-8 w-48 mb-6" />
        <div className="rounded-xl border bg-card p-6 space-y-4">
          <Skeleton className="h-6 w-64" />
          <Skeleton className="h-4 w-48" />
          <Skeleton className="h-4 w-32" />
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
      {/* Back button */}
      <Button variant="ghost" size="sm" className="gap-1.5 -ml-2 mb-2" onClick={() => router.push('/leads')}>
        <ArrowLeft className="h-3.5 w-3.5" />
        Back to Leads
      </Button>

      {/* Summary Card */}
      <div className="rounded-xl border bg-card p-5 shadow-sm">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
          <div className="min-w-0">
            <div className="flex items-center gap-3">
              <h1 className="text-xl font-semibold truncate">
                {lead.full_name || 'Anonymous Lead'}
              </h1>
              <StatusBadge status={getStatusVariant(lead.status)} label={lead.status} />
            </div>
            <div className="flex flex-wrap items-center gap-x-4 gap-y-1 mt-2 text-sm text-muted-foreground">
              {lead.email && (
                <span className="flex items-center gap-1.5"><Mail className="h-3.5 w-3.5" />{lead.email}</span>
              )}
              {lead.phone && (
                <span className="flex items-center gap-1.5"><Phone className="h-3.5 w-3.5" />{lead.phone}</span>
              )}
              {lead.company_name && (
                <span className="flex items-center gap-1.5"><Building2 className="h-3.5 w-3.5" />{lead.company_name}</span>
              )}
            </div>
          </div>

          {/* Score */}
          <div className="flex items-center gap-3 shrink-0">
            <div className="text-center">
              <p className="text-2xl font-bold">{lead.lead_score}</p>
              <p className="text-xs text-muted-foreground">Score</p>
            </div>
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
              <TabsTrigger value="activity">Activity</TabsTrigger>
              <TabsTrigger value="notes">Notes</TabsTrigger>
              <TabsTrigger value="conversation">Conversation</TabsTrigger>
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
                  <p className="text-sm text-muted-foreground whitespace-pre-wrap">{lead.requirements}</p>
                </div>
              )}

              {/* Contact */}
              <div className="rounded-lg border p-4">
                <h3 className="text-sm font-medium mb-2">Contact Information</h3>
                <div className="grid sm:grid-cols-2 gap-x-6">
                  <InfoRow icon={Mail} label="Email" value={lead.email} />
                  <InfoRow icon={Phone} label="Phone" value={lead.phone} />
                  <InfoRow icon={Building2} label="Company" value={lead.company_name} />
                  <InfoRow icon={Target} label="Source" value={lead.source} />
                </div>
              </div>
            </TabsContent>

            <TabsContent value="activity" className="mt-4">
              <div className="rounded-lg border p-8 text-center">
                <FileText className="h-8 w-8 text-muted-foreground mx-auto mb-3" />
                <p className="text-sm font-medium">Activity Timeline</p>
                <p className="text-xs text-muted-foreground mt-1">Coming soon</p>
              </div>
            </TabsContent>

            <TabsContent value="notes" className="mt-4">
              <div className="rounded-lg border p-8 text-center">
                <FileText className="h-8 w-8 text-muted-foreground mx-auto mb-3" />
                <p className="text-sm font-medium">Notes</p>
                <p className="text-xs text-muted-foreground mt-1">Coming soon</p>
              </div>
            </TabsContent>

            <TabsContent value="conversation" className="mt-4">
              {lead.conversation && lead.conversation.messages.length > 0 ? (
                <div className="rounded-lg border p-4 space-y-3 max-h-[500px] overflow-y-auto">
                  {lead.conversation.messages.map((msg, i) => (
                    <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                      <div className={`rounded-lg px-3 py-2 max-w-[80%] text-sm ${
                        msg.role === 'user'
                          ? 'bg-primary text-primary-foreground'
                          : 'bg-muted'
                      }`}>
                        {msg.content}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="rounded-lg border p-8 text-center">
                  <MessageSquare className="h-8 w-8 text-muted-foreground mx-auto mb-3" />
                  <p className="text-sm font-medium">No conversation</p>
                  <p className="text-xs text-muted-foreground mt-1">No chat history available</p>
                </div>
              )}
            </TabsContent>
          </Tabs>
        </div>

        {/* Sidebar */}
        <div className="space-y-4">
          {/* Status */}
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

          {/* Meta */}
          <div className="rounded-lg border p-4 space-y-3">
            <h3 className="text-sm font-medium">Details</h3>
            <div className="space-y-2.5 text-sm">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Score</span>
                <span className="font-medium">{lead.lead_score}/100</span>
              </div>
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
            </div>
          </div>

          {/* Actions */}
          <div className="rounded-lg border p-4 space-y-2">
            <h3 className="text-sm font-medium mb-2">Actions</h3>
            {lead.email && (
              <a href={`mailto:${lead.email}`} className="w-full">
                <Button variant="outline" size="sm" className="w-full justify-start gap-2">
                  <Mail className="h-3.5 w-3.5" />Send Email
                </Button>
              </a>
            )}
            {lead.phone && (
              <a href={`tel:${lead.phone}`} className="w-full">
                <Button variant="outline" size="sm" className="w-full justify-start gap-2">
                  <Phone className="h-3.5 w-3.5" />Call
                </Button>
              </a>
            )}
          </div>
        </div>
      </div>
    </PageContainer>
  );
}
