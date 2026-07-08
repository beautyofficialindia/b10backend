'use client';

import { useState, useMemo } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { PageContainer, PageHeader } from '@/components/layout';
import { ErrorState, EmptyState, SkeletonTable, DeleteDialog } from '@/components/common';
import { DataTable, TableToolbar, TablePagination, type Column } from '@/components/tables';
import { Button } from '@/components/ui/button';
import { RefreshCw, Shield, Plus, Eye } from 'lucide-react';
import { useRolesList, useDeleteRole, type Role, type RoleFilters } from '@/features/roles';
import { useDebounce } from '@/hooks/use-debounce';

const PAGE_SIZE = 20;

const columns: Column<Role>[] = [
  { key: 'name', header: 'Role', render: (row) => <span className="text-sm font-medium">{row.name}</span> },
  { key: 'users_count', header: 'Users', render: (row) => <span className="text-sm">{row.users_count}</span>, className: 'hidden sm:table-cell' },
  { key: 'permissions_count', header: 'Permissions', render: (row) => <span className="text-sm">{row.permissions_count}</span>, className: 'hidden md:table-cell' },
  { key: 'actions', header: '', render: (row) => (
    <div className="flex gap-1">
      <Link href={`/roles/${row.id}`}><Button variant="ghost" size="icon" className="h-7 w-7"><Eye className="h-3.5 w-3.5" /></Button></Link>
    </div>
  ), className: 'w-10' },
];

export default function RolesPage() {
  const router = useRouter();
  const [search, setSearch] = useState('');
  const debouncedSearch = useDebounce(search, 300);
  const [filters, setFilters] = useState<Omit<RoleFilters, 'search'>>({ page: 1, page_size: PAGE_SIZE, ordering: 'name' });
  const [deleteTarget, setDeleteTarget] = useState<Role | null>(null);
  const deleteMutation = useDeleteRole();

  const queryFilters = useMemo<RoleFilters>(() => ({ ...filters, search: debouncedSearch }), [filters, debouncedSearch]);
  const { data, isLoading, isError, refetch, isFetching } = useRolesList(queryFilters);
  const roles = data?.data || [];
  const totalCount = data?.meta?.pagination?.total_count || 0;
  const totalPages = data?.meta?.pagination?.total_pages || 0;

  return (
    <PageContainer>
      <PageHeader title="Roles" description="Manage roles and permissions">
        <Button size="sm" onClick={() => router.push('/roles/new')} className="gap-1.5"><Plus className="h-3.5 w-3.5" />New Role</Button>
        <Button variant="outline" size="sm" onClick={() => refetch()} disabled={isFetching} className="gap-1.5">
          <RefreshCw className={`h-3.5 w-3.5 ${isFetching ? 'animate-spin' : ''}`} />Refresh
        </Button>
      </PageHeader>

      <TableToolbar searchValue={search} onSearchChange={(v) => { setSearch(v); setFilters(f => ({...f, page: 1})); }} searchPlaceholder="Search roles..." />

      {totalCount > 0 && <p className="text-xs text-muted-foreground">{totalCount} role{totalCount !== 1 ? 's' : ''}</p>}

      {isLoading ? <SkeletonTable rows={5} cols={4} /> : isError ? <ErrorState message="Failed to load roles" onRetry={() => refetch()} /> : roles.length === 0 ? (
        <EmptyState icon={Shield} title="No roles found" description="Create your first role">
          <Button size="sm" onClick={() => router.push('/roles/new')}>Create Role</Button>
        </EmptyState>
      ) : (
        <>
          <DataTable columns={columns} data={roles} />
          {totalPages > 1 && <TablePagination page={filters.page || 1} totalPages={totalPages} totalCount={totalCount} pageSize={PAGE_SIZE} onPageChange={(p) => setFilters(f => ({...f, page: p}))} />}
        </>
      )}

      <DeleteDialog open={!!deleteTarget} onOpenChange={(o) => !o && setDeleteTarget(null)} itemName={deleteTarget?.name} isLoading={deleteMutation.isPending} onConfirm={() => { if (deleteTarget) deleteMutation.mutate(deleteTarget.id, { onSuccess: () => setDeleteTarget(null) }); }} />
    </PageContainer>
  );
}
