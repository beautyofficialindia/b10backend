import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { PermissionGuard } from '@/features/auth/components/permission-guard';
import { useCreateLeadNote } from '../api';
import { toast } from 'sonner';
import { Loader2 } from 'lucide-react';
import { AxiosError } from 'axios';

const formSchema = z.object({
  note: z.string().trim().min(1, 'Note content is required').max(10000, 'Note is too long'),
});

export type LeadNoteFormData = z.infer<typeof formSchema>;

interface LeadNoteFormProps {
  leadId: string;
}

export const LeadNoteForm: React.FC<LeadNoteFormProps> = ({ leadId }) => {
  const { mutate: createNote, isPending } = useCreateLeadNote(leadId);

  const { register, handleSubmit, reset, formState: { errors } } = useForm<LeadNoteFormData>({
    resolver: zodResolver(formSchema),
    defaultValues: { note: '' },
  });

  const onSubmit = (data: LeadNoteFormData) => {
    createNote(data, {
      onSuccess: () => {
        toast.success('Note added successfully');
        reset();
      },
      onError: (error: Error) => {
        const axiosError = error as AxiosError<{ detail?: string }>;
        toast.error(axiosError?.response?.data?.detail || 'Failed to add note');
      },
    });
  };

  return (
    <PermissionGuard permissions={['crm.add_leadnote']} fallback={null}>
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <div className="space-y-2">
          <Textarea 
            {...register('note')}
            placeholder="Write a note (Markdown is supported)..."
            className="min-h-[120px] resize-y"
            disabled={isPending}
          />
          {errors.note && (
            <p className="text-sm font-medium text-destructive">{errors.note.message}</p>
          )}
        </div>
        <div className="flex justify-end">
          <Button type="submit" disabled={isPending}>
            {isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            Add Note
          </Button>
        </div>
      </form>
    </PermissionGuard>
  );
};
