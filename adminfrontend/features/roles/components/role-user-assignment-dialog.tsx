'use client';

import * as React from 'react';
import { useState, useMemo } from 'react';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Checkbox } from '@/components/ui/checkbox';
import { Search, Loader2 } from 'lucide-react';
import { toast } from 'sonner';
import { useAssignUsers, type RoleUser } from '@/features/roles';
import { useUsersList } from '@/features/users';
import { useDebounce } from '@/hooks/use-debounce';

interface RoleUserAssignmentDialogProps {
  roleId: number;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  existingUsers: RoleUser[];
}

export function RoleUserAssignmentDialog({ roleId, open, onOpenChange, existingUsers }: RoleUserAssignmentDialogProps) {
  const [search, setSearch] = useState('');
  const debouncedSearch = useDebounce(search, 300);
  const [selectedUserIds, setSelectedUserIds] = useState<Set<number>>(new Set());

  const assignMutation = useAssignUsers();

  const { data, isLoading } = useUsersList({
    page: 1,
    page_size: 50,
    search: debouncedSearch,
    ordering: 'username',
  });

  // Filter out users already in the role
  const existingUserIds = useMemo(() => new Set(existingUsers.map(u => u.id)), [existingUsers]);
  const assignableUsers = useMemo(() => {
    const userList = data?.data || [];
    return userList.filter(u => !existingUserIds.has(u.id));
  }, [data?.data, existingUserIds]);

  const { reset: resetAssignMutation } = assignMutation;

  const handleOpenChange = (newOpen: boolean) => {
    if (!newOpen) {
      setSearch('');
      setSelectedUserIds(new Set());
      resetAssignMutation();
    }
    onOpenChange(newOpen);
  };

  const toggleUser = (id: number) => {
    const next = new Set(selectedUserIds);
    if (next.has(id)) next.delete(id);
    else next.add(id);
    setSelectedUserIds(next);
  };

  const handleAssign = () => {
    if (selectedUserIds.size === 0) {
      toast.error('Please select at least one user');
      return;
    }

    assignMutation.mutate(
      { id: roleId, user_ids: Array.from(selectedUserIds) },
      {
        onSuccess: () => {
          toast.success(`Assigned ${selectedUserIds.size} user(s) successfully`);
          handleOpenChange(false);
        },
        onError: () => {
          toast.error('Failed to assign users');
        }
      }
    );
  };

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle>Assign Users to Role</DialogTitle>
          <DialogDescription>
            Search and select users to add them to this role.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-4">
          <div className="relative">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
            <input
              type="text"
              placeholder="Search users by name or email..."
              className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50 pl-9"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>

          <div className="h-64 overflow-y-auto rounded-md border p-2">
            {isLoading ? (
              <div className="flex h-full items-center justify-center text-muted-foreground">
                <Loader2 className="h-5 w-5 animate-spin" />
              </div>
            ) : assignableUsers.length === 0 ? (
              <div className="flex h-full items-center justify-center text-sm text-muted-foreground">
                {search ? 'No users found.' : 'Search for users to assign.'}
              </div>
            ) : (
              <div className="space-y-2">
                {assignableUsers.map(u => (
                  <label key={u.id} className="flex items-center gap-3 rounded p-2 hover:bg-muted cursor-pointer transition-colors">
                    <Checkbox 
                      checked={selectedUserIds.has(u.id)}
                      onCheckedChange={() => toggleUser(u.id)}
                    />
                    <div className="flex flex-col">
                      <span className="text-sm font-medium leading-none">
                        {u.first_name || u.last_name ? `${u.first_name} ${u.last_name}`.trim() : u.username}
                      </span>
                      <span className="text-xs text-muted-foreground mt-1">{u.email}</span>
                    </div>
                  </label>
                ))}
              </div>
            )}
          </div>
          <div className="text-xs text-muted-foreground">
            {selectedUserIds.size} user(s) selected
          </div>
        </div>

        <DialogFooter>
          <Button 
            type="button" 
            variant="outline" 
            onClick={() => handleOpenChange(false)}
            disabled={assignMutation.isPending}
          >
            Cancel
          </Button>
          <Button 
            type="button" 
            onClick={handleAssign}
            disabled={assignMutation.isPending || selectedUserIds.size === 0}
          >
            {assignMutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            Assign Users
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
