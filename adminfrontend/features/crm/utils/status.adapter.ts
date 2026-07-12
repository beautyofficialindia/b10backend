import { ArrowRightLeft } from 'lucide-react';
import type { LeadStatusHistory, TimelineItem } from '../types';

export function adaptStatusHistory(history: LeadStatusHistory): TimelineItem {
  return {
    id: `status-${history.id}`,
    type: 'status',
    icon: ArrowRightLeft,
    title: `Changed status from ${history.old_status} to ${history.new_status}`,
    description: undefined,
    actor: 'System', // Backend doesn't store actor
    timestamp: history.changed_at,
    metadata: {
      old_status: history.old_status,
      new_status: history.new_status,
    }
  };
}
