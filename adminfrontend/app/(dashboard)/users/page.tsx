'use client';

import { useState, useMemo } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { PageContainer, PageHeader } from '@/components/layout';
import { StatusBadge, RoleBadge, ErrorState, EmptyState, SkeletonTable } from '@/components/common';
import { DataTable, TableToolbar, TablePagination, type Column } from '@/components/tables';
import { Button } from '@/components/ui/button';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { RefreshCw, Users, Plus, Eye, Shield } from 'lucide-react';
import { useUsersList, useBulkActivate, useBulkDeactivate, type User, type UserFilters } from '@/features/users';
import { useDebounce } from '@/hooks/use-debounce';

const PAGE_SIZE = 20;

const columns: Column<User>[] = [
  { key: 'username', header: 'User', render: (row) => (
    <div className="flex items-center gap-3">
      <Avatar className="h-8 w-8">
        <AvatarFallback className="text-xs">{(row.first_name?.[0] || row.username[0]).toUpperCase()}{(row.last_name?.[0] || '').toUpperCase()}</AvatarFallback>
      </Avatar>
      <div>
        <p className="text-sm font-medium">{row.first_name && row.last_name ? `${row.first_name} ${row.last_name}` : row.username}</p>
        <p className="text-xs text-muted-foreground">{row.email}</p>
      </div>
    </div>
  )},
  { key: 'groups', header: 'Roles', render: (row) => (
    <div className="flex flex-wrap gap-1">{row.groups.map(g => <RoleBadge key={g} role={g} />)}</div>
  ), className: 'hidden md:table-cell' },
  { key: 'is_active', header: 'Status', render: (row) => (
    <div className="flex items-center gap-1.5">
      <StatusBadge status={row.is_active ? 'active' : 'inactive'} label={row.is_active ? 'Active' : 'Inactive'} />
      {row.is_superuser && <Shield className="h-3.5 w-3.5 text-amber-500" />}
    </div>
  )},
  { key: 'last_login', header: 'Last Login', render: (row) => (
    <span className="text-xs text-muted-foreground">{row.last_login ? new Date(row.last_login).toLocaleDateString() : 'Never'}</span>
  ), className: 'hidden lg:table-cell' },
  { key: 'actions', header: '', render: (row) => (
    <Link href={`/users/${row.id}`}><Button variant="ghost" size="icon" className="h-7 w-7"><Eye className="h-3.5 w-3.5" /></Button></Link>
  ), className: 'w-10' },
];

export default function UsersPage() {
  const router = useRouter();
  const [search, setSearch] = useState('');
  const debouncedSearch = useDebounce(search, 300);
  const [filters, setFilters] = useState<Omit<UserFilters, 'search'>>({
    page: 1, page_size: PAGE_SIZE, ordering: '-date_joined', is_active: '', is_superuser: '', group: '',
  });
  const [selected, setSelected] = useState<number[]>([]);

  const queryFilters = useMemo<UserFilters>(() => ({ ...filters, search: debouncedSearch }), [filters, debouncedSearch]);
  const { data, isLoading, isError, refetch, isFetching } = useUsersList(queryFilters);
  const bulkActivate = useBulkActivate();
  const bulkDeactivate = useBulkDeactivate();

  const users = data?.data || [];
  const totalCount = data?.meta?.pagination?.total_count || 0;
  const totalPages = data?.meta?.pagination?.total_pages || 0;

  const updateFilter = (update: Partial<Omit<UserFilters, 'search'>>) => {
    setFilters(prev => ({ ...prev, ...update, page: update.page ?? 1 }));
  };

  return (
    <PageContainer>
      <PageHeader title="Users" description="Manage admin and staff accounts">
        <Button size="sm" onClick={() => router.push('/users/new')} className="gap-1.5"><Plus className="h-3.5 w-3.5" />New User</Button>
        <Button variant="outline" size="sm" onClick={() => refetch()} disabled={isFetching} className="gap-1.5">
          <RefreshCw className={`h-3.5 w-3.5 ${isFetching ? 'animate-spin' : ''}`} />Refresh
        </Button>
      </PageHeader>

      <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
        <TableToolbar searchValue={search} onSearchChange={(v) => { setSearch(v); setFilters(f => ({...f, page: 1})); }} searchPlaceholder="Search users..." className="flex-1">
          <select value={filters.is_active} onChange={(e) => updateFilter({ is_active: e.target.value })} className="h-9 rounded-md border bg-background px-3 text-sm" aria-label="Status">
            <option value="">All</option>
            <option value="true">Active</option>
            <option value="false">Inactive</option>
          </select>
          <select value={filters.is_superuser} onChange={(e) => updateFilter({ is_superuser: e.target.value })} className="h-9 rounded-md border bg-background px-3 text-sm" aria-label="Role">
            <option value="">All Roles</option>
            <option value="true">Superusers</option>
            <option value="false">Regular</option>
          </select>
        </TableToolbar>
      </div>

      {/* Bulk actions */}
      {selected.length > 0 && (
        <div className="flex items-center gap-2 p-3 rounded-lg bg-muted">
          <span className="text-sm font-medium">{selected.length} selected</span>
          <Button size="sm" variant="outline" onClick={() => bulkActivate.mutate(selected, { onSuccess: () => setSelected([]) })}>Activate</Button>
          <Button size="sm" variant="outline" onClick={() => bulkDeactivate.mutate(selected, { onSuccess: () => setSelected([]) })}>Deactivate</Button>
          <Button size="sm" variant="ghost" onClick={() => setSelected([])}>Clear</Button>
        </div>
      )}

      {totalCount > 0 && <p className="text-xs text-muted-foreground">{totalCount} user{totalCount !== 1 ? 's' : ''}</p>}

      {isLoading ? <SkeletonTable rows={8} cols={5} /> : isError ? <ErrorState message="Failed to load users" onRetry={() => refetch()} /> : users.length === 0 ? (
        <EmptyState icon={Users} title="No users found" description={debouncedSearch ? 'Try adjusting your search' : 'Create your first user'}>
          <Button size="sm" onClick={() => router.push('/users/new')}>Create User</Button>
        </EmptyState>
      ) : (
        <>
          <DataTable columns={columns} data={users} />
          {totalPages > 1 && <TablePagination page={filters.page || 1} totalPages={totalPages} totalCount={totalCount} pageSize={PAGE_SIZE} onPageChange={(p) => updateFilter({ page: p })} />}
        </>
      )}
    </PageContainer>
  );
}
