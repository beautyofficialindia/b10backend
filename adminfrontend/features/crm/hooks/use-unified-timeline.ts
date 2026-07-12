import { useMemo } from 'react';
import { 
  useLeadActivities, 
  useLeadStatusHistory, 
  useLeadFollowUps, 
  useLeadNotes 
} from '../api';
import { 
  adaptActivity, 
  adaptStatusHistory, 
  adaptFollowUp, 
  adaptNote 
} from '../utils';
import type { TimelineItem } from '../types';

export function useUnifiedTimeline(leadId: string) {
  const activities = useLeadActivities(leadId);
  const statusHistory = useLeadStatusHistory(leadId);
  const followUps = useLeadFollowUps(leadId);
  const notes = useLeadNotes(leadId);

  const isLoading = activities.isLoading || statusHistory.isLoading || followUps.isLoading || notes.isLoading;
  const isError = activities.isError || statusHistory.isError || followUps.isError || notes.isError;

  const refetch = () => {
    activities.refetch();
    statusHistory.refetch();
    followUps.refetch();
    notes.refetch();
  };

  const items = useMemo(() => {
    if (isLoading || isError) return [];

    const unified: TimelineItem[] = [];

    if (activities.data) {
      unified.push(...activities.data.map(adaptActivity));
    }
    if (statusHistory.data) {
      unified.push(...statusHistory.data.map(adaptStatusHistory));
    }
    if (followUps.data) {
      unified.push(...followUps.data.map(adaptFollowUp));
    }
    if (notes.data) {
      unified.push(...notes.data.map(adaptNote));
    }

    return unified.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());
  }, [
    activities.data, 
    statusHistory.data, 
    followUps.data, 
    notes.data, 
    isLoading, 
    isError
  ]);

  return {
    items,
    isLoading,
    isError,
    refetch,
  };
}
