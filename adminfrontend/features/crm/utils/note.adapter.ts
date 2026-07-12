import { StickyNote } from 'lucide-react';
import type { LeadNote, TimelineItem } from '../types';

export function adaptNote(note: LeadNote): TimelineItem {
  const authorName = note.author?.full_name || note.author?.username || 'Unknown User';
  return {
    id: `note-${note.id}`,
    type: 'note',
    icon: StickyNote,
    title: 'Added a note',
    description: note.note, // Backend uses 'note'
    actor: authorName,
    timestamp: note.created_at,
    metadata: {
      author_id: note.author_id,
      author: note.author
    }
  };
}
