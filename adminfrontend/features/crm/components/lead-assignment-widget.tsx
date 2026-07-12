'use client';

import { useUserDetail } from '@/features/users';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { Button } from '@/components/ui/button';
import { UserPlus } from 'lucide-react';
import { LeadAssignmentDialog } from './lead-assignment-dialog';

interface LeadAssignmentWidgetProps {
  leadId: string;
  assignedAdminId?: string | null;
}

export function LeadAssignmentWidget({ leadId, assignedAdminId }: LeadAssignmentWidgetProps) {
  const { data: user, isLoading, isError } = useUserDetail(assignedAdminId ? parseInt(assignedAdminId) : 0);

  if (!assignedAdminId) {
    return (
      <div className="rounded-lg border p-4">
        <h3 className="text-sm font-medium mb-3">Assignment</h3>
        <div className="flex flex-col items-center justify-center py-6 text-center text-muted-foreground border-2 border-dashed rounded-lg mb-3">
          <UserPlus className="h-8 w-8 mb-2 opacity-20" />
          <p className="text-sm font-medium">Unassigned</p>
          <p className="text-xs">No one is working on this lead</p>
        </div>
        <LeadAssignmentDialog leadId={leadId} currentAssigneeId={assignedAdminId} />
      </div>
    );
  }

  return (
    <div className="rounded-lg border p-4">
      <h3 className="text-sm font-medium mb-3 flex items-center gap-2">
        Assignment
      </h3>
      
      {isLoading ? (
        <div className="flex items-center gap-3 mb-4">
          <Skeleton className="h-10 w-10 rounded-full shrink-0" />
          <div className="space-y-2 flex-1">
            <Skeleton className="h-4 w-2/3" />
            <Skeleton className="h-3 w-1/2" />
          </div>
        </div>
      ) : isError || !user?.data ? (
        <div className="flex items-center gap-3 mb-4 p-3 bg-destructive/10 text-destructive rounded-lg">
          <div className="flex-1 text-sm">Failed to load user</div>
        </div>
      ) : (
        <div className="flex items-start gap-3 mb-4 p-3 border rounded-lg bg-card">
          <Avatar className="h-10 w-10 shrink-0 border">
            <AvatarFallback className="text-xs font-semibold bg-primary/10 text-primary uppercase">
              {user.data.first_name?.[0] || ''}{user.data.last_name?.[0] || user.data.email[0]}
            </AvatarFallback>
          </Avatar>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-semibold truncate">
              {user.data.first_name} {user.data.last_name}
            </p>
            <p className="text-xs text-muted-foreground truncate mb-1">
              {user.data.email}
            </p>
            <Badge variant="secondary" className="text-[10px] capitalize font-medium">
              {user.data.groups?.[0] || 'User'}
            </Badge>
          </div>
        </div>
      )}

      <LeadAssignmentDialog 
        leadId={leadId} 
        currentAssigneeId={assignedAdminId} 
        trigger={
          <Button variant="outline" size="sm" className="w-full text-xs">
            Change Assignment
          </Button>
        }
      />
    </div>
  );
}
