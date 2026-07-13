'use client';

import React from 'react';
import Select, { Props as SelectProps, StylesConfig } from 'react-select';
import CreatableSelect from 'react-select/creatable';
import { FieldWrapper } from './form-fields';

export const selectStyles: StylesConfig<Option, boolean> = {
  control: (base, state) => ({
    ...base,
    background: 'transparent',
    borderColor: state.isFocused ? 'hsl(var(--ring))' : 'hsl(var(--input))',
    boxShadow: state.isFocused ? '0 0 0 1px hsl(var(--ring))' : 'none',
    '&:hover': {
      borderColor: state.isFocused ? 'hsl(var(--ring))' : 'hsl(var(--input))',
    },
    borderRadius: 'calc(var(--radius) - 2px)',
    minHeight: '2.25rem',
  }),
  menu: (base) => ({
    ...base,
    backgroundColor: 'hsl(var(--popover))',
    border: '1px solid hsl(var(--border))',
    boxShadow: 'var(--shadow-md)',
    borderRadius: 'calc(var(--radius) - 2px)',
    zIndex: 50,
  }),
  option: (base, state) => ({
    ...base,
    backgroundColor: state.isSelected
      ? 'hsl(var(--accent))'
      : state.isFocused
      ? 'hsl(var(--accent) / 0.5)'
      : 'transparent',
    color: state.isSelected ? 'hsl(var(--accent-foreground))' : 'hsl(var(--foreground))',
    '&:active': {
      backgroundColor: 'hsl(var(--accent))',
    },
    cursor: 'pointer',
  }),
  singleValue: (base) => ({
    ...base,
    color: 'hsl(var(--foreground))',
  }),
  multiValue: (base) => ({
    ...base,
    backgroundColor: 'hsl(var(--secondary))',
    borderRadius: 'calc(var(--radius) - 4px)',
  }),
  multiValueLabel: (base) => ({
    ...base,
    color: 'hsl(var(--secondary-foreground))',
  }),
  multiValueRemove: (base) => ({
    ...base,
    color: 'hsl(var(--secondary-foreground))',
    ':hover': {
      backgroundColor: 'hsl(var(--destructive))',
      color: 'hsl(var(--destructive-foreground))',
    },
  }),
  input: (base) => ({
    ...base,
    color: 'hsl(var(--foreground))',
  }),
};

export interface Option {
  label: string;
  value: string | number;
}

interface EntitySelectProps extends Omit<SelectProps<Option, boolean>, 'options' | 'value' | 'onChange'> {
  label?: string;
  error?: string;
  description?: string;
  required?: boolean;
  options: Option[];
  isLoading?: boolean;
  isCreatable?: boolean;
  value?: Option | Option[] | null;
  onChange?: (value: Option | readonly Option[] | null) => void;
  onCreateOption?: (inputValue: string) => void;
}

export function EntitySelect({
  label,
  error,
  description,
  required,
  options,
  isLoading,
  isCreatable,
  value,
  onChange,
  onCreateOption,
  ...props
}: EntitySelectProps) {
  const Component = isCreatable ? CreatableSelect : Select;

  return (
    <FieldWrapper label={label} error={error} description={description} required={required}>
      <Component
        options={options}
        isLoading={isLoading}
        styles={selectStyles}
        classNamePrefix="react-select"
        value={value}
        onChange={onChange}
        onCreateOption={onCreateOption}
        {...(props as SelectProps<Option, boolean>)}
      />
    </FieldWrapper>
  );
}
