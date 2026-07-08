'use client';

import { useState, useMemo } from 'react';
import Link from 'next/link';
import { PageContainer, PageHeader } from '@/components/layout';
import { StatusBadge, ErrorState, EmptyState } from '@/components/common';
import { DataTable, TableToolbar, TablePagination, type Column } from '@/components/tables';
import { SkeletonTable } from '@/components/common';
import { Button } from '@/components/ui/button';
import { RefreshCw, Inbox, Eye } from 'lucide-react';
import { useLeads, type Lead, type LeadFilters, type LeadStatus } from '@/features/leads';
import { getStatusVariant, statusOptions, sortOptions } from '@/features/leads/utils';
import { useDebounce } from '@/hooks/use-debounce';

const PAGE_SIZE = 20;

const columns: Column<Lead>[] = [
  {
    key: 'full_name',
    header: 'Lead',
    render: (row) => (
      <div>
        <p className="text-sm font-medium">{row.full_name || 'Anonymous'}</p>
        <p className="text-xs text-muted-foreground">{row.email || '—'}</p>
      </div>
    ),
  },
  {
    key: 'company_name',
    header: 'Company',
    render: (row) => <span className="text-sm">{row.company_name || '—'}</span>,
    className: 'hidden md:table-cell',
  },
  {
    key: 'phone',
    header: 'Phone',
    render: (row) => <span className="text-sm">{row.phone || '—'}</span>,
    className: 'hidden lg:table-cell',
  },
  {
    key: 'project_type',
    header: 'Project',
    render: (row) => <span className="text-sm">{row.project_type || '—'}</span>,
    className: 'hidden xl:table-cell',
  },
  {
    key: 'status',
    header: 'Status',
    render: (row) => (
      <StatusBadge status={getStatusVariant(row.status)} label={row.status} />
    ),
  },
  {
    key: 'created_at',
    header: 'Created',
    render: (row) => (
      <span className="text-xs text-muted-foreground">
        {new Date(row.created_at).toLocaleDateString()}
      </span>
    ),
    className: 'hidden sm:table-cell',
  },
  {
    key: 'actions',
    header: '',
    render: (row) => (
      <Link href={`/leads/${row.id}`}>
        <Button variant="ghost" size="icon" className="h-7 w-7">
          <Eye className="h-3.5 w-3.5" />
        </Button>
      </Link>
    ),
    className: 'w-10',
  },
];

export default function LeadsPage() {
  const [search, setSearch] = useState('');
  const debouncedSearch = useDebounce(search, 300);
  const [filters, setFilters] = useState<Omit<LeadFilters, 'search'>>({
    page: 1,
    page_size: PAGE_SIZE,
    ordering: '-created_at',
    status: '',
  });

  const queryFilters = useMemo<LeadFilters>(
    () => ({ ...filters, search: debouncedSearch }),
    [filters, debouncedSearch]
  );

  const { data, isLoading, isError, refetch, isFetching } = useLeads(queryFilters);

  const totalPages = data ? Math.ceil(data.count / PAGE_SIZE) : 0;

  const updateFilter = (update: Partial<Omit<LeadFilters, 'search'>>) => {
    setFilters((prev) => ({ ...prev, ...update, page: update.page ?? 1 }));
  };

  return (
    <PageContainer>
      <PageHeader title="Leads" description="Manage captured leads from chatbot conversations">
        <Button
          variant="outline"
          size="sm"
          onClick={() => refetch()}
          disabled={isFetching}
          className="gap-1.5"
        >
          <RefreshCw className={`h-3.5 w-3.5 ${isFetching ? 'animate-spin' : ''}`} />
          Refresh
        </Button>
      </PageHeader>

      {/* Filters */}
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
        <TableToolbar
          searchValue={search}
          onSearchChange={(val) => { setSearch(val); setFilters(f => ({ ...f, page: 1 })); }}
          searchPlaceholder="Search leads..."
          className="flex-1"
        >
          <select
            value={filters.status}
            onChange={(e) => updateFilter({ status: e.target.value as LeadStatus | '' })}
            className="h-9 rounded-md border bg-background px-3 text-sm"
            aria-label="Filter by status"
          >
            {statusOptions.map((opt) => (
              <option key={opt.value} value={opt.value}>{opt.label}</option>
            ))}
          </select>

          <select
            value={filters.ordering}
            onChange={(e) => updateFilter({ ordering: e.target.value })}
            className="h-9 rounded-md border bg-background px-3 text-sm"
            aria-label="Sort order"
          >
            {sortOptions.map((opt) => (
              <option key={opt.value} value={opt.value}>{opt.label}</option>
            ))}
          </select>
        </TableToolbar>
      </div>

      {/* Result count */}
      {data && data.count > 0 && (
        <p className="text-xs text-muted-foreground">
          {data.count} lead{data.count !== 1 ? 's' : ''} found
        </p>
      )}

      {/* Table */}
      {isLoading ? (
        <SkeletonTable rows={8} cols={6} />
      ) : isError ? (
        <ErrorState message="Failed to load leads" onRetry={() => refetch()} />
      ) : data && data.results.length === 0 ? (
        <EmptyState
          icon={Inbox}
          title="No leads found"
          description={debouncedSearch || filters.status ? 'Try adjusting your filters' : 'Leads will appear here once captured by the chatbot'}
        />
      ) : data ? (
        <>
          <DataTable columns={columns} data={data.results} />
          {totalPages > 1 && (
            <TablePagination
              page={filters.page || 1}
              totalPages={totalPages}
              totalCount={data.count}
              pageSize={PAGE_SIZE}
              onPageChange={(page) => updateFilter({ page })}
            />
          )}
        </>
      ) : null}
    </PageContainer>
  );
}
