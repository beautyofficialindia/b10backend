"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { AlertTriangle, DatabaseZap, RefreshCw, Loader2 } from "lucide-react";
import { useInitializeSettings, useRefreshSettingsCache, useClearSettingsCache, useResetSettings } from "../hooks";
import { toast } from "sonner";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";

export function SettingsManagement() {
  const [resetConfirmText, setResetConfirmText] = useState("");
  const [isResetDialogOpen, setIsResetDialogOpen] = useState(false);
  const [isInitDialogOpen, setIsInitDialogOpen] = useState(false);

  const initMutation = useInitializeSettings();
  const refreshMutation = useRefreshSettingsCache();
  const clearMutation = useClearSettingsCache();
  const resetMutation = useResetSettings();

  const handleInitialize = () => {
    initMutation.mutate(undefined, {
      onSuccess: (data) => {
        setIsInitDialogOpen(false);
        if (data && data.created > 0) {
          toast.success(`Successfully initialized ${data.created} missing platform settings.`);
        } else {
          toast.success("All platform settings are already initialized.");
        }
      },
      onError: () => {
        setIsInitDialogOpen(false);
        toast.error("Failed to initialize platform settings. Please try again.");
      }
    });
  };

  const handleReset = () => {
    if (resetConfirmText !== "RESET_PLATFORM_SETTINGS") return;
    
    resetMutation.mutate({ confirm: resetConfirmText }, {
      onSuccess: () => {
        setIsResetDialogOpen(false);
        setResetConfirmText("");
        toast.success("Platform settings have been reset to defaults");
      },
    });
  };

  return (
    <div className="space-y-6 max-w-4xl">
      <div className="pb-4 border-b">
        <h2 className="text-2xl font-semibold tracking-tight">Advanced Settings</h2>
        <p className="text-sm text-muted-foreground mt-1">
          Manage cache, initialize configurations, and perform maintenance actions.
        </p>
      </div>

      <div className="border rounded-md divide-y bg-card px-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between py-6 group">
          <div className="space-y-1 pr-4 max-w-[70%]">
            <h4 className="text-sm font-medium text-foreground flex items-center gap-2">
              <DatabaseZap className="w-4 h-4 text-blue-500" />
              Initialize Platform Settings
            </h4>
            <p className="text-sm text-muted-foreground leading-relaxed">
              Seed missing platform settings from the defaults file. Existing settings are preserved and will not be overwritten.
            </p>
          </div>
          <div className="mt-4 sm:mt-0 flex shrink-0">
            <Button 
              variant="outline"
              disabled={initMutation.isPending}
              onClick={() => setIsInitDialogOpen(true)}
            >
              {initMutation.isPending ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Initializing...
                </>
              ) : (
                "Initialize"
              )}
            </Button>
            <Dialog open={isInitDialogOpen} onOpenChange={setIsInitDialogOpen}>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Initialize Platform Settings</DialogTitle>
                  <DialogDescription>
                    Seed missing platform settings from the defaults file.
                  </DialogDescription>
                </DialogHeader>
                <div className="space-y-4 pt-4 text-foreground text-sm">
                  <p>This action will:</p>
                  <ul className="list-disc pl-6 space-y-1">
                    <li>Create any missing platform settings.</li>
                    <li>Preserve all existing values.</li>
                    <li>Never overwrite configured settings.</li>
                  </ul>
                  <p>This operation is safe and can be run multiple times.</p>
                  <p className="pt-2 font-medium">Do you want to continue?</p>
                </div>
                <DialogFooter>
                  <Button variant="outline" onClick={() => setIsInitDialogOpen(false)}>
                    Cancel
                  </Button>
                  <Button onClick={handleInitialize} disabled={initMutation.isPending}>
                    Initialize Settings
                  </Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>
          </div>
        </div>

        <div className="flex flex-col sm:flex-row sm:items-center justify-between py-6 group">
          <div className="space-y-1 pr-4 max-w-[70%]">
            <h4 className="text-sm font-medium text-foreground flex items-center gap-2">
              <RefreshCw className="w-4 h-4 text-green-500" />
              Cache Management
            </h4>
            <p className="text-sm text-muted-foreground leading-relaxed">
              Refresh or clear the settings cache. Cache is normally invalidated automatically, but this can resolve synchronization issues.
            </p>
          </div>
          <div className="mt-4 sm:mt-0 flex gap-2 shrink-0">
            <Button 
              variant="secondary"
              onClick={() => refreshMutation.mutate({})} 
              disabled={refreshMutation.isPending}
            >
              Refresh Cache
            </Button>
            <Button 
              variant="outline"
              onClick={() => clearMutation.mutate({})} 
              disabled={clearMutation.isPending}
            >
              Clear Cache
            </Button>
          </div>
        </div>

        <div className="flex flex-col sm:flex-row sm:items-center justify-between py-6 group">
          <div className="space-y-1 pr-4 max-w-[70%]">
            <h4 className="text-sm font-medium text-destructive flex items-center gap-2">
              <AlertTriangle className="w-4 h-4" />
              Danger Zone
            </h4>
            <p className="text-sm text-muted-foreground leading-relaxed">
              Reset all platform settings to their system defaults. This action is destructive and cannot be undone.
            </p>
          </div>
          <div className="mt-4 sm:mt-0 flex shrink-0">
            <Dialog open={isResetDialogOpen} onOpenChange={setIsResetDialogOpen}>
              <Button variant="destructive" onClick={() => setIsResetDialogOpen(true)}>
                Reset Platform Settings
              </Button>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Are you absolutely sure?</DialogTitle>
                  <DialogDescription>
                    This action cannot be undone. This will permanently reset all platform 
                    settings back to their factory defaults. Any customizations will be lost.
                  </DialogDescription>
                </DialogHeader>
                <div className="my-4 space-y-2">
                  <p className="text-sm font-medium">
                    Type <span className="font-mono bg-muted px-1 py-0.5 rounded">RESET_PLATFORM_SETTINGS</span> to confirm.
                  </p>
                  <Input 
                    value={resetConfirmText}
                    onChange={(e) => setResetConfirmText(e.target.value)}
                    placeholder="RESET_PLATFORM_SETTINGS"
                  />
                </div>
                <DialogFooter>
                  <Button variant="outline" onClick={() => setIsResetDialogOpen(false)}>
                    Cancel
                  </Button>
                  <Button 
                    variant="destructive" 
                    onClick={handleReset}
                    disabled={resetConfirmText !== "RESET_PLATFORM_SETTINGS" || resetMutation.isPending}
                  >
                    {resetMutation.isPending ? "Resetting..." : "Confirm Reset"}
                  </Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>
          </div>
        </div>
      </div>
    </div>
  );
}
