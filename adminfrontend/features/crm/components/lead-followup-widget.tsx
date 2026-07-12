import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { CalendarClock, Clock } from 'lucide-react';
import { useLeadFollowUps } from '../api';
import { ScheduleFollowUpDialog } from './schedule-followup-dialog';
import { PermissionGuard } from '@/features/auth/components/permission-guard';
import { format } from 'date-fns';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';

interface LeadFollowUpWidgetProps {
  leadId: string;
}

export const LeadFollowUpWidget: React.FC<LeadFollowUpWidgetProps> = ({ leadId }) => {
  const { data: followUps, isLoading } = useLeadFollowUps(leadId);
  const [isDialogOpen, setIsDialogOpen] = useState(false);

  // Find the most imminent pending follow-up
  const pendingFollowUp = followUps
    ?.filter(f => f.status === 'pending')
    ?.sort((a, b) => new Date(a.scheduled_at).getTime() - new Date(b.scheduled_at).getTime())[0];

  return (
    <>
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-semibold flex items-center gap-2">
            <CalendarClock className="w-4 h-4 text-muted-foreground" />
            Upcoming Follow-up
          </CardTitle>
          <PermissionGuard permissions={['crm.add_leadfollowup']}>
            <Button variant="ghost" size="sm" onClick={() => setIsDialogOpen(true)}>
              Schedule
            </Button>
          </PermissionGuard>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="space-y-2 mt-2">
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-4 w-2/3" />
            </div>
          ) : pendingFollowUp ? (
            <div className="mt-2 space-y-3">
              <div className="flex justify-between items-start">
                <div>
                  <p className="text-sm font-medium">
                    {format(new Date(pendingFollowUp.scheduled_at), 'MMM d, yyyy')}
                  </p>
                  <p className="text-xs text-muted-foreground flex items-center gap-1 mt-0.5">
                    <Clock className="w-3 h-3" />
                    {format(new Date(pendingFollowUp.scheduled_at), 'h:mm a')}
                  </p>
                </div>
                <Badge variant="outline" className="capitalize text-xs">
                  {pendingFollowUp.followup_type}
                </Badge>
              </div>
              {pendingFollowUp.notes && (
                <p className="text-sm text-muted-foreground line-clamp-2">
                  {pendingFollowUp.notes}
                </p>
              )}
            </div>
          ) : (
            <div className="text-center py-4 text-muted-foreground">
              <CalendarClock className="w-8 h-8 mx-auto mb-2 opacity-20" />
              <p className="text-sm">No upcoming follow-ups</p>
            </div>
          )}
        </CardContent>
      </Card>

      <ScheduleFollowUpDialog 
        leadId={leadId}
        open={isDialogOpen}
        onOpenChange={setIsDialogOpen}
      />
    </>
  );
};
