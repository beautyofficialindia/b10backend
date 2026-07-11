'use client';

import * as React from 'react';
import { Check, ChevronsUpDown, X, Loader2 } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { Command, CommandEmpty, CommandGroup, CommandInput, CommandItem, CommandList } from '@/components/ui/command';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { Badge } from '@/components/ui/badge';
import { useRolesList } from '@/features/roles';

interface RoleSelectorProps {
  value?: string[];
  onChange: (value: string[]) => void;
  disabled?: boolean;
}

export function RoleSelector({ value = [], onChange, disabled = false }: RoleSelectorProps) {
  const [open, setOpen] = React.useState(false);
  const { data, isLoading, isError } = useRolesList({ page_size: 100 });

  const roles = data?.data || [];
  
  const handleSelect = (currentValue: string) => {
    if (value.includes(currentValue)) {
      onChange(value.filter(item => item !== currentValue));
    } else {
      onChange([...value, currentValue]);
    }
  };

  const handleRemove = (e: React.MouseEvent, roleToRemove: string) => {
    e.stopPropagation();
    onChange(value.filter(item => item !== roleToRemove));
  };

  return (
    <div className="space-y-2">
      <Popover open={open} onOpenChange={setOpen}>
        <PopoverTrigger
          render={
            <Button
              variant="outline"
              role="combobox"
              aria-expanded={open}
              className="w-full justify-between h-auto min-h-10 py-2"
              disabled={disabled}
            />
          }
        >
          <div className="flex flex-wrap gap-1.5 items-center w-full">
            {value.length === 0 && <span className="text-muted-foreground font-normal">Select roles...</span>}
            {value.map((val) => (
              <Badge key={val} variant="secondary" className="mr-1 gap-1 flex items-center pr-1.5 font-normal">
                {val}
                <div
                  role="button"
                  className="h-3 w-3 rounded-full hover:bg-muted-foreground/20 flex items-center justify-center cursor-pointer"
                  onClick={(e) => handleRemove(e, val)}
                >
                  <X className="h-2 w-2" />
                </div>
              </Badge>
            ))}
          </div>
          <ChevronsUpDown className="h-4 w-4 shrink-0 opacity-50 ml-2" />
        </PopoverTrigger>
        <PopoverContent className="w-[400px] p-0" align="start">
          <Command>
            <CommandInput placeholder="Search roles..." />
            <CommandList>
              <CommandEmpty>
                {isLoading ? (
                  <div className="flex items-center justify-center p-4 gap-2 text-sm text-muted-foreground">
                    <Loader2 className="h-4 w-4 animate-spin" /> Loading roles...
                  </div>
                ) : isError ? (
                  <div className="p-4 text-sm text-destructive">Failed to load roles.</div>
                ) : (
                  "No roles found."
                )}
              </CommandEmpty>
              {!isLoading && !isError && (
                <CommandGroup>
                  {roles.map((role) => (
                    <CommandItem
                      key={role.name}
                      value={role.name}
                      onSelect={() => handleSelect(role.name)}
                    >
                      <Check
                        className={cn(
                          "mr-2 h-4 w-4",
                          value.includes(role.name) ? "opacity-100" : "opacity-0"
                        )}
                      />
                      {role.name}
                    </CommandItem>
                  ))}
                </CommandGroup>
              )}
            </CommandList>
          </Command>
        </PopoverContent>
      </Popover>
    </div>
  );
}
