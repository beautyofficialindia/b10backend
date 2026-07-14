'use client';

import { use } from 'react';
import { useRouter } from 'next/navigation';
import { PageContainer } from '@/components/layout';
import { StatusBadge, ErrorState, CopyButton } from '@/components/common';
import { Skeleton } from '@/components/ui/skeleton';
import { Button } from '@/components/ui/button';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs';
import { ArrowLeft, Edit, Globe, Archive, Bot, RefreshCcw, EyeOff, History } from 'lucide-react';
import { 
  useKnowledgeDetail, 
  usePublishEntry, 
  useArchiveEntry, 
  useUnpublishEntry, 
  useRestoreEntry 
} from '@/features/knowledge';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { KnowledgeHistory } from '@/features/knowledge/components/knowledge-history';

function getStatusVariant(status: string): 'active' | 'inactive' | 'pending' | 'error' {
  switch (status) {
    case 'published': return 'active';
    case 'archived': return 'inactive';
    case 'draft': return 'pending';
    default: return 'inactive';
  }
}

export default function KnowledgeDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const router = useRouter();
  const { data, isLoading, isError, refetch } = useKnowledgeDetail(id);
  const publishMutation = usePublishEntry();
  const archiveMutation = useArchiveEntry();
  const unpublishMutation = useUnpublishEntry();
  const restoreMutation = useRestoreEntry();

  const entry = data?.data;

  if (isLoading) {
    return (
      <PageContainer>
        <Skeleton className="h-6 w-32 mb-4" />
        <Skeleton className="h-48 w-full" />
      </PageContainer>
    );
  }

  if (isError || !entry) {
    return (
      <PageContainer>
        <ErrorState title="Entry not found" message="This knowledge entry may have been deleted." onRetry={() => refetch()} />
      </PageContainer>
    );
  }

  return (
    <PageContainer>
      <Button variant="ghost" size="sm" className="gap-1.5 -ml-2 mb-2" onClick={() => router.push('/knowledge')}>
        <ArrowLeft className="h-3.5 w-3.5" />Back to Knowledge Base
      </Button>

      {/* Header */}
      <div className="rounded-xl border bg-card p-5 shadow-sm">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <div className="flex items-center gap-3 flex-wrap">
              <h1 className="text-xl font-semibold">{entry.title}</h1>
              <StatusBadge status={getStatusVariant(entry.status)} label={entry.status} />
            </div>
            <div className="flex flex-wrap items-center gap-x-4 gap-y-1 mt-2 text-sm text-muted-foreground">
              <span className="capitalize bg-muted px-2 py-0.5 rounded text-xs">{entry.category?.name || 'Uncategorized'}</span>
              <span className="flex items-center gap-1 text-xs">/{entry.slug} <CopyButton value={entry.slug} /></span>
              {entry.tags && entry.tags.length > 0 && (
                <span className="flex items-center gap-1 text-xs text-muted-foreground ml-2">
                  Tags: {entry.tags.map((t: { name: string }) => t.name).join(', ')}
                </span>
              )}
              {entry.created_by && <span className="text-xs">by {entry.created_by}</span>}
            </div>
          </div>
          <div className="flex gap-2 shrink-0">
            <Button variant="outline" size="sm" className="gap-1.5" onClick={() => router.push(`/knowledge/${id}/edit`)}>
              <Edit className="h-3.5 w-3.5" />Edit
            </Button>
            {entry.status === 'draft' && (
              <Button size="sm" className="gap-1.5 bg-emerald-600 hover:bg-emerald-700" disabled={publishMutation.isPending} onClick={() => publishMutation.mutate(id)}>
                <Globe className="h-3.5 w-3.5" />Publish
              </Button>
            )}
            {entry.status === 'published' && (
              <Button variant="outline" size="sm" className="gap-1.5" disabled={unpublishMutation.isPending} onClick={() => unpublishMutation.mutate(id)}>
                <EyeOff className="h-3.5 w-3.5" />Unpublish
              </Button>
            )}
            {entry.status !== 'archived' && (
              <Button variant="outline" size="sm" className="gap-1.5" disabled={archiveMutation.isPending} onClick={() => archiveMutation.mutate(id)}>
                <Archive className="h-3.5 w-3.5" />Archive
              </Button>
            )}
            {entry.status === 'archived' && (
              <Button variant="outline" size="sm" className="gap-1.5" disabled={restoreMutation.isPending} onClick={() => restoreMutation.mutate(id)}>
                <RefreshCcw className="h-3.5 w-3.5" />Restore
              </Button>
            )}
          </div>
        </div>
      </div>

      {/* Content Tabs */}
      <Tabs defaultValue="overview" className="mt-6">
        <TabsList className="mb-4">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="preview">Preview</TabsTrigger>
          <TabsTrigger value="history" className="gap-1.5">
            <History className="h-3.5 w-3.5" />History
          </TabsTrigger>
        </TabsList>
        
        <TabsContent value="overview">
          <div className="grid gap-6 lg:grid-cols-3">
            <div className="lg:col-span-2">
              <div className="rounded-lg border p-5 bg-card">
                <h3 className="text-sm font-medium mb-3 text-muted-foreground">Source Markdown</h3>
                <div className="prose prose-sm dark:prose-invert max-w-none">
                  <p className="whitespace-pre-wrap font-mono text-xs leading-relaxed text-muted-foreground">{entry.content || 'No content yet.'}</p>
                </div>
              </div>
            </div>

            <div className="space-y-4">
              {/* AI Context Preview */}
              <div className="rounded-lg border p-4 bg-muted/30">
                <div className="flex items-center gap-2 mb-2">
                  <Bot className="h-4 w-4 text-primary" />
                  <h3 className="text-sm font-medium">AI Context</h3>
                </div>
                <p className="text-xs text-muted-foreground">
                  {entry.status === 'published'
                    ? `This entry is included in chatbot responses when "${entry.category?.name || 'Uncategorized'}" knowledge is requested.`
                    : 'This entry is NOT visible to the chatbot (not published).'}
                </p>
              </div>

              {/* Meta */}
              <div className="rounded-lg border p-4 space-y-2.5 bg-card">
                <h3 className="text-sm font-medium">Details</h3>
                <div className="text-sm space-y-2">
                  <div className="flex justify-between"><span className="text-muted-foreground">Category</span><span className="font-medium capitalize">{entry.category?.name || 'None'}</span></div>
                  <div className="flex justify-between"><span className="text-muted-foreground">Source</span><span className="font-medium capitalize">{entry.source}</span></div>
                  <div className="flex justify-between"><span className="text-muted-foreground">Created</span><span className="font-medium">{new Date(entry.created_at).toLocaleDateString()}</span></div>
                  <div className="flex justify-between"><span className="text-muted-foreground">Updated</span><span className="font-medium">{new Date(entry.updated_at).toLocaleDateString()}</span></div>
                  {entry.published_at && <div className="flex justify-between"><span className="text-muted-foreground">Published</span><span className="font-medium">{new Date(entry.published_at).toLocaleDateString()}</span></div>}
                </div>
              </div>
            </div>
          </div>
        </TabsContent>
        
        <TabsContent value="preview">
          <div className="rounded-lg border p-8 bg-card shadow-sm">
            <div className="prose prose-sm dark:prose-invert max-w-none break-words">
              {entry.content ? (
                <ReactMarkdown remarkPlugins={[remarkGfm]}>{entry.content}</ReactMarkdown>
              ) : (
                <span className="text-muted-foreground italic">Nothing to preview</span>
              )}
            </div>
          </div>
        </TabsContent>

        <TabsContent value="history">
          <KnowledgeHistory entryId={id} />
        </TabsContent>
      </Tabs>
    </PageContainer>
  );
}
