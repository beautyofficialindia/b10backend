'use client';

import { use, useEffect, useMemo } from 'react';
import { useRouter } from 'next/navigation';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { PageContainer } from '@/components/layout';
import { ErrorState } from '@/components/common';
import { TextField, FormSection } from '@/components/forms';
import { EntitySelect, type Option } from '@/components/forms/entity-select';
import { Skeleton } from '@/components/ui/skeleton';
import { Button } from '@/components/ui/button';
import { ArrowLeft, Save, Loader2 } from 'lucide-react';
import { useKnowledgeDetail, useUpdateEntry, useCategories, useTags, useCreateTag, useCreateCategory } from '@/features/knowledge';
import { MarkdownEditor } from '@/features/knowledge/components/markdown-editor';

const schema = z.object({
  title: z.string().min(1, 'Title is required'),
  category: z.number().min(1, 'Category is required'),
  tags: z.array(z.number()).optional(),
  content: z.string(),
  sort_order: z.number().min(0).optional(),
});

type FormData = z.infer<typeof schema>;

export default function KnowledgeEditPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const router = useRouter();
  
  const { data, isLoading, isError, refetch } = useKnowledgeDetail(id);
  const updateMutation = useUpdateEntry();
  const createTagMutation = useCreateTag();
  const createCategoryMutation = useCreateCategory();

  const { data: categoriesResponse, isLoading: isLoadingCategories } = useCategories();
  const { data: tagsResponse, isLoading: isLoadingTags } = useTags();

  const categoryOptions = useMemo(() => {
    return categoriesResponse?.data?.map(c => ({ label: c.name, value: c.id })) || [];
  }, [categoriesResponse]);

  const tagOptions = useMemo(() => {
    return tagsResponse?.data?.map(t => ({ label: t.name, value: t.id })) || [];
  }, [tagsResponse]);

  const { register, handleSubmit, control, reset, formState: { errors, isDirty }, setValue, getValues } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: { title: '', content: '', tags: [] },
  });

  const entry = data?.data;

  useEffect(() => {
    if (entry) {
      reset({
        title: entry.title,
        category: entry.category?.id,
        tags: entry.tags?.map(t => t.id) || [],
        content: entry.content,
        sort_order: entry.sort_order,
      });
    }
  }, [entry, reset]);

  const onSubmit = (formData: FormData) => {
    updateMutation.mutate(
      { id, data: formData },
      { onSuccess: () => router.push(`/knowledge/${id}`) }
    );
  };

  const handleCreateTag = async (inputValue: string) => {
    try {
      const res = await createTagMutation.mutateAsync({ name: inputValue });
      const currentTags = getValues('tags') || [];
      setValue('tags', [...currentTags, res.id], { shouldDirty: true });
    } catch (err) {
      console.error('Failed to create tag', err);
    }
  };

  const handleCreateCategory = async (inputValue: string) => {
    try {
      const res = await createCategoryMutation.mutateAsync({ name: inputValue });
      setValue('category', res.id, { shouldDirty: true });
    } catch (err) {
      console.error('Failed to create category', err);
    }
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
            
            <Controller
              name="category"
              control={control}
              render={({ field }) => (
                <EntitySelect
                  label="Category"
                  required
                  isCreatable
                  options={categoryOptions}
                  isLoading={isLoadingCategories || createCategoryMutation.isPending}
                  value={categoryOptions.find(o => o.value === field.value) || null}
                  onChange={(selected: Option | readonly Option[] | null) => field.onChange((selected as Option)?.value || null)}
                  onCreateOption={handleCreateCategory}
                  error={errors.category?.message}
                  placeholder="Select or create category..."
                />
              )}
            />

            <Controller
              name="tags"
              control={control}
              render={({ field }) => (
                <EntitySelect
                  label="Tags"
                  options={tagOptions}
                  isLoading={isLoadingTags}
                  isMulti
                  isCreatable
                  value={tagOptions.filter(o => (field.value || []).includes(o.value as number))}
                  onChange={(selected: Option | readonly Option[] | null) => {
                    const values = ((selected as Option[]) || []).map((v: Option) => v.value);
                    field.onChange(values);
                  }}
                  onCreateOption={handleCreateTag}
                  error={errors.tags?.message}
                />
              )}
            />
          </FormSection>

          <FormSection title="Content" description="Markdown content used by the chatbot and preview">
            <Controller
              name="content"
              control={control}
              render={({ field }) => (
                <MarkdownEditor
                  value={field.value}
                  onChange={field.onChange}
                  placeholder="Write knowledge content in Markdown..."
                />
              )}
            />
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
