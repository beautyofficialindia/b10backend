import { useMemo } from 'react';
import { Checkbox } from '@/components/ui/checkbox';
import type { Permission } from '../types';

interface PermissionTreeProps {
  permissions: Permission[];
  activePerms: Set<string>;
  onTogglePerm: (code: string) => void;
  disabled?: boolean;
}

export function PermissionTree({ permissions, activePerms, onTogglePerm, disabled }: PermissionTreeProps) {
  const groupedPerms = useMemo(() => {
    const groups: Record<string, Permission[]> = {};
    for (const p of permissions) {
      const app = p.content_type.split('.')[0];
      if (!groups[app]) groups[app] = [];
      groups[app].push(p);
    }
    return groups;
  }, [permissions]);

  return (
    <div className="space-y-6">
      {Object.entries(groupedPerms).sort().map(([app, perms]) => (
        <div key={app} className="rounded-lg border p-4">
          <h3 className="text-sm font-medium capitalize mb-3">{app}</h3>
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-2">
            {perms.map(p => {
              const code = `${p.content_type.split('.')[0]}.${p.codename}`;
              return (
                <label key={p.id} className={`flex items-center gap-2 text-sm ${disabled ? 'cursor-not-allowed opacity-70' : 'cursor-pointer'}`}>
                  <Checkbox 
                    disabled={disabled} 
                    checked={activePerms.has(code)} 
                    onCheckedChange={() => onTogglePerm(code)} 
                  />
                  <span className="truncate" title={p.name}>{p.codename}</span>
                </label>
              );
            })}
          </div>
        </div>
      ))}
    </div>
  );
}
