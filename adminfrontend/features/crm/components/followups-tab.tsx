import React, { useState } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { CalendarClock, CheckCircle2, Clock, XCircle, Edit2, MoreVertical } from 'lucide-react';
import { useLeadFollowUps, useCompleteFollowUp, useCancelFollowUp } from '../api';
import { format } from 'date-fns';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { PermissionGuard } from '@/features/auth/components/permission-guard';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from '@/components/ui/dropdown-menu';
import { EditFollowUpDialog } from './edit-followup-dialog';
import { toast } from 'sonner';
import type { LeadFollowUp } from '../types';

interface FollowupsTabProps {
  leadId: string;
}

export const FollowupsTab: React.FC<FollowupsTabProps> = ({ leadId }) => {
  const { data: followUps, isLoading } = useLeadFollowUps(leadId);
  const { mutate: completeFollowUp } = useCompleteFollowUp(leadId);
  const { mutate: cancelFollowUp } = useCancelFollowUp(leadId);
  const [editingFollowup, setEditingFollowup] = useState<LeadFollowUp | null>(null);

  if (isLoading) {
    return (
      <div className="space-y-4 mt-6">
        <Skeleton className="h-[100px] w-full" />
        <Skeleton className="h-[100px] w-full" />
      </div>
    );
  }

  const upcoming = followUps?.filter(f => f.status === 'pending') || [];
  const completed = followUps?.filter(f => f.status === 'completed') || [];
  const cancelled = followUps?.filter(f => f.status === 'cancelled') || [];

  const handleComplete = (id: string) => {
    completeFollowUp(id, {
      onSuccess: () => toast.success('Follow-up completed')
    });
  };

  const handleCancel = (id: string) => {
    cancelFollowUp(id, {
      onSuccess: () => toast.success('Follow-up cancelled')
    });
  };

  const renderFollowUpCard = (f: LeadFollowUp, isPending: boolean = false) => (
    <Card key={f.id} className="mb-4 overflow-hidden border-l-4" style={{
      borderLeftColor: isPending ? 'hsl(var(--primary))' : f.status === 'completed' ? 'hsl(var(--emerald-500))' : 'hsl(var(--muted))'
    }}>
      <CardContent className="p-4 flex gap-4">
        <div className="mt-1">
          {isPending ? (
            <CalendarClock className="h-5 w-5 text-primary" />
          ) : f.status === 'completed' ? (
            <CheckCircle2 className="h-5 w-5 text-emerald-500" />
          ) : (
            <XCircle className="h-5 w-5 text-muted-foreground" />
          )}
        </div>
        <div className="flex-1">
          <div className="flex justify-between items-start">
            <div>
              <p className="font-semibold">{format(new Date(f.scheduled_at), 'MMMM d, yyyy')}</p>
              <div className="flex items-center gap-3 mt-1 text-sm text-muted-foreground">
                <span className="flex items-center gap-1">
                  <Clock className="h-3.5 w-3.5" />
                  {format(new Date(f.scheduled_at), 'h:mm a')}
                </span>
                <Badge variant="secondary" className="capitalize text-[10px]">{f.followup_type}</Badge>
              </div>
            </div>
            
            {isPending && (
              <PermissionGuard permissions={['crm.change_leadfollowup']}>
                <DropdownMenu>
                  <DropdownMenuTrigger className="h-8 w-8 inline-flex items-center justify-center rounded-md hover:bg-accent hover:text-accent-foreground transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring">
                    <MoreVertical className="h-4 w-4" />
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end">
                    <DropdownMenuItem onClick={() => setEditingFollowup(f)}>
                      <Edit2 className="h-4 w-4 mr-2" /> Edit
                    </DropdownMenuItem>
                    <DropdownMenuItem onClick={() => handleComplete(f.id)}>
                      <CheckCircle2 className="h-4 w-4 mr-2 text-emerald-500" /> Complete
                    </DropdownMenuItem>
                    <DropdownMenuItem onClick={() => handleCancel(f.id)}>
                      <XCircle className="h-4 w-4 mr-2 text-destructive" /> Cancel
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              </PermissionGuard>
            )}
          </div>
          {f.notes && (
            <div className="mt-3 text-sm bg-muted/50 p-3 rounded-md">
              {f.notes}
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );

  return (
    <div className="mt-6 space-y-8">
      {editingFollowup && (
        <EditFollowUpDialog 
          leadId={leadId}
          followup={editingFollowup}
          open={!!editingFollowup}
          onOpenChange={(open) => !open && setEditingFollowup(null)}
        />
      )}

      <div>
        <h3 className="font-semibold mb-4 text-lg">Upcoming</h3>
        {upcoming.length > 0 ? (
          upcoming.map(f => renderFollowUpCard(f, true))
        ) : (
          <p className="text-sm text-muted-foreground">No upcoming follow-ups scheduled.</p>
        )}
      </div>

      {(completed.length > 0 || cancelled.length > 0) && (
        <div>
          <h3 className="font-semibold mb-4 text-lg">Past Follow-ups</h3>
          {[...completed, ...cancelled]
            .sort((a, b) => new Date(b.scheduled_at).getTime() - new Date(a.scheduled_at).getTime())
            .map(f => renderFollowUpCard(f, false))}
        </div>
      )}
    </div>
  );
};
