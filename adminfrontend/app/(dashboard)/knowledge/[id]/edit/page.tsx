'use client';

import { use, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { PageContainer } from '@/components/layout';
import { ErrorState } from '@/components/common';
import { TextField, TextAreaField, FormSection } from '@/components/forms';
import { Skeleton } from '@/components/ui/skeleton';
import { Button } from '@/components/ui/button';
import { ArrowLeft, Save, Loader2 } from 'lucide-react';
import { useKnowledgeDetail, useUpdateEntry } from '@/features/knowledge';
import type { KBCategory } from '@/features/knowledge';

const schema = z.object({
  title: z.string().min(1, 'Title is required'),
  category: z.string().min(1, 'Category is required'),
  content: z.string(),
  sort_order: z.number().min(0).optional(),
});

type FormData = z.infer<typeof schema>;

const categories: { value: KBCategory; label: string }[] = [
  { value: 'company', label: 'Company' },
  { value: 'service', label: 'Service' },
  { value: 'industry', label: 'Industry' },
  { value: 'faq', label: 'FAQ' },
  { value: 'contact', label: 'Contact' },
  { value: 'technology', label: 'Technology' },
  { value: 'general', label: 'General' },
];

export default function KnowledgeEditPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const router = useRouter();
  const { data, isLoading, isError, refetch } = useKnowledgeDetail(id);
  const updateMutation = useUpdateEntry();

  const { register, handleSubmit, reset, formState: { errors, isDirty } } = useForm<FormData>({
    resolver: zodResolver(schema),
  });

  const entry = data?.data;

  useEffect(() => {
    if (entry) {
      reset({
        title: entry.title,
        category: entry.category,
        content: entry.content,
        sort_order: entry.sort_order,
      });
    }
  }, [entry, reset]);

  const onSubmit = (formData: FormData) => {
    updateMutation.mutate(
      { id, data: formData as Partial<{ category: KBCategory; title: string; content: string; sort_order: number }> },
      { onSuccess: () => router.push(`/knowledge/${id}`) }
    );
  };

  if (isLoading) return <PageContainer><Skeleton className="h-6 w-32 mb-4" /><Skeleton className="h-64 w-full" /></PageContainer>;
  if (isError || !entry) return <PageContainer><ErrorState title="Entry not found" onRetry={() => refetch()} /></PageContainer>;

  return (
    <PageContainer>
      <Button variant="ghost" size="sm" className="gap-1.5 -ml-2 mb-2" onClick={() => router.push(`/knowledge/${id}`)}>
        <ArrowLeft className="h-3.5 w-3.5" />Back to Entry
      </Button>

      <div className="max-w-2xl">
        <h1 className="text-xl font-semibold mb-6">Edit Entry</h1>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
          <FormSection title="Details">
            <TextField label="Title" error={errors.title?.message} required {...register('title')} />
            <div className="space-y-1.5">
              <label className="text-sm font-medium">Category <span className="text-destructive">*</span></label>
              <select {...register('category')} className="w-full h-9 rounded-md border bg-background px-3 text-sm">
                {categories.map(c => <option key={c.value} value={c.value}>{c.label}</option>)}
              </select>
              {errors.category && <p className="text-xs text-destructive">{errors.category.message}</p>}
            </div>
          </FormSection>

          <FormSection title="Content" description="Plain text content used by the chatbot">
            <TextAreaField label="Content" rows={12} className="font-mono text-sm" {...register('content')} />
          </FormSection>

          <div className="flex gap-3">
            <Button type="submit" disabled={updateMutation.isPending || !isDirty} className="gap-1.5">
              {updateMutation.isPending ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <Save className="h-3.5 w-3.5" />}
              Save Changes
            </Button>
            <Button type="button" variant="outline" onClick={() => router.push(`/knowledge/${id}`)}>Cancel</Button>
          </div>
        </form>
      </div>
    </PageContainer>
  );
}
