import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { CheckCircle2, XCircle, AlertTriangle, Info } from 'lucide-react';
import { cn } from '@/lib/utils';

interface AlertProps {
  title?: string;
  message: string;
  className?: string;
}

export function SuccessAlert({ title, message, className }: AlertProps) {
  return (
    <Alert className={cn('border-emerald-200 bg-emerald-50 dark:border-emerald-800 dark:bg-emerald-950/30', className)}>
      <CheckCircle2 className="h-4 w-4 text-emerald-600 dark:text-emerald-400" />
      {title && <AlertTitle className="text-emerald-800 dark:text-emerald-200">{title}</AlertTitle>}
      <AlertDescription className="text-emerald-700 dark:text-emerald-300">{message}</AlertDescription>
    </Alert>
  );
}

export function ErrorAlert({ title, message, className }: AlertProps) {
  return (
    <Alert className={cn('border-red-200 bg-red-50 dark:border-red-800 dark:bg-red-950/30', className)}>
      <XCircle className="h-4 w-4 text-red-600 dark:text-red-400" />
      {title && <AlertTitle className="text-red-800 dark:text-red-200">{title}</AlertTitle>}
      <AlertDescription className="text-red-700 dark:text-red-300">{message}</AlertDescription>
    </Alert>
  );
}

export function WarningAlert({ title, message, className }: AlertProps) {
  return (
    <Alert className={cn('border-amber-200 bg-amber-50 dark:border-amber-800 dark:bg-amber-950/30', className)}>
      <AlertTriangle className="h-4 w-4 text-amber-600 dark:text-amber-400" />
      {title && <AlertTitle className="text-amber-800 dark:text-amber-200">{title}</AlertTitle>}
      <AlertDescription className="text-amber-700 dark:text-amber-300">{message}</AlertDescription>
    </Alert>
  );
}

export function InfoAlert({ title, message, className }: AlertProps) {
  return (
    <Alert className={cn('border-blue-200 bg-blue-50 dark:border-blue-800 dark:bg-blue-950/30', className)}>
      <Info className="h-4 w-4 text-blue-600 dark:text-blue-400" />
      {title && <AlertTitle className="text-blue-800 dark:text-blue-200">{title}</AlertTitle>}
      <AlertDescription className="text-blue-700 dark:text-blue-300">{message}</AlertDescription>
    </Alert>
  );
}
