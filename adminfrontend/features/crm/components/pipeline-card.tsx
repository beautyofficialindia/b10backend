'use client';

import Link from 'next/link';
import type { Lead } from '@/features/leads/types';
import { Building2 } from 'lucide-react';
import { useDraggable } from '@dnd-kit/core';
import { cn } from '@/lib/utils';

interface PipelineCardProps {
  lead: Lead;
}

export function PipelineCard({ lead }: PipelineCardProps) {
  const { attributes, listeners, setNodeRef, transform, isDragging } = useDraggable({
    id: lead.id,
    data: { lead },
  });

  const style = transform
    ? { transform: `translate(${transform.x}px, ${transform.y}px)` }
    : undefined;

  return (
    <div
      ref={setNodeRef}
      style={style}
      {...listeners}
      {...attributes}
      className={cn(
        'rounded-lg border bg-card p-3 shadow-sm cursor-grab active:cursor-grabbing transition-shadow hover:shadow-md',
        isDragging && 'opacity-50 shadow-lg ring-2 ring-primary/20'
      )}
    >
      <Link href={`/leads/${lead.id}`} className="block" onClick={(e) => e.stopPropagation()}>
        <p className="text-sm font-medium truncate">{lead.full_name || 'Anonymous'}</p>
        {lead.company_name && (
          <p className="flex items-center gap-1 text-xs text-muted-foreground mt-1 truncate">
            <Building2 className="h-3 w-3 shrink-0" />
            {lead.company_name}
          </p>
        )}
        <div className="flex items-center justify-between mt-2">
          {lead.project_type && (
            <span className="text-[10px] text-muted-foreground bg-muted px-1.5 py-0.5 rounded truncate max-w-[60%]">
              {lead.project_type}
            </span>
          )}
          <span className="text-xs text-muted-foreground ml-auto">
            {new Date(lead.created_at).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })}
          </span>
        </div>
      </Link>
    </div>
  );
}
