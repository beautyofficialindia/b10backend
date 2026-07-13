import * as React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Textarea } from '@/components/ui/textarea';
import { cn } from '@/lib/utils';

export interface MarkdownEditorProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  className?: string;
}

export function MarkdownEditor({
  value,
  onChange,
  placeholder = 'Write in Markdown...',
  className,
}: MarkdownEditorProps) {
  return (
    <div className={cn("border rounded-md overflow-hidden bg-background", className)}>
      <Tabs defaultValue="write" className="w-full">
        <div className="border-b px-2 py-1 bg-muted/20">
          <TabsList className="bg-transparent h-8">
            <TabsTrigger value="write" className="text-xs data-[state=active]:bg-background">Write</TabsTrigger>
            <TabsTrigger value="preview" className="text-xs data-[state=active]:bg-background">Preview</TabsTrigger>
          </TabsList>
        </div>
        <TabsContent value="write" className="p-0 m-0 border-none outline-none">
          <Textarea
            value={value}
            onChange={(e) => onChange(e.target.value)}
            placeholder={placeholder}
            className="min-h-[300px] border-none focus-visible:ring-0 rounded-none resize-y shadow-none p-4 font-mono text-sm"
          />
        </TabsContent>
        <TabsContent value="preview" className="p-0 m-0">
          <div className="min-h-[300px] p-4 prose prose-sm dark:prose-invert max-w-none break-words">
            {value ? (
              <ReactMarkdown remarkPlugins={[remarkGfm]}>{value}</ReactMarkdown>
            ) : (
              <span className="text-muted-foreground italic">Nothing to preview</span>
            )}
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
