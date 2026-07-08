import type { LeadStatus } from '@/features/leads/types';

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
