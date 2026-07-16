"use client";

import { createContext, useContext, ReactNode, useMemo } from "react";
import { getSettingsByGroup } from "../api";
import { useQuery } from "@tanstack/react-query";

interface FeatureFlagsContextType {
  flags: Record<string, boolean>;
  strings: Record<string, string>;
  isLoading: boolean;
  isError: boolean;
}

const FeatureFlagsContext = createContext<FeatureFlagsContextType>({
  flags: {},
  strings: {},
  isLoading: true,
  isError: false,
});

export const useFeatureFlags = () => useContext(FeatureFlagsContext);

interface FeatureFlagsProviderProps {
  children: ReactNode;
}

export function FeatureFlagsProvider({ children }: FeatureFlagsProviderProps) {
  // Fetch FEATURES group
  const { data: featuresData, isLoading: isLoadingFeatures, isError: isErrorFeatures } = useQuery({
    queryKey: ["platformSettings", "groups", "FEATURES", "list"],
    queryFn: () => getSettingsByGroup("FEATURES"),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });

  // Fetch MAINTENANCE group
  const { data: maintenanceData, isLoading: isLoadingMaintenance, isError: isErrorMaintenance } = useQuery({
    queryKey: ["platformSettings", "groups", "MAINTENANCE", "list"],
    queryFn: () => getSettingsByGroup("MAINTENANCE"),
    staleTime: 5 * 60 * 1000,
  });

  const { flags, strings } = useMemo(() => {
    const newFlags: Record<string, boolean> = {};
    const newStrings: Record<string, string> = {};

    if (featuresData && maintenanceData) {
      const allSettings = [...featuresData.data, ...maintenanceData.data];
      
      allSettings.forEach((setting) => {
        if (setting.value_type === "BOOLEAN") {
          newFlags[setting.key] = setting.value.toLowerCase() === "true";
        } else if (setting.value_type === "STRING") {
          newStrings[setting.key] = setting.value;
        }
      });
    }
    
    return { flags: newFlags, strings: newStrings };
  }, [featuresData, maintenanceData]);

  const isLoading = isLoadingFeatures || isLoadingMaintenance;
  const isError = isErrorFeatures || isErrorMaintenance;

  return (
    <FeatureFlagsContext.Provider value={{ flags, strings, isLoading, isError }}>
      {children}
    </FeatureFlagsContext.Provider>
  );
}
