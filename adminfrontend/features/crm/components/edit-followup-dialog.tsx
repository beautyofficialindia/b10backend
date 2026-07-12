import React from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui/dialog';
import { FollowUpForm, FollowUpFormData } from './followup-form';
import { useUpdateFollowUp } from '../api';
import type { LeadFollowUp } from '../types';
import { toast } from 'sonner';

interface EditFollowUpDialogProps {
  leadId: string;
  followup: LeadFollowUp;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export const EditFollowUpDialog: React.FC<EditFollowUpDialogProps> = ({ leadId, followup, open, onOpenChange }) => {
  const { mutateAsync: updateFollowUp, isPending } = useUpdateFollowUp(leadId);

  // Parse existing scheduled_at into date and time strings
  const scheduledDate = new Date(followup.scheduled_at);
  const dateStr = scheduledDate.toISOString().split('T')[0];
  const timeStr = scheduledDate.toTimeString().slice(0, 5);

  const initialData: Partial<FollowUpFormData> = {
    date: dateStr,
    time: timeStr,
    followup_type: followup.followup_type,
    notes: followup.notes || '',
  };

  const handleSubmit = async (data: FollowUpFormData) => {
    try {
      const scheduledAt = new Date(`${data.date}T${data.time}`).toISOString();
      
      await updateFollowUp({
        id: followup.id,
        data: {
          scheduled_at: scheduledAt,
          followup_type: data.followup_type,
          notes: data.notes,
        }
      });
      
      toast.success('Follow-up updated successfully');
      onOpenChange(false);
    } catch (error) {
      toast.error('Failed to update follow-up');
      console.error(error);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Edit Follow-up</DialogTitle>
          <DialogDescription>
            Update the date, time, or details of this follow-up.
          </DialogDescription>
        </DialogHeader>
        
        <FollowUpForm 
          initialData={initialData}
          onSubmit={handleSubmit}
          isSubmitting={isPending}
        />
      </DialogContent>
    </Dialog>
  );
};
