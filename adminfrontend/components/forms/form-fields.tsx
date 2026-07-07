'use client';

import { forwardRef } from 'react';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Checkbox } from '@/components/ui/checkbox';
import { Switch } from '@/components/ui/switch';
import { cn } from '@/lib/utils';
import { Eye, EyeOff, Search } from 'lucide-react';
import { useState } from 'react';

// ─── Field wrapper ────────────────────────────────────────────────

interface FieldWrapperProps {
  label?: string;
  error?: string;
  description?: string;
  required?: boolean;
  children: React.ReactNode;
  className?: string;
}

export function FieldWrapper({ label, error, description, required, children, className }: FieldWrapperProps) {
  return (
    <div className={cn('space-y-1.5', className)}>
      {label && (
        <label className="text-sm font-medium leading-none">
          {label}
          {required && <span className="text-destructive ml-0.5">*</span>}
        </label>
      )}
      {children}
      {description && !error && (
        <p className="text-xs text-muted-foreground">{description}</p>
      )}
      {error && <p className="text-xs text-destructive">{error}</p>}
    </div>
  );
}

// ─── TextField ────────────────────────────────────────────────────

interface TextFieldProps extends React.ComponentProps<typeof Input> {
  label?: string;
  error?: string;
  description?: string;
}

export const TextField = forwardRef<HTMLInputElement, TextFieldProps>(
  ({ label, error, description, required, className, ...props }, ref) => (
    <FieldWrapper label={label} error={error} description={description} required={required}>
      <Input ref={ref} className={cn(error && 'border-destructive', className)} {...props} />
    </FieldWrapper>
  )
);
TextField.displayName = 'TextField';

// ─── PasswordField ────────────────────────────────────────────────

interface PasswordFieldProps extends Omit<React.ComponentProps<typeof Input>, 'type'> {
  label?: string;
  error?: string;
  description?: string;
}

export const PasswordField = forwardRef<HTMLInputElement, PasswordFieldProps>(
  ({ label, error, description, required, className, ...props }, ref) => {
    const [show, setShow] = useState(false);
    return (
      <FieldWrapper label={label} error={error} description={description} required={required}>
        <div className="relative">
          <Input
            ref={ref}
            type={show ? 'text' : 'password'}
            className={cn('pr-9', error && 'border-destructive', className)}
            {...props}
          />
          <button
            type="button"
            onClick={() => setShow(!show)}
            className="absolute right-2.5 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
            aria-label={show ? 'Hide password' : 'Show password'}
          >
            {show ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
          </button>
        </div>
      </FieldWrapper>
    );
  }
);
PasswordField.displayName = 'PasswordField';

// ─── SearchField ──────────────────────────────────────────────────

interface SearchFieldProps extends React.ComponentProps<typeof Input> {
  label?: string;
}

export const SearchField = forwardRef<HTMLInputElement, SearchFieldProps>(
  ({ label, className, ...props }, ref) => (
    <FieldWrapper label={label}>
      <div className="relative">
        <Search className="absolute left-2.5 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
        <Input ref={ref} type="search" className={cn('pl-8', className)} {...props} />
      </div>
    </FieldWrapper>
  )
);
SearchField.displayName = 'SearchField';

// ─── TextAreaField ────────────────────────────────────────────────

interface TextAreaFieldProps extends React.ComponentProps<typeof Textarea> {
  label?: string;
  error?: string;
  description?: string;
}

export const TextAreaField = forwardRef<HTMLTextAreaElement, TextAreaFieldProps>(
  ({ label, error, description, required, className, ...props }, ref) => (
    <FieldWrapper label={label} error={error} description={description} required={required}>
      <Textarea ref={ref} className={cn(error && 'border-destructive', className)} {...props} />
    </FieldWrapper>
  )
);
TextAreaField.displayName = 'TextAreaField';

// ─── CheckboxField ────────────────────────────────────────────────

interface CheckboxFieldProps {
  label: string;
  description?: string;
  checked?: boolean;
  onCheckedChange?: (checked: boolean) => void;
  className?: string;
}

export function CheckboxField({ label, description, checked, onCheckedChange, className }: CheckboxFieldProps) {
  return (
    <label className={cn('flex items-start gap-3 cursor-pointer', className)}>
      <Checkbox checked={checked} onCheckedChange={onCheckedChange} className="mt-0.5" />
      <div>
        <span className="text-sm font-medium">{label}</span>
        {description && <p className="text-xs text-muted-foreground mt-0.5">{description}</p>}
      </div>
    </label>
  );
}

// ─── SwitchField ──────────────────────────────────────────────────

interface SwitchFieldProps {
  label: string;
  description?: string;
  checked?: boolean;
  onCheckedChange?: (checked: boolean) => void;
  className?: string;
}

export function SwitchField({ label, description, checked, onCheckedChange, className }: SwitchFieldProps) {
  return (
    <div className={cn('flex items-center justify-between gap-4', className)}>
      <div>
        <span className="text-sm font-medium">{label}</span>
        {description && <p className="text-xs text-muted-foreground mt-0.5">{description}</p>}
      </div>
      <Switch checked={checked} onCheckedChange={onCheckedChange} />
    </div>
  );
}

// ─── FormSection ──────────────────────────────────────────────────

interface FormSectionProps {
  title: string;
  description?: string;
  children: React.ReactNode;
  className?: string;
}

export function FormSection({ title, description, children, className }: FormSectionProps) {
  return (
    <div className={cn('space-y-4', className)}>
      <div>
        <h3 className="text-sm font-medium">{title}</h3>
        {description && <p className="text-xs text-muted-foreground mt-0.5">{description}</p>}
      </div>
      <div className="space-y-4">{children}</div>
    </div>
  );
}
