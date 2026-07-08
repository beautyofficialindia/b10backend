import type { LeadStatus } from '../types';

export function getStatusVariant(status: string): 'active' | 'inactive' | 'pending' | 'error' {
  switch (status) {
    case 'qualified':
    case 'converted':
      return 'active';
    case 'lost':
    case 'disqualified':
      return 'error';
    case 'escalated':
      return 'pending';
    default:
      return 'inactive';
  }
}

export const statusOptions: { value: LeadStatus | ''; label: string }[] = [
  { value: '', label: 'All Statuses' },
  { value: 'gathering', label: 'Gathering' },
  { value: 'qualified', label: 'Qualified' },
  { value: 'disqualified', label: 'Disqualified' },
  { value: 'converted', label: 'Converted' },
  { value: 'escalated', label: 'Escalated' },
  { value: 'lost', label: 'Lost' },
];

export const sortOptions = [
  { value: '-created_at', label: 'Newest first' },
  { value: 'created_at', label: 'Oldest first' },
  { value: '-updated_at', label: 'Recently updated' },
];
