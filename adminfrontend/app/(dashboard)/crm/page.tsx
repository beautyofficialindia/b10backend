'use client';

import { useState } from 'react';
import { DndContext, DragOverlay, closestCenter, type DragEndEvent, type DragStartEvent } from '@dnd-kit/core';
import { PageContainer, PageHeader } from '@/components/layout';
import { ErrorState } from '@/components/common';
import { Skeleton } from '@/components/ui/skeleton';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { RefreshCw, Search } from 'lucide-react';
import {
  PipelineColumn,
  PipelineCard,
  usePipelineLeads,
  useMoveLeadStatus,
  getColumnLeads,
  PIPELINE_COLUMNS,
} from '@/features/crm';
import type { Lead, LeadStatus } from '@/features/leads/types';
import { useDebounce } from '@/hooks/use-debounce';
import { MIN_SEARCH_LENGTH } from '@/lib/constants/search';

export default function CRMPage() {
  const [search, setSearch] = useState('');
  const debouncedSearch = useDebounce(search, 300);
  const effectiveSearch = debouncedSearch.length >= MIN_SEARCH_LENGTH ? debouncedSearch : '';
  const { data: leads, isLoading, isError, refetch, isFetching } = usePipelineLeads(effectiveSearch || undefined);
  const moveStatus = useMoveLeadStatus();
  const [activeCard, setActiveCard] = useState<Lead | null>(null);

  const handleDragStart = (event: DragStartEvent) => {
    const lead = (event.active.data.current as { lead: Lead })?.lead;
    if (lead) setActiveCard(lead);
  };

  const handleDragEnd = (event: DragEndEvent) => {
    setActiveCard(null);
    const { active, over } = event;
    if (!over) return;

    const leadId = active.id as string;
    const newStatus = over.id as LeadStatus;

    // Find the lead
    const lead = leads?.find((l) => l.id === leadId);
    if (!lead || lead.status === newStatus) return;

    moveStatus.mutate({ id: leadId, status: newStatus });
  };

  return (
    <PageContainer className="!space-y-4">
      <PageHeader title="CRM Pipeline" description="Drag leads between stages to update their status">
        <Button
          variant="outline"
          size="sm"
          onClick={() => refetch()}
          disabled={isFetching}
          className="gap-1.5"
        >
          <RefreshCw className={`h-3.5 w-3.5 ${isFetching ? 'animate-spin' : ''}`} />
          Refresh
        </Button>
      </PageHeader>

      {/* Search */}
      <div className="relative max-w-xs">
        <Search className="absolute left-2.5 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
        <Input
          type="search"
          placeholder="Search leads..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="pl-8 h-9"
        />
      </div>

      {/* Pipeline */}
      {isLoading ? (
        <div className="flex gap-4 overflow-x-auto pb-4">
          {PIPELINE_COLUMNS.map((col) => (
            <div key={col.id} className="min-w-[280px] flex-1 space-y-3">
              <Skeleton className="h-5 w-24" />
              <Skeleton className="h-[200px] w-full rounded-lg" />
            </div>
          ))}
        </div>
      ) : isError ? (
        <ErrorState message="Failed to load pipeline" onRetry={() => refetch()} />
      ) : leads ? (
        <DndContext
          collisionDetection={closestCenter}
          onDragStart={handleDragStart}
          onDragEnd={handleDragEnd}
        >
          <div className="flex gap-4 overflow-x-auto pb-4">
            {PIPELINE_COLUMNS.map((column) => (
              <PipelineColumn
                key={column.id}
                column={column}
                leads={getColumnLeads(leads, column)}
              />
            ))}
          </div>

          <DragOverlay>
            {activeCard ? (
              <div className="w-[264px] opacity-90">
                <PipelineCard lead={activeCard} />
              </div>
            ) : null}
          </DragOverlay>
        </DndContext>
      ) : null}
    </PageContainer>
  );
}
