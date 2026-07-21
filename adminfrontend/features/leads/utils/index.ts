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

export const sourceOptions = [
  { value: '', label: 'All Sources' },
  { value: 'chatbot', label: 'Chatbot' },
  { value: 'website_contact_form', label: 'Website Contact Form' },
  { value: 'manual', label: 'Manual' },
  { value: 'api', label: 'API' },
  { value: 'website_service_request', label: 'Website Service Request' },
  { value: 'website_book_meeting', label: 'Website Book Meeting' },
  { value: 'website_partnership', label: 'Website Partnership' },
  { value: 'website_careers', label: 'Website Careers' },
];
