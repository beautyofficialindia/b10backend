'use client';

import { useState } from 'react';
import { PageContainer, PageHeader } from '@/components/layout';
import { PermissionGuard } from '@/features/auth';
import { ErrorState } from '@/components/common';
import { Skeleton } from '@/components/ui/skeleton';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Switch } from '@/components/ui/switch';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs';
import { Save, Loader2, Eye, EyeOff } from 'lucide-react';
import { useSettingsCategory, useUpdateSettings, SETTING_CATEGORIES, type Setting, type SettingCategory } from '@/features/settings';

function SettingField({ setting, value, onChange }: { setting: Setting; value: unknown; onChange: (v: unknown) => void }) {
  const [showSecret, setShowSecret] = useState(false);

  // Secret masked field
  if (typeof value === 'object' && value !== null && 'is_set' in (value as Record<string, unknown>)) {
    return (
      <div className="space-y-1.5">
        <label className="text-sm font-medium">{setting.key.replace(/_/g, ' ')}</label>
        {setting.description && <p className="text-xs text-muted-foreground">{setting.description}</p>}
        <div className="flex items-center gap-2">
          <Input
            type={showSecret ? 'text' : 'password'}
            placeholder={(value as { is_set: boolean }).is_set ? '••••••••' : 'Not set'}
            onChange={(e) => onChange(e.target.value || null)}
            className="font-mono text-sm"
          />
          <Button variant="ghost" size="icon" className="h-9 w-9 shrink-0" onClick={() => setShowSecret(!showSecret)}>
            {showSecret ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
          </Button>
        </div>
      </div>
    );
  }

  // Boolean
  if (typeof value === 'boolean') {
    return (
      <div className="flex items-center justify-between gap-4 py-1">
        <div>
          <p className="text-sm font-medium">{setting.key.replace(/_/g, ' ')}</p>
          {setting.description && <p className="text-xs text-muted-foreground">{setting.description}</p>}
        </div>
        <Switch checked={value} onCheckedChange={(v) => onChange(v)} />
      </div>
    );
  }

  // Number
  if (typeof value === 'number') {
    return (
      <div className="space-y-1.5">
        <label className="text-sm font-medium">{setting.key.replace(/_/g, ' ')}</label>
        {setting.description && <p className="text-xs text-muted-foreground">{setting.description}</p>}
        <Input type="number" value={value} onChange={(e) => onChange(Number(e.target.value))} />
      </div>
    );
  }

  // Object/Array — JSON textarea
  if (typeof value === 'object' && value !== null) {
    return (
      <div className="space-y-1.5">
        <label className="text-sm font-medium">{setting.key.replace(/_/g, ' ')}</label>
        {setting.description && <p className="text-xs text-muted-foreground">{setting.description}</p>}
        <Textarea
          value={JSON.stringify(value, null, 2)}
          onChange={(e) => { try { onChange(JSON.parse(e.target.value)); } catch { /* invalid JSON */ } }}
          rows={4}
          className="font-mono text-xs"
        />
      </div>
    );
  }

  // Long text
  const strValue = String(value ?? '');
  if (strValue.length > 100) {
    return (
      <div className="space-y-1.5">
        <label className="text-sm font-medium">{setting.key.replace(/_/g, ' ')}</label>
        {setting.description && <p className="text-xs text-muted-foreground">{setting.description}</p>}
        <Textarea value={strValue} onChange={(e) => onChange(e.target.value)} rows={3} />
      </div>
    );
  }

  // Default: text input
  return (
    <div className="space-y-1.5">
      <label className="text-sm font-medium">{setting.key.replace(/_/g, ' ')}</label>
      {setting.description && <p className="text-xs text-muted-foreground">{setting.description}</p>}
      <Input value={strValue} onChange={(e) => onChange(e.target.value)} />
    </div>
  );
}

function CategoryPanel({ category }: { category: SettingCategory }) {
  const { data, isLoading, isError, refetch } = useSettingsCategory(category);
  const updateMutation = useUpdateSettings();
  const [edits, setEdits] = useState<Record<string, unknown>>({});

  const settings = data?.data || [];
  const hasEdits = Object.keys(edits).length > 0;

  const handleChange = (key: string, value: unknown) => {
    setEdits(prev => ({ ...prev, [key]: value }));
  };

  const handleSave = () => {
    updateMutation.mutate(
      { category, settings: edits },
      { onSuccess: () => setEdits({}) }
    );
  };

  if (isLoading) return <div className="space-y-4">{Array.from({length: 4}).map((_, i) => <Skeleton key={i} className="h-16 w-full" />)}</div>;
  if (isError) return <ErrorState message="Failed to load settings" onRetry={() => refetch()} />;

  return (
    <div className="space-y-5">
      {hasEdits && (
        <div className="flex items-center gap-2 p-3 rounded-lg bg-muted sticky top-0 z-10">
          <span className="text-sm font-medium">Unsaved changes</span>
          <Button size="sm" onClick={handleSave} disabled={updateMutation.isPending} className="gap-1.5">
            {updateMutation.isPending ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <Save className="h-3.5 w-3.5" />}
            Save
          </Button>
          <Button size="sm" variant="ghost" onClick={() => setEdits({})}>Discard</Button>
        </div>
      )}

      {settings.map(setting => (
        <SettingField
          key={setting.key}
          setting={setting}
          value={edits[setting.key] !== undefined ? edits[setting.key] : setting.value}
          onChange={(v) => handleChange(setting.key, v)}
        />
      ))}

      {settings.length === 0 && (
        <p className="text-sm text-muted-foreground py-8 text-center">No settings in this category</p>
      )}
    </div>
  );
}

export default function SettingsPage() {
  return (
    <PermissionGuard permissions={['settings_management.view_setting']}>
    <PageContainer>
      <PageHeader title="Settings" description="Configure platform behavior and integrations" />

      <Tabs defaultValue="GENERAL">
        <TabsList className="flex-wrap h-auto gap-1">
          {SETTING_CATEGORIES.map(cat => (
            <TabsTrigger key={cat.value} value={cat.value} className="text-xs">
              {cat.label}
            </TabsTrigger>
          ))}
        </TabsList>

        {SETTING_CATEGORIES.map(cat => (
          <TabsContent key={cat.value} value={cat.value} className="mt-4">
            <div className="rounded-xl border bg-card p-5 shadow-sm">
              <div className="mb-4">
                <h2 className="text-sm font-medium">{cat.label}</h2>
                <p className="text-xs text-muted-foreground">{cat.description}</p>
              </div>
              <CategoryPanel category={cat.value} />
            </div>
          </TabsContent>
        ))}
      </Tabs>
    </PageContainer>
    </PermissionGuard>
  );
}
