"use client";

import { usePendingFollowups } from "../hooks/use-dashboard";
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from "@/components/ui/card";
import { Loader2, Calendar, Clock } from "lucide-react";

export function PendingFollowups() {
  const { data, isLoading, isError } = usePendingFollowups(true);

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Pending Follow-ups</CardTitle>
          <CardDescription>Scheduled tasks that need your attention.</CardDescription>
        </CardHeader>
        <CardContent className="flex justify-center py-6">
          <Loader2 className="h-5 w-5 animate-spin text-muted-foreground" />
        </CardContent>
      </Card>
    );
  }

  if (isError || !data?.results) {
    return null;
  }

  const followups = data.results;

  return (
    <Card>
      <CardHeader>
        <CardTitle>Pending Follow-ups</CardTitle>
        <CardDescription>Scheduled tasks that need your attention.</CardDescription>
      </CardHeader>
      <CardContent>
        {followups.length === 0 ? (
          <div className="text-center py-6 text-sm text-muted-foreground">
            No pending follow-ups. You&apos;re all caught up!
          </div>
        ) : (
          <div className="space-y-4">
            {followups.slice(0, 5).map((followup) => (
              <div key={followup.id} className="flex items-start justify-between border-b pb-4 last:border-0 last:pb-0">
                <div>
                  <p className="font-medium text-sm">{followup.followup_type.replace('_', ' ').toUpperCase()}</p>
                  <p className="text-xs text-muted-foreground mt-1 truncate max-w-[200px]">{followup.notes || 'No notes provided'}</p>
                </div>
                <div className="flex flex-col items-end gap-1">
                  <div className="flex items-center text-xs text-orange-500 font-medium">
                    <Calendar className="mr-1 h-3 w-3" />
                    {new Date(followup.scheduled_at).toLocaleDateString()}
                  </div>
                  <div className="flex items-center text-xs text-muted-foreground">
                    <Clock className="mr-1 h-3 w-3" />
                    {new Date(followup.scheduled_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
