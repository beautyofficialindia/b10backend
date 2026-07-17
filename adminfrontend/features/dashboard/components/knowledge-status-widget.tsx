"use client";

import { useKnowledgeStatus } from "../hooks/use-dashboard";
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from "@/components/ui/card";
import { Loader2, BookOpen, FileEdit, Archive } from "lucide-react";

export function KnowledgeStatusWidget() {
  const { data, isLoading, isError } = useKnowledgeStatus(true);

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Knowledge Base Status</CardTitle>
          <CardDescription>Current state of your articles.</CardDescription>
        </CardHeader>
        <CardContent className="flex justify-center py-6">
          <Loader2 className="h-5 w-5 animate-spin text-muted-foreground" />
        </CardContent>
      </Card>
    );
  }

  if (isError || !data?.data) {
    return null;
  }

  const { draft, published, archived } = data.data;

  return (
    <Card>
      <CardHeader>
        <CardTitle>Knowledge Base Status</CardTitle>
        <CardDescription>Current state of your articles.</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-3 gap-4">
          <div className="flex flex-col items-center justify-center p-4 bg-muted/50 rounded-lg">
            <BookOpen className="h-5 w-5 text-green-500 mb-2" />
            <span className="text-2xl font-bold">{published}</span>
            <span className="text-xs text-muted-foreground uppercase tracking-wider mt-1">Published</span>
          </div>
          <div className="flex flex-col items-center justify-center p-4 bg-muted/50 rounded-lg">
            <FileEdit className="h-5 w-5 text-orange-500 mb-2" />
            <span className="text-2xl font-bold">{draft}</span>
            <span className="text-xs text-muted-foreground uppercase tracking-wider mt-1">Drafts</span>
          </div>
          <div className="flex flex-col items-center justify-center p-4 bg-muted/50 rounded-lg">
            <Archive className="h-5 w-5 text-gray-500 mb-2" />
            <span className="text-2xl font-bold">{archived}</span>
            <span className="text-xs text-muted-foreground uppercase tracking-wider mt-1">Archived</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
