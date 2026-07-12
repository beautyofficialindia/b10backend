import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { format } from 'date-fns';
import { useLeadNotes } from '../api';
import { LeadNoteForm } from './lead-note-form';
import { Skeleton } from '@/components/ui/skeleton';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { MessageSquareOff } from 'lucide-react';

interface NotesTabProps {
  leadId: string;
}

export const NotesTab: React.FC<NotesTabProps> = ({ leadId }) => {
  const { data: notes, isLoading, isError } = useLeadNotes(leadId);

  return (
    <div className="space-y-6">
      <LeadNoteForm leadId={leadId} />

      <div className="space-y-4">
        <h3 className="text-sm font-semibold tracking-tight">Recent Notes</h3>

        {isLoading && (
          <div className="space-y-4">
            {[1, 2].map((i) => (
              <div key={i} className="flex gap-4 p-4 rounded-lg border bg-card">
                <Skeleton className="h-10 w-10 rounded-full" />
                <div className="space-y-2 flex-1">
                  <Skeleton className="h-4 w-1/4" />
                  <Skeleton className="h-20 w-full" />
                </div>
              </div>
            ))}
          </div>
        )}

        {isError && (
          <div className="p-4 rounded-lg border border-destructive/50 bg-destructive/10 text-destructive text-sm text-center">
            Failed to load notes. Please try again.
          </div>
        )}

        {!isLoading && !isError && notes?.length === 0 && (
          <div className="p-8 rounded-lg border border-dashed text-center">
            <MessageSquareOff className="h-8 w-8 text-muted-foreground mx-auto mb-3 opacity-50" />
            <p className="text-sm font-medium">No notes yet</p>
            <p className="text-xs text-muted-foreground mt-1">Be the first to add a note to this lead.</p>
          </div>
        )}

        {!isLoading && !isError && notes && notes.length > 0 && (
          <div className="space-y-4">
            {notes.map((note) => {
              const authorName = note.author?.full_name || note.author?.username || 'Unknown User';
              const initials = authorName.substring(0, 2).toUpperCase();
              
              return (
                <div key={note.id} className="flex gap-4 p-4 rounded-lg border bg-card/50">
                  <Avatar className="h-10 w-10 border bg-background">
                    <AvatarFallback className="bg-primary/5 text-primary text-xs">
                      {initials}
                    </AvatarFallback>
                  </Avatar>
                  <div className="flex-1 space-y-1">
                    <div className="flex items-center justify-between">
                      <p className="text-sm font-medium">{authorName}</p>
                      <time className="text-xs text-muted-foreground" dateTime={note.created_at}>
                        {format(new Date(note.created_at), 'MMM d, yyyy h:mm a')}
                      </time>
                    </div>
                    <div className="text-sm text-foreground/90 prose prose-sm dark:prose-invert max-w-none pt-1">
                      <ReactMarkdown remarkPlugins={[remarkGfm]}>
                        {note.note}
                      </ReactMarkdown>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};
