'use client';

import { useRouter } from 'next/navigation';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { PageContainer } from '@/components/layout';
import { TextField, FormSection } from '@/components/forms';
import { EntitySelect, type Option } from '@/components/forms/entity-select';
import { Button } from '@/components/ui/button';
import { ArrowLeft, Save, Loader2, Play } from 'lucide-react';
import { useCreateEntry, useCategories, useTags, useCreateTag } from '@/features/knowledge';
import { MarkdownEditor } from '@/features/knowledge/components/markdown-editor';
import { useMemo } from 'react';

const schema = z.object({
  title: z.string().min(1, 'Title is required'),
  category: z.number().min(1, 'Category is required'),
  tags: z.array(z.number()).optional(),
  content: z.string(),
});

type FormData = z.infer<typeof schema>;

export default function KnowledgeNewPage() {
  const router = useRouter();
  const createMutation = useCreateEntry();
  const createTagMutation = useCreateTag();

  const { data: categoriesResponse, isLoading: isLoadingCategories } = useCategories();
  const { data: tagsResponse, isLoading: isLoadingTags } = useTags();

  const categoryOptions = useMemo(() => {
    return categoriesResponse?.data?.map(c => ({ label: c.name, value: c.id })) || [];
  }, [categoriesResponse]);

  const tagOptions = useMemo(() => {
    return tagsResponse?.data?.map(t => ({ label: t.name, value: t.id })) || [];
  }, [tagsResponse]);

  const { register, handleSubmit, control, formState: { errors }, setValue, getValues } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: { title: '', content: '', tags: [] },
  });

  const onSubmit = (formData: FormData, status: 'draft' | 'published') => {
    createMutation.mutate(
      { title: formData.title, category: formData.category, tags: formData.tags, content: formData.content, status },
      { onSuccess: (res) => router.push(`/knowledge/${res.data.id}`) }
    );
  };

  const handleCreateTag = async (inputValue: string) => {
    try {
      const slug = inputValue.toLowerCase().replace(/[^a-z0-9]+/g, '-');
      const res = await createTagMutation.mutateAsync({ name: inputValue, slug });
      const currentTags = getValues('tags') || [];
      setValue('tags', [...currentTags, res.data.id]);
    } catch (err) {
      console.error('Failed to create tag', err);
    }
  };

  return (
    <PageContainer>
      <Button variant="ghost" size="sm" className="gap-1.5 -ml-2 mb-2" onClick={() => router.push('/knowledge')}>
        <ArrowLeft className="h-3.5 w-3.5" />Back to Knowledge Base
      </Button>

      <div className="max-w-2xl">
        <h1 className="text-xl font-semibold mb-6">New Entry</h1>

        <form className="space-y-6">
          <FormSection title="Details">
            <TextField label="Title" error={errors.title?.message} required placeholder="Entry title..." {...register('title')} />
            
            <Controller
              name="category"
              control={control}
              render={({ field }) => (
                <EntitySelect
                  label="Category"
                  required
                  error={errors.category?.message}
                  isLoading={isLoadingCategories}
                  options={categoryOptions}
                  value={categoryOptions.find(o => o.value === field.value) || null}
                  onChange={(option: Option | readonly Option[] | null) => field.onChange((option as Option)?.value || null)}
                  placeholder="Select category..."
                />
              )}
            />

            <Controller
              name="tags"
              control={control}
              render={({ field }) => (
                <EntitySelect
                  label="Tags"
                  isMulti
                  isCreatable
                  isLoading={isLoadingTags || createTagMutation.isPending}
                  options={tagOptions}
                  value={tagOptions.filter(o => field.value?.includes(o.value as number))}
                  onChange={(options: Option | readonly Option[] | null) => {
                    field.onChange((options as Option[] || []).map(o => o.value as number));
                  }}
                  onCreateOption={handleCreateTag}
                  placeholder="Select or create tags..."
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
            <Button 
              type="button"
              onClick={handleSubmit((data) => onSubmit(data, 'draft'))}
              disabled={createMutation.isPending} 
              className="gap-1.5"
            >
              {createMutation.isPending ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <Save className="h-3.5 w-3.5" />}
              Save Draft
            </Button>
            <Button 
              type="button"
              onClick={handleSubmit((data) => onSubmit(data, 'published'))}
              disabled={createMutation.isPending}
              variant="default" 
              className="gap-1.5 bg-emerald-600 hover:bg-emerald-700"
            >
              <Play className="h-3.5 w-3.5" />
              Publish Now
            </Button>
            <Button type="button" variant="outline" onClick={() => router.push('/knowledge')}>Cancel</Button>
          </div>
        </form>
      </div>
    </PageContainer>
  );
}
