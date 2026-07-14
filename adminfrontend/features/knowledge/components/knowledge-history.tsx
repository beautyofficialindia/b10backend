'use client';

import { useState } from 'react';
import { formatDistanceToNow, format } from 'date-fns';
import { 
  useKnowledgeVersions, 
  useKnowledgeVersion, 
  useRestoreKnowledgeVersion 
} from '../hooks';
import { KnowledgeVersion } from '../types';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import { StatusBadge } from '@/components/common';
import { 
  Sheet, 
  SheetContent, 
  SheetHeader, 
  SheetTitle, 
  SheetDescription 
} from '@/components/ui/sheet';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from '@/components/ui/dialog';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Eye, ArrowLeftRight, RotateCcw } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

function getStatusVariant(status: string): 'active' | 'inactive' | 'pending' | 'error' {
  switch (status) {
    case 'published': return 'active';
    case 'archived': return 'inactive';
    case 'draft': return 'pending';
    default: return 'inactive';
  }
}

interface KnowledgeHistoryProps {
  entryId: string;
}

export function KnowledgeHistory({ entryId }: KnowledgeHistoryProps) {
  const { data, isLoading, isError } = useKnowledgeVersions(entryId);
  const versions = data?.data || [];

  const [viewVersionId, setViewVersionId] = useState<string | null>(null);
  const [restoreVersionId, setRestoreVersionId] = useState<string | null>(null);

  if (isLoading) {
    return (
      <div className="space-y-4">
        {[1, 2, 3].map(i => (
          <div key={i} className="flex gap-4 p-4 border rounded-lg">
            <div className="flex-1 space-y-2">
              <Skeleton className="h-5 w-32" />
              <Skeleton className="h-4 w-full max-w-md" />
              <div className="flex gap-2 pt-2">
                <Skeleton className="h-8 w-8 rounded-full" />
                <div className="space-y-1">
                  <Skeleton className="h-3 w-24" />
                  <Skeleton className="h-3 w-16" />
                </div>
              </div>
            </div>
            <div className="flex flex-col gap-2 w-24">
              <Skeleton className="h-8 w-full" />
              <Skeleton className="h-8 w-full" />
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (isError) {
    return <div className="text-sm text-red-500">Failed to load version history.</div>;
  }

  if (versions.length === 0) {
    return (
      <div className="text-center py-12 border rounded-lg bg-muted/20">
        <h3 className="text-lg font-medium text-foreground mb-1">No version history yet.</h3>
        <p className="text-sm text-muted-foreground">Versions are created whenever this article changes.</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {versions.map((version) => (
        <div key={version.id} className="flex flex-col sm:flex-row gap-4 p-5 border rounded-lg bg-card hover:bg-muted/10 transition-colors">
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-2">
              <span className="font-semibold text-base bg-muted px-2 py-0.5 rounded-md border text-foreground">
                V{version.version_number}
              </span>
              <StatusBadge status={getStatusVariant(version.status)} label={version.status} />
            </div>
            <p className="text-sm text-foreground font-medium mb-4">{version.change_summary}</p>
            
            <div className="flex items-center gap-2">
              <Avatar className="h-8 w-8 border">
                <AvatarFallback className="text-xs bg-primary/10 text-primary">
                  {version.created_by?.first_name?.charAt(0) || version.created_by?.username?.charAt(0) || '?'}
                </AvatarFallback>
              </Avatar>
              <div className="flex flex-col">
                <span className="text-xs font-medium text-foreground">
                  {version.created_by ? `${version.created_by.first_name} ${version.created_by.last_name}`.trim() || version.created_by.username : 'System'}
                </span>
                <span className="text-xs text-muted-foreground" title={format(new Date(version.created_at), 'PPP p')}>
                  {formatDistanceToNow(new Date(version.created_at), { addSuffix: true })}
                </span>
              </div>
            </div>
          </div>
          <div className="flex sm:flex-col gap-2 shrink-0">
            <Button variant="outline" size="sm" className="gap-1.5 w-full sm:w-auto" onClick={() => setViewVersionId(version.id)}>
              <Eye className="h-3.5 w-3.5" /> View
            </Button>
            <Button variant="outline" size="sm" className="gap-1.5 w-full sm:w-auto opacity-50 cursor-not-allowed" disabled title="Coming soon">
              <ArrowLeftRight className="h-3.5 w-3.5" /> Compare
            </Button>
            <Button variant="outline" size="sm" className="gap-1.5 w-full sm:w-auto hover:bg-destructive/10 hover:text-destructive hover:border-destructive/30" onClick={() => setRestoreVersionId(version.id)}>
              <RotateCcw className="h-3.5 w-3.5" /> Restore
            </Button>
          </div>
        </div>
      ))}

      {/* View Drawer */}
      <VersionDrawer 
        versionId={viewVersionId} 
        onClose={() => setViewVersionId(null)} 
      />

      {/* Restore Dialog */}
      <RestoreDialog
        entryId={entryId}
        version={versions.find(v => v.id === restoreVersionId) || null}
        onClose={() => setRestoreVersionId(null)}
      />
    </div>
  );
}

function VersionDrawer({ versionId, onClose }: { versionId: string | null, onClose: () => void }) {
  const { data, isLoading } = useKnowledgeVersion(versionId || '');
  const version = data?.data;

  return (
    <Sheet open={!!versionId} onOpenChange={(open) => !open && onClose()}>
      <SheetContent className="w-full sm:max-w-2xl overflow-y-auto sm:w-[600px] border-l">
        <SheetHeader className="mb-6">
          <SheetTitle className="text-xl">Version {version?.version_number}</SheetTitle>
          <SheetDescription>
            View a read-only snapshot of this entry&apos;s past state.
          </SheetDescription>
        </SheetHeader>

        {isLoading && (
          <div className="space-y-6 mt-4">
            <Skeleton className="h-24 w-full" />
            <Skeleton className="h-40 w-full" />
          </div>
        )}

        {version && !isLoading && (
          <div className="space-y-6">
            {/* Meta */}
            <div className="grid grid-cols-2 gap-4 rounded-lg border p-4 bg-muted/20">
              <div>
                <p className="text-xs text-muted-foreground mb-1">Status</p>
                <StatusBadge status={getStatusVariant(version.status)} label={version.status} />
              </div>
              <div>
                <p className="text-xs text-muted-foreground mb-1">Created</p>
                <p className="text-sm font-medium">{format(new Date(version.created_at), 'PPP')}</p>
              </div>
              <div>
                <p className="text-xs text-muted-foreground mb-1">Author</p>
                <p className="text-sm font-medium">
                  {version.created_by ? `${version.created_by.first_name} ${version.created_by.last_name}`.trim() || version.created_by.username : 'System'}
                </p>
              </div>
              <div className="col-span-2 pt-2 border-t mt-1">
                <p className="text-xs text-muted-foreground mb-1">Summary</p>
                <p className="text-sm">{version.change_summary}</p>
              </div>
              <div className="col-span-2 pt-2 border-t mt-1 grid grid-cols-2 gap-4">
                <div>
                  <p className="text-xs text-muted-foreground mb-1">Category</p>
                  <p className="text-sm capitalize">{version.category_snapshot?.name as string || 'None'}</p>
                </div>
                <div>
                  <p className="text-xs text-muted-foreground mb-1">Tags</p>
                  <p className="text-sm">
                    {version.tags_snapshot && version.tags_snapshot.length > 0 
                      ? version.tags_snapshot.map(t => t.name).join(', ') 
                      : 'None'}
                  </p>
                </div>
              </div>
            </div>

            {/* Content Preview */}
            <div>
              <h3 className="text-sm font-medium mb-3 text-muted-foreground">Markdown Preview</h3>
              <div className="rounded-lg border p-6 bg-card shadow-sm">
                <div className="prose prose-sm dark:prose-invert max-w-none break-words">
                  {version.content ? (
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>{version.content}</ReactMarkdown>
                  ) : (
                    <span className="text-muted-foreground italic">No content</span>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}
      </SheetContent>
    </Sheet>
  );
}

function RestoreDialog({ entryId, version, onClose }: { entryId: string, version: KnowledgeVersion | null, onClose: () => void }) {
  const restoreMutation = useRestoreKnowledgeVersion(entryId);

  const handleRestore = () => {
    if (!version) return;
    restoreMutation.mutate(version.id, {
      onSuccess: () => {
        onClose();
      }
    });
  };

  return (
    <Dialog open={!!version} onOpenChange={(open) => !open && onClose()}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Restore Version {version?.version_number}?</DialogTitle>
          <DialogDescription>
            You are about to restore this entry to the state it was in on {version && format(new Date(version.created_at), 'PPP')}.
          </DialogDescription>
        </DialogHeader>
        
        <div className="bg-amber-50 dark:bg-amber-950/30 text-amber-800 dark:text-amber-200 p-4 rounded-md text-sm my-2 border border-amber-200 dark:border-amber-900">
          <p className="font-medium mb-1">The current version will NOT be deleted.</p>
          <p>A new version will be created containing Version {version?.version_number}&apos;s content. This ensures history is always preserved.</p>
        </div>

        <DialogFooter className="mt-4">
          <Button variant="outline" onClick={onClose} disabled={restoreMutation.isPending}>
            Cancel
          </Button>
          <Button onClick={handleRestore} disabled={restoreMutation.isPending}>
            {restoreMutation.isPending ? 'Restoring...' : 'Restore'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
