import React, { useState } from 'react';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import { CalendarClock, CheckCircle2, Edit2 } from 'lucide-react';
import { useLeadFollowUps, useCompleteFollowUp } from '../api';
import { EditFollowUpDialog } from './edit-followup-dialog';
import { format, isToday, isTomorrow, isPast } from 'date-fns';
import { PermissionGuard } from '@/features/auth/components/permission-guard';
import { toast } from 'sonner';

interface PendingFollowUpBannerProps {
  leadId: string;
}

export const PendingFollowUpBanner: React.FC<PendingFollowUpBannerProps> = ({ leadId }) => {
  const { data: followUps } = useLeadFollowUps(leadId);
  const { mutate: completeFollowUp, isPending: isCompleting } = useCompleteFollowUp(leadId);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);

  const pendingFollowUp = followUps
    ?.filter(f => f.status === 'pending')
    ?.sort((a, b) => new Date(a.scheduled_at).getTime() - new Date(b.scheduled_at).getTime())[0];

  if (!pendingFollowUp) return null;

  const scheduledDate = new Date(pendingFollowUp.scheduled_at);
  const isOverdue = isPast(scheduledDate) && !isToday(scheduledDate);
  
  let dateText = format(scheduledDate, 'MMM d, yyyy');
  if (isToday(scheduledDate)) dateText = 'Today';
  else if (isTomorrow(scheduledDate)) dateText = 'Tomorrow';

  return (
    <>
      <Alert variant={isOverdue ? 'destructive' : 'default'} className="mb-6 border-l-4">
        <CalendarClock className="h-5 w-5" />
        <AlertTitle className="flex items-center gap-2">
          Pending Follow-up
          <span className="text-xs font-normal opacity-80 uppercase tracking-wider bg-background/50 px-2 rounded-md">
            {pendingFollowUp.followup_type}
          </span>
        </AlertTitle>
        <AlertDescription className="mt-2 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="text-sm">
            <span className="font-semibold">{dateText}</span> at {format(scheduledDate, 'h:mm a')}
            {pendingFollowUp.notes && (
              <span className="block mt-1 opacity-90 line-clamp-1">{pendingFollowUp.notes}</span>
            )}
          </div>
          
          <PermissionGuard permissions={['crm.change_leadfollowup']}>
            <div className="flex items-center gap-2 shrink-0">
              <Button 
                variant="outline" 
                size="sm" 
                className="h-8"
                onClick={() => setIsEditDialogOpen(true)}
              >
                <Edit2 className="w-4 h-4 mr-1" />
                Edit
              </Button>
              <Button 
                variant="outline" 
                size="sm" 
                className="h-8 hover:bg-emerald-500 hover:text-white"
                disabled={isCompleting}
                onClick={() => {
                  completeFollowUp(pendingFollowUp.id, {
                    onSuccess: () => toast.success('Follow-up completed')
                  });
                }}
              >
                <CheckCircle2 className="w-4 h-4 mr-1" />
                Complete
              </Button>
            </div>
          </PermissionGuard>
        </AlertDescription>
      </Alert>

      <EditFollowUpDialog 
        leadId={leadId}
        followup={pendingFollowUp}
        open={isEditDialogOpen}
        onOpenChange={setIsEditDialogOpen}
      />
    </>
  );
};
