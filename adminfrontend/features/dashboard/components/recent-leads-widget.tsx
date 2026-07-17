"use client";

import { useRecentLeads } from "../hooks/use-dashboard";
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from "@/components/ui/card";
import { Loader2 } from "lucide-react";
import { DataTable, type Column } from "@/components/tables";
import type { Lead } from "../types";
import { cn } from "@/lib/utils";

const leadsColumns: Column<Lead>[] = [
  { key: 'full_name', header: 'Name', render: (row) => {
    const initials = (row.full_name || 'U').substring(0, 2).toUpperCase();
    return (
      <div className="flex items-center gap-3">
        <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-primary/20 text-xs font-semibold text-primary">
          {initials}
        </div>
        <div>
          <p className="text-sm font-medium">{row.full_name || '—'}</p>
          <p className="text-xs text-muted-foreground">{row.email || ''}</p>
        </div>
      </div>
    );
  }},
  { key: 'company_name', header: 'Company', render: (row) => <span className="font-medium text-muted-foreground">{row.company_name || '—'}</span> },
  { key: 'project_type', header: 'Project', render: (row) => <span className="font-medium text-muted-foreground">{row.project_type || '—'}</span> },
  { key: 'status', header: 'Status', render: (row) => {
    const statusMap = {
      gathering: { label: 'Gathering', color: 'bg-blue-500/10 text-blue-500 border-blue-500/20' },
      qualified: { label: 'Qualified', color: 'bg-green-500/10 text-green-500 border-green-500/20' },
      converted: { label: 'Converted', color: 'bg-orange-500/10 text-orange-500 border-orange-500/20' },
      lost: { label: 'Lost', color: 'bg-red-500/10 text-red-500 border-red-500/20' },
      escalated: { label: 'Escalated', color: 'bg-purple-500/10 text-purple-500 border-purple-500/20' },
    };
    const s = statusMap[row.status as keyof typeof statusMap] || statusMap.gathering;
    return (
      <span className={cn("px-2.5 py-1 rounded-md text-[11px] font-semibold tracking-wide uppercase border", s.color)}>
        {s.label}
      </span>
    );
  }},
  { key: 'created_at', header: 'Created', render: (row) => (
    <span className="text-xs font-medium text-muted-foreground">{new Date(row.created_at).toLocaleDateString()}</span>
  )},
];

export function RecentLeadsWidget() {
  const { data, isLoading, isError } = useRecentLeads(true);

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Recent Leads</CardTitle>
          <CardDescription>The latest leads generated across all channels.</CardDescription>
        </CardHeader>
        <CardContent className="flex justify-center py-10">
          <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
        </CardContent>
      </Card>
    );
  }

  if (isError) {
    return null;
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Recent Leads</CardTitle>
        <CardDescription>The latest leads generated across all channels.</CardDescription>
      </CardHeader>
      <CardContent>
        <DataTable
          columns={leadsColumns}
          data={data?.results || []}
          isLoading={false}
          onRowClick={() => {}}
        />
      </CardContent>
    </Card>
  );
}
