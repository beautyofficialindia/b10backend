'use client';

import type { Lead } from '@/features/leads/types';
import type { PipelineColumn as PipelineColumnType } from '../types';
import { PipelineCard } from './pipeline-card';
import { useDroppable } from '@dnd-kit/core';
import { cn } from '@/lib/utils';
import { ScrollArea } from '@/components/ui/scroll-area';

interface PipelineColumnProps {
  column: PipelineColumnType;
  leads: Lead[];
}

export function PipelineColumn({ column, leads }: PipelineColumnProps) {
  const { setNodeRef, isOver } = useDroppable({
    id: column.id,
  });

  return (
    <div className="flex flex-col min-w-[280px] w-[280px] shrink-0 lg:min-w-0 lg:w-auto lg:flex-1">
      {/* Column Header */}
      <div className="flex items-center gap-2 mb-3 px-1">
        <div className={cn('h-2.5 w-2.5 rounded-full', column.color)} />
        <h3 className="text-sm font-medium">{column.title}</h3>
        <span className="text-xs text-muted-foreground bg-muted px-1.5 py-0.5 rounded-full">
          {leads.length}
        </span>
      </div>

      {/* Drop zone */}
      <div
        ref={setNodeRef}
        className={cn(
          'flex-1 rounded-lg border border-dashed p-2 min-h-[200px] transition-colors',
          isOver ? 'border-primary bg-primary/5' : 'border-transparent bg-muted/30'
        )}
      >
        <ScrollArea className="h-[calc(100vh-280px)]">
          <div className="space-y-2 pr-2">
            {leads.length === 0 ? (
              <p className="text-xs text-muted-foreground text-center py-8">
                No leads
              </p>
            ) : (
              leads.map((lead) => <PipelineCard key={lead.id} lead={lead} />)
            )}
          </div>
        </ScrollArea>
      </div>
    </div>
  );
}
