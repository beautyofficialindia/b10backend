import React from 'react';
import { useForm, useWatch } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';

const followupSchema = z.object({
  date: z.string().min(1, 'Date is required'),
  time: z.string().min(1, 'Time is required'),
  followup_type: z.enum(['call', 'meeting', 'email', 'demo', 'other']),
  notes: z.string().optional(),
  reminder: z.string().optional(),
});

export type FollowUpFormData = z.infer<typeof followupSchema>;

interface FollowUpFormProps {
  initialData?: Partial<FollowUpFormData>;
  onSubmit: (data: FollowUpFormData) => void;
  isSubmitting?: boolean;
}

export const FollowUpForm: React.FC<FollowUpFormProps> = ({ initialData, onSubmit, isSubmitting }) => {
  const { register, handleSubmit, setValue, control, formState: { errors } } = useForm<FollowUpFormData>({
    resolver: zodResolver(followupSchema),
    defaultValues: {
      date: initialData?.date || '',
      time: initialData?.time || '',
      followup_type: initialData?.followup_type || 'call',
      notes: initialData?.notes || '',
      reminder: initialData?.reminder || '15_min',
    },
  });

  const followup_type = useWatch({ control, name: 'followup_type' });
  const reminder = useWatch({ control, name: 'reminder' });

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4 pt-4">
      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <label className="text-sm font-medium">Date</label>
          <Input type="date" {...register('date')} />
          {errors.date && <p className="text-xs text-red-500">{errors.date.message}</p>}
        </div>
        <div className="space-y-2">
          <label className="text-sm font-medium">Time</label>
          <Input type="time" {...register('time')} />
          {errors.time && <p className="text-xs text-red-500">{errors.time.message}</p>}
        </div>
      </div>

      <div className="space-y-2">
        <label className="text-sm font-medium">Type</label>
        <Select value={followup_type} onValueChange={(value: "call" | "meeting" | "email" | "demo" | "other" | null) => value && setValue('followup_type', value)}>
          <SelectTrigger>
            <SelectValue placeholder="Select type" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="call">Call</SelectItem>
            <SelectItem value="meeting">Meeting</SelectItem>
            <SelectItem value="email">Email</SelectItem>
            <SelectItem value="demo">Demo</SelectItem>
            <SelectItem value="other">Other</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <div className="space-y-2">
        <label className="text-sm font-medium">Notes</label>
        <Textarea 
          placeholder="Add details about this follow-up..." 
          className="min-h-[100px]"
          {...register('notes')} 
        />
      </div>

      <div className="space-y-2">
        <label className="text-sm font-medium">Reminder (UI Only)</label>
        <Select value={reminder} onValueChange={(value) => setValue('reminder', value as string)}>
          <SelectTrigger>
            <SelectValue placeholder="Select reminder" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="none">None</SelectItem>
            <SelectItem value="15_min">15 minutes before</SelectItem>
            <SelectItem value="30_min">30 minutes before</SelectItem>
            <SelectItem value="1_hour">1 hour before</SelectItem>
            <SelectItem value="1_day">1 day before</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <div className="flex justify-end pt-2">
        <Button type="submit" disabled={isSubmitting}>
          {isSubmitting ? 'Saving...' : 'Save Follow-up'}
        </Button>
      </div>
    </form>
  );
};
