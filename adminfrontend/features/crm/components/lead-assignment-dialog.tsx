'use client';

import { useState } from 'react';
import { 
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { Search, Loader2, UserCheck, AlertCircle } from 'lucide-react';
import { useDebounce } from '@/hooks/use-debounce';
import { useUsersList } from '@/features/users';
import { useAssignLead } from '../api';
import { PermissionGuard } from '@/features/auth';
import { toast } from 'sonner';

interface LeadAssignmentDialogProps {
  leadId: string;
  currentAssigneeId?: string | null;
  trigger?: React.ReactElement;
  onSuccess?: () => void;
}

export function LeadAssignmentDialog({ leadId, currentAssigneeId, trigger, onSuccess }: LeadAssignmentDialogProps) {
  const [open, setOpen] = useState(false);
  const [search, setSearch] = useState('');
  const debouncedSearch = useDebounce(search, 300);

  const { data, isLoading, isError } = useUsersList({
    page: 1,
    search: debouncedSearch,
  });

  const { mutate: assignLead, isPending } = useAssignLead(leadId);

  const handleAssign = (userId: string) => {
    assignLead(userId, {
      onSuccess: () => {
        toast.success('Lead assigned successfully');
        setOpen(false);
        setSearch('');
        onSuccess?.();
      },
      onError: () => {
        toast.error('Failed to assign lead');
      }
    });
  };

  const users = data?.data || [];

  return (
    <PermissionGuard permissions={["leads.change_lead"]}>
      <Dialog open={open} onOpenChange={(val) => {
        setOpen(val);
        if (!val) setSearch('');
      }}>
        <DialogTrigger render={
          trigger || (
            <Button variant="outline" size="sm" className="w-full justify-start gap-2">
              <UserCheck className="h-3.5 w-3.5" /> Assign Lead
            </Button>
          )
        } />
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Assign Lead</DialogTitle>
          </DialogHeader>

          <div className="space-y-4">
            <div className="relative">
              <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search users by name or email..."
                className="pl-9"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
            </div>

            <div className="max-h-[300px] overflow-y-auto space-y-2 pr-1">
              {isLoading ? (
                <div className="py-8 text-center text-muted-foreground flex flex-col items-center justify-center">
                  <Loader2 className="h-6 w-6 animate-spin mb-2" />
                  <p className="text-sm">Searching users...</p>
                </div>
              ) : isError ? (
                <div className="py-8 text-center text-destructive flex flex-col items-center justify-center">
                  <AlertCircle className="h-6 w-6 mb-2" />
                  <p className="text-sm">Failed to load users.</p>
                </div>
              ) : users.length === 0 ? (
                <div className="py-8 text-center text-muted-foreground">
                  <p className="text-sm">No users found.</p>
                </div>
              ) : (
                users.map(user => {
                  const isCurrent = user.id.toString() === currentAssigneeId?.toString();
                  return (
                    <div 
                      key={user.id}
                      className="flex items-center justify-between p-3 rounded-lg border bg-card hover:bg-accent transition-colors"
                    >
                      <div className="flex items-center gap-3">
                        <Avatar className="h-9 w-9">
                          <AvatarFallback className="text-xs uppercase bg-primary/10 text-primary">
                            {user.first_name?.[0] || ''}{user.last_name?.[0] || user.email[0]}
                          </AvatarFallback>
                        </Avatar>
                        <div className="flex flex-col">
                          <p className="text-sm font-medium">
                            {user.first_name} {user.last_name}
                          </p>
                          <p className="text-[11px] text-muted-foreground">
                            {user.email}
                          </p>
                        </div>
                        <Badge variant="secondary" className="ml-2 text-[10px] capitalize">
                          {user.groups?.[0] || 'User'}
                        </Badge>
                      </div>
                      
                      <Button
                        size="sm"
                        variant={isCurrent ? "secondary" : "default"}
                        disabled={isCurrent || isPending}
                        onClick={() => handleAssign(user.id.toString())}
                        className="h-8"
                      >
                        {isCurrent ? 'Current' : 'Assign'}
                      </Button>
                    </div>
                  );
                })
              )}
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </PermissionGuard>
  );
}
