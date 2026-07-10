'use client';

import { useState, useMemo } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { PageContainer, PageHeader } from '@/components/layout';
import { StatusBadge, ErrorState, EmptyState, SkeletonTable, DeleteDialog } from '@/components/common';
import { DataTable, TableToolbar, TablePagination, type Column } from '@/components/tables';
import { Button } from '@/components/ui/button';
import { RefreshCw, BookOpen, Plus, Eye, Trash2 } from 'lucide-react';
import { useKnowledgeList, useDeleteEntry, type KnowledgeEntry, type KBFilters, type KBCategory, type KBStatus } from '@/features/knowledge';
import { useDebounce } from '@/hooks/use-debounce';
import { MIN_SEARCH_LENGTH } from '@/lib/constants/search';

const PAGE_SIZE = 20;

const categoryOptions: { value: KBCategory | ''; label: string }[] = [
  { value: '', label: 'All Categories' },
  { value: 'company', label: 'Company' },
  { value: 'service', label: 'Service' },
  { value: 'industry', label: 'Industry' },
  { value: 'faq', label: 'FAQ' },
  { value: 'contact', label: 'Contact' },
  { value: 'technology', label: 'Technology' },
  { value: 'general', label: 'General' },
];

const statusOptions: { value: KBStatus | ''; label: string }[] = [
  { value: '', label: 'All Statuses' },
  { value: 'draft', label: 'Draft' },
  { value: 'published', label: 'Published' },
  { value: 'archived', label: 'Archived' },
];

function getStatusVariant(status: string): 'active' | 'inactive' | 'pending' | 'error' {
  switch (status) {
    case 'published': return 'active';
    case 'archived': return 'error';
    default: return 'inactive';
  }
}

export default function KnowledgePage() {
  const router = useRouter();
  const [search, setSearch] = useState('');
  const debouncedSearch = useDebounce(search, 300);
  const [filters, setFilters] = useState<Omit<KBFilters, 'search'>>({
    page: 1, page_size: PAGE_SIZE, ordering: '-updated_at', category: '', status: '',
  });
  const [deleteTarget, setDeleteTarget] = useState<KnowledgeEntry | null>(null);
  const deleteMutation = useDeleteEntry();

  const queryFilters = useMemo<KBFilters>(
    () => ({ ...filters, search: debouncedSearch.length >= MIN_SEARCH_LENGTH ? debouncedSearch : '' }),
    [filters, debouncedSearch]
  );

  const { data, isLoading, isError, refetch, isFetching } = useKnowledgeList(queryFilters);
  const entries = data?.data || [];
  const totalCount = data?.meta?.pagination?.total_count || 0;
  const totalPages = data?.meta?.pagination?.total_pages || 0;

  const updateFilter = (update: Partial<Omit<KBFilters, 'search'>>) => {
    setFilters((prev) => ({ ...prev, ...update, page: update.page ?? 1 }));
  };

  const columns: Column<KnowledgeEntry>[] = [
    { key: 'title', header: 'Title', render: (row) => (
      <div>
        <p className="text-sm font-medium truncate max-w-[200px]">{row.title}</p>
        <p className="text-xs text-muted-foreground">{row.slug}</p>
      </div>
    )},
    { key: 'category', header: 'Category', render: (row) => (
      <span className="text-xs capitalize bg-muted px-2 py-0.5 rounded">{row.category}</span>
    ), className: 'hidden md:table-cell' },
    { key: 'status', header: 'Status', render: (row) => (
      <StatusBadge status={getStatusVariant(row.status)} label={row.status} />
    )},
    { key: 'updated_at', header: 'Updated', render: (row) => (
      <span className="text-xs text-muted-foreground">{new Date(row.updated_at).toLocaleDateString()}</span>
    ), className: 'hidden sm:table-cell' },
    { key: 'actions', header: '', render: (row) => (
      <div className="flex gap-1">
        <Link href={`/knowledge/${row.id}`}>
          <Button variant="ghost" size="icon" className="h-7 w-7"><Eye className="h-3.5 w-3.5" /></Button>
        </Link>
        <Button variant="ghost" size="icon" className="h-7 w-7 text-destructive" onClick={(e) => { e.stopPropagation(); setDeleteTarget(row); }}>
          <Trash2 className="h-3.5 w-3.5" />
        </Button>
      </div>
    ), className: 'w-20' },
  ];

  return (
    <PageContainer>
      <PageHeader title="Knowledge Base" description="Manage content that powers the chatbot">
        <Button size="sm" onClick={() => router.push('/knowledge/new')} className="gap-1.5">
          <Plus className="h-3.5 w-3.5" />New Entry
        </Button>
        <Button variant="outline" size="sm" onClick={() => refetch()} disabled={isFetching} className="gap-1.5">
          <RefreshCw className={`h-3.5 w-3.5 ${isFetching ? 'animate-spin' : ''}`} />Refresh
        </Button>
      </PageHeader>

      <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
        <TableToolbar searchValue={search} onSearchChange={(v) => { setSearch(v); setFilters(f => ({...f, page: 1})); }} searchPlaceholder="Search entries..." className="flex-1">
          <select value={filters.category} onChange={(e) => updateFilter({ category: e.target.value as KBCategory | '' })} className="h-9 rounded-md border bg-background px-3 text-sm" aria-label="Category">
            {categoryOptions.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
          </select>
          <select value={filters.status} onChange={(e) => updateFilter({ status: e.target.value as KBStatus | '' })} className="h-9 rounded-md border bg-background px-3 text-sm" aria-label="Status">
            {statusOptions.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
          </select>
        </TableToolbar>
      </div>

      {totalCount > 0 && <p className="text-xs text-muted-foreground">{totalCount} entr{totalCount === 1 ? 'y' : 'ies'} found</p>}

      {isLoading ? <SkeletonTable rows={6} cols={5} /> : isError ? <ErrorState message="Failed to load entries" onRetry={() => refetch()} /> : entries.length === 0 ? (
        <EmptyState icon={BookOpen} title="No entries found" description={debouncedSearch || filters.category || filters.status ? 'Try adjusting your filters' : 'Create your first knowledge base entry'}>
          <Button size="sm" onClick={() => router.push('/knowledge/new')}>Create Entry</Button>
        </EmptyState>
      ) : (
        <>
          <DataTable columns={columns} data={entries} />
          {totalPages > 1 && <TablePagination page={filters.page || 1} totalPages={totalPages} totalCount={totalCount} pageSize={PAGE_SIZE} onPageChange={(p) => updateFilter({ page: p })} />}
        </>
      )}

      <DeleteDialog open={!!deleteTarget} onOpenChange={(o) => !o && setDeleteTarget(null)} itemName={deleteTarget?.title} isLoading={deleteMutation.isPending} onConfirm={() => { if (deleteTarget) deleteMutation.mutate(deleteTarget.id, { onSuccess: () => setDeleteTarget(null) }); }} />
    </PageContainer>
  );
}
