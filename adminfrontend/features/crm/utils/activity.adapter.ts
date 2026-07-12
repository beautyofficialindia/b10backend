import { ClipboardCheck, Mail, Calendar, Phone } from 'lucide-react';
import type { LeadActivity, TimelineItem } from '../types';

export function adaptActivity(activity: LeadActivity): TimelineItem {
  let icon = ClipboardCheck;
  let type: TimelineItem['type'] = 'activity';
  
  if (activity.activity_type.toLowerCase() === 'email') {
    icon = Mail;
    type = 'email';
  } else if (activity.activity_type.toLowerCase() === 'meeting') {
    icon = Calendar;
    type = 'meeting';
  } else if (activity.activity_type.toLowerCase() === 'call') {
    icon = Phone;
    type = 'phone';
  }

  return {
    id: `activity-${activity.id}`,
    type,
    icon,
    title: `Logged an activity: ${activity.activity_type.replace('_', ' ')}`,
    description: activity.notes || undefined,
    actor: 'System', // Backend doesn't store actor currently
    timestamp: activity.created_at,
  };
}
