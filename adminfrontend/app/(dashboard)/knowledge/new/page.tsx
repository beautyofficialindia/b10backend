'use client';

import { useRouter } from 'next/navigation';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { PageContainer } from '@/components/layout';
import { TextField, TextAreaField, FormSection } from '@/components/forms';
import { Button } from '@/components/ui/button';
import { ArrowLeft, Save, Loader2 } from 'lucide-react';
import { useCreateEntry, type KBCategory } from '@/features/knowledge';

const schema = z.object({
  title: z.string().min(1, 'Title is required'),
  category: z.string().min(1, 'Category is required'),
  content: z.string(),
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

export default function KnowledgeNewPage() {
  const router = useRouter();
  const createMutation = useCreateEntry();

  const { register, handleSubmit, formState: { errors } } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: { title: '', category: 'general', content: '' },
  });

  const onSubmit = (formData: FormData) => {
    createMutation.mutate(
      { title: formData.title, category: formData.category as KBCategory, content: formData.content },
      { onSuccess: (res) => router.push(`/knowledge/${res.data.id}`) }
    );
  };

  return (
    <PageContainer>
      <Button variant="ghost" size="sm" className="gap-1.5 -ml-2 mb-2" onClick={() => router.push('/knowledge')}>
        <ArrowLeft className="h-3.5 w-3.5" />Back to Knowledge Base
      </Button>

      <div className="max-w-2xl">
        <h1 className="text-xl font-semibold mb-6">New Entry</h1>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
          <FormSection title="Details">
            <TextField label="Title" error={errors.title?.message} required placeholder="Entry title..." {...register('title')} />
            <div className="space-y-1.5">
              <label className="text-sm font-medium">Category <span className="text-destructive">*</span></label>
              <select {...register('category')} className="w-full h-9 rounded-md border bg-background px-3 text-sm">
                {categories.map(c => <option key={c.value} value={c.value}>{c.label}</option>)}
              </select>
            </div>
          </FormSection>

          <FormSection title="Content" description="Plain text content used by the chatbot">
            <TextAreaField label="Content" rows={12} placeholder="Write knowledge content..." className="font-mono text-sm" {...register('content')} />
          </FormSection>

          <div className="flex gap-3">
            <Button type="submit" disabled={createMutation.isPending} className="gap-1.5">
              {createMutation.isPending ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <Save className="h-3.5 w-3.5" />}
              Create Entry
            </Button>
            <Button type="button" variant="outline" onClick={() => router.push('/knowledge')}>Cancel</Button>
          </div>
        </form>
      </div>
    </PageContainer>
  );
}
