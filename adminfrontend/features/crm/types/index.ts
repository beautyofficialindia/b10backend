import type { LeadStatus } from '@/features/leads/types';
import React from 'react';

export interface PipelineColumn {
  id: LeadStatus;
  title: string;
  color: string;
}

export const PIPELINE_COLUMNS: PipelineColumn[] = [
  { id: 'gathering', title: 'Gathering', color: 'bg-slate-500' },
  { id: 'qualified', title: 'Qualified', color: 'bg-blue-500' },
  { id: 'escalated', title: 'Escalated', color: 'bg-amber-500' },
  { id: 'converted', title: 'Converted', color: 'bg-emerald-500' },
  { id: 'lost', title: 'Lost', color: 'bg-red-500' },
];

export interface TimelineItem {
  id: string;
  type: 'activity' | 'followup' | 'status' | 'note' | 'assignment' | 'email' | 'meeting' | 'phone';
  icon: React.ElementType; // We'll map Lucide icons in the component
  title: string;
  description?: string;
  actor: string;
  timestamp: string;
  metadata?: Record<string, unknown>;
}

// Backend Schemas

export interface LeadActivity {
  id: string;
  lead: string;
  activity_type: string; 
  notes: string | null;
  created_at: string;
}

export interface LeadStatusHistory {
  id: string;
  lead: string;
  old_status: string;
  new_status: string;
  changed_at: string;
}

export interface LeadFollowUp {
  id: string;
  lead: string;
  scheduled_at: string;
  followup_type: 'call' | 'meeting' | 'email' | 'demo' | 'other';
  status: 'pending' | 'completed' | 'cancelled';
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface LeadNote {
  id: string;
  lead: string;
  note: string;
  author_id: string | null;
  author: {
    id: number;
    username: string;
    full_name: string;
  } | null;
  created_at: string;
}
