"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { AlertTriangle, DatabaseZap, RefreshCw } from "lucide-react";
import { useInitializeSettings, useRefreshSettingsCache, useClearSettingsCache, useResetSettings } from "../hooks";
import { toast } from "sonner";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";

export function SettingsManagement() {
  const [resetConfirmText, setResetConfirmText] = useState("");
  const [isResetDialogOpen, setIsResetDialogOpen] = useState(false);

  const initMutation = useInitializeSettings();
  const refreshMutation = useRefreshSettingsCache();
  const clearMutation = useClearSettingsCache();
  const resetMutation = useResetSettings();

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
      <div>
        <h2 className="text-2xl font-semibold tracking-tight">System Management</h2>
        <p className="text-muted-foreground">
          Manage cache, initialize configurations, and perform maintenance actions.
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2">
              <DatabaseZap className="w-5 h-5 text-blue-500" />
              Initialize Defaults
            </CardTitle>
            <CardDescription>
              Seed missing platform settings from the defaults file. Existing settings are preserved.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button 
              onClick={() => initMutation.mutate()} 
              disabled={initMutation.isPending}
            >
              {initMutation.isPending ? "Initializing..." : "Initialize Settings"}
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2">
              <RefreshCw className="w-5 h-5 text-green-500" />
              Cache Management
            </CardTitle>
            <CardDescription>
              Refresh or clear the settings cache. Cache is normally invalidated automatically.
            </CardDescription>
          </CardHeader>
          <CardContent className="flex gap-2">
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
          </CardContent>
        </Card>
      </div>

      <Card className="border-destructive/50 mt-8">
        <CardHeader>
          <CardTitle className="text-lg text-destructive flex items-center gap-2">
            <AlertTriangle className="w-5 h-5" />
            Danger Zone
          </CardTitle>
          <CardDescription>
            These actions are destructive and cannot be undone. Exercise extreme caution.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium text-sm">Reset Platform Settings</p>
              <p className="text-xs text-muted-foreground mt-1">
                Deletes all customized settings and completely restores the platform to initial defaults.
              </p>
            </div>
            
            <Dialog open={isResetDialogOpen} onOpenChange={setIsResetDialogOpen}>
              <DialogTrigger className="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 bg-destructive text-destructive-foreground shadow-sm hover:bg-destructive/90 h-9 px-4 py-2">
                Reset Settings
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle className="text-destructive flex items-center gap-2">
                    <AlertTriangle className="w-5 h-5" />
                    Reset All Settings
                  </DialogTitle>
                  <DialogDescription>
                    This action will delete all user-configured platform settings and restore the initial codebase defaults. 
                    This could impact active features and integrations.
                  </DialogDescription>
                </DialogHeader>
                <div className="py-4">
                  <p className="text-sm font-medium mb-2">
                    To confirm, please type <span className="font-mono bg-muted px-1 py-0.5 rounded text-destructive select-all">RESET_PLATFORM_SETTINGS</span> below:
                  </p>
                  <Input 
                    value={resetConfirmText}
                    onChange={(e) => setResetConfirmText(e.target.value)}
                    placeholder="RESET_PLATFORM_SETTINGS"
                    className="font-mono"
                  />
                </div>
                <DialogFooter>
                  <Button variant="outline" onClick={() => setIsResetDialogOpen(false)}>Cancel</Button>
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
        </CardContent>
      </Card>
    </div>
  );
}
