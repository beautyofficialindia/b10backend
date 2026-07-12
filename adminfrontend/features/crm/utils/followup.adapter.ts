import { Clock } from 'lucide-react';
import type { LeadFollowUp, TimelineItem } from '../types';

export function adaptFollowUp(followup: LeadFollowUp): TimelineItem {
  return {
    id: `followup-${followup.id}`,
    type: 'followup',
    icon: Clock,
    title: `${followup.followup_type ? followup.followup_type.charAt(0).toUpperCase() + followup.followup_type.slice(1) : 'Follow up'} scheduled for ${new Date(followup.scheduled_at).toLocaleDateString()}`,
    description: followup.notes || undefined,
    actor: 'System',
    timestamp: followup.created_at,
    metadata: {
      status: followup.status,
      followup_type: followup.followup_type,
    }
  };
}
