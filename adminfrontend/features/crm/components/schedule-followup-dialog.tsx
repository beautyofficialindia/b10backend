import React from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui/dialog';
import { FollowUpForm, FollowUpFormData } from './followup-form';
import { useCreateFollowUp } from '../api';
import { toast } from 'sonner';

interface ScheduleFollowUpDialogProps {
  leadId: string;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export const ScheduleFollowUpDialog: React.FC<ScheduleFollowUpDialogProps> = ({ leadId, open, onOpenChange }) => {
  const { mutateAsync: createFollowUp, isPending } = useCreateFollowUp(leadId);

  const handleSubmit = async (data: FollowUpFormData) => {
    try {
      // Combine date and time into ISO string
      const scheduledAt = new Date(`${data.date}T${data.time}`).toISOString();
      
      await createFollowUp({
        scheduled_at: scheduledAt,
        followup_type: data.followup_type,
        notes: data.notes,
        status: 'pending',
      });
      
      toast.success('Follow-up scheduled successfully');
      onOpenChange(false);
    } catch (error) {
      toast.error('Failed to schedule follow-up');
      console.error(error);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Schedule Follow-up</DialogTitle>
          <DialogDescription>
            Set a date and time for your next touchpoint.
          </DialogDescription>
        </DialogHeader>
        
        <FollowUpForm 
          onSubmit={handleSubmit}
          isSubmitting={isPending}
        />
      </DialogContent>
    </Dialog>
  );
};
