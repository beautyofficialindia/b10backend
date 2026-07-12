'use client';

import { useState, useMemo } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { PageContainer, PageHeader, PageBreadcrumbs } from '@/components/layout';
import { PermissionGuard, useHasPermission } from '@/features/auth';
import { ErrorState, EmptyState, SkeletonTable, DeleteDialog } from '@/components/common';
import { DataTable, TableToolbar, TablePagination, type Column } from '@/components/tables';
import { Button } from '@/components/ui/button';
import { RefreshCw, Shield, Plus, Eye, Trash2 } from 'lucide-react';
import { useRolesList, useDeleteRole, type Role, type RoleFilters } from '@/features/roles';
import { useDebounce } from '@/hooks/use-debounce';
import { MIN_SEARCH_LENGTH } from '@/lib/constants/search';

const PAGE_SIZE = 20;

const columns: Column<Role>[] = [
  { key: 'name', header: 'Role', sortable: true, render: (row) => <span className="text-sm font-medium">{row.name}</span> },
  { key: 'users_count', header: 'Users', render: (row) => <span className="text-sm">{row.users_count}</span>, className: 'hidden sm:table-cell' },
  { key: 'permissions_count', header: 'Permissions', render: (row) => <span className="text-sm">{row.permissions_count}</span>, className: 'hidden md:table-cell' },
  { key: 'actions', header: '', render: (row) => (
    <div className="flex gap-1 justify-end">
      <Link href={`/roles/${row.id}`}><Button variant="ghost" size="icon" className="h-7 w-7"><Eye className="h-3.5 w-3.5" /></Button></Link>
    </div>
  ), className: 'w-16' },
];

export default function RolesPage() {
  const router = useRouter();
  const [search, setSearch] = useState('');
  const debouncedSearch = useDebounce(search, 300);
  const [filters, setFilters] = useState<Omit<RoleFilters, 'search'>>({ page: 1, page_size: PAGE_SIZE, ordering: 'name' });
  const [deleteTarget, setDeleteTarget] = useState<Role | null>(null);
  const deleteMutation = useDeleteRole();

  const queryFilters = useMemo<RoleFilters>(() => ({ ...filters, search: debouncedSearch.length >= MIN_SEARCH_LENGTH ? debouncedSearch : '' }), [filters, debouncedSearch]);
  const { data, isLoading, isError, refetch, isFetching } = useRolesList(queryFilters);
  const roles = data?.data || [];
  const totalCount = data?.meta?.pagination?.total_count || 0;
  const totalPages = data?.meta?.pagination?.total_pages || 0;
  const hasDeleteGroup = useHasPermission(['auth.delete_group']);

  const handleSort = (key: string) => {
    setFilters(f => {
      if (f.ordering === key) return { ...f, ordering: `-${key}`, page: 1 };
      if (f.ordering === `-${key}`) return { ...f, ordering: key, page: 1 };
      return { ...f, ordering: key, page: 1 };
    });
  };

  // Add delete action dynamically based on permission
  const dynamicColumns = useMemo(() => {
    if (!hasDeleteGroup) return columns;
    const cols = [...columns];
    cols[cols.length - 1] = {
      key: 'actions', header: '', className: 'w-20',
      render: (row) => (
        <div className="flex gap-1 justify-end">
          <Link href={`/roles/${row.id}`}><Button variant="ghost" size="icon" className="h-7 w-7"><Eye className="h-3.5 w-3.5" /></Button></Link>
          <Button variant="ghost" size="icon" className="h-7 w-7 text-muted-foreground hover:text-destructive" onClick={() => setDeleteTarget(row)}>
            <Trash2 className="h-3.5 w-3.5" />
          </Button>
        </div>
      )
    };
    return cols;
  }, [hasDeleteGroup]);

  return (
    <PermissionGuard permissions={['auth.view_group']}>
    <PageContainer>
      <PageHeader 
        title="Roles" 
        description="Manage roles and permissions"
        breadcrumbs={<PageBreadcrumbs items={[{ label: 'Roles', href: '/roles' }]} />}
      >
        <PermissionGuard permissions={['auth.add_group']}>
          <Button size="sm" onClick={() => router.push('/roles/new')} className="gap-1.5"><Plus className="h-3.5 w-3.5" />New Role</Button>
        </PermissionGuard>
        <Button variant="outline" size="sm" onClick={() => refetch()} disabled={isFetching} className="gap-1.5">
          <RefreshCw className={`h-3.5 w-3.5 ${isFetching ? 'animate-spin' : ''}`} />Refresh
        </Button>
      </PageHeader>

      <TableToolbar searchValue={search} onSearchChange={(v) => { setSearch(v); setFilters(f => ({...f, page: 1})); }} searchPlaceholder="Search roles..." />

      {totalCount > 0 && <p className="text-xs text-muted-foreground">{totalCount} role{totalCount !== 1 ? 's' : ''}</p>}

      {isLoading ? <SkeletonTable rows={5} cols={4} /> : isError ? <ErrorState message="Failed to load roles" onRetry={() => refetch()} /> : roles.length === 0 ? (
        <EmptyState icon={Shield} title="No roles found" description="Create your first role">
          <PermissionGuard permissions={['auth.add_group']}>
            <Button size="sm" onClick={() => router.push('/roles/new')}>Create Role</Button>
          </PermissionGuard>
        </EmptyState>
      ) : (
        <>
          <DataTable 
            columns={dynamicColumns} 
            data={roles}
            sortKey={filters.ordering?.replace('-', '')}
            sortDirection={filters.ordering?.startsWith('-') ? 'desc' : 'asc'}
            onSort={handleSort}
          />
          {totalPages > 1 && <TablePagination page={filters.page || 1} totalPages={totalPages} totalCount={totalCount} pageSize={PAGE_SIZE} onPageChange={(p) => setFilters(f => ({...f, page: p}))} />}
        </>
      )}

      <DeleteDialog open={!!deleteTarget} onOpenChange={(o) => !o && setDeleteTarget(null)} itemName={deleteTarget?.name} isLoading={deleteMutation.isPending} onConfirm={() => { if (deleteTarget) deleteMutation.mutate(deleteTarget.id, { onSuccess: () => setDeleteTarget(null) }); }} />
    </PageContainer>
    </PermissionGuard>
  );
}
