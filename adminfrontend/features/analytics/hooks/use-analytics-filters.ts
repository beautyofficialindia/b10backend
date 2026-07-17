import { useRouter, useSearchParams, usePathname } from "next/navigation";
import { useCallback } from "react";

export type AnalyticsPeriod = "today" | "7d" | "30d" | "90d" | "custom";

export function useAnalyticsFilters() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const pathname = usePathname();

  const period = (searchParams.get("period") as AnalyticsPeriod) || "30d";
  const startDate = searchParams.get("start_date") || "";
  const endDate = searchParams.get("end_date") || "";

  const createQueryString = useCallback(
    (params: Record<string, string | null>) => {
      const newSearchParams = new URLSearchParams(searchParams.toString());

      for (const [key, value] of Object.entries(params)) {
        if (value === null) {
          newSearchParams.delete(key);
        } else {
          newSearchParams.set(key, value);
        }
      }

      return newSearchParams.toString();
    },
    [searchParams]
  );

  const setPeriod = useCallback(
    (newPeriod: AnalyticsPeriod) => {
      if (newPeriod === "custom") {
        router.push(`${pathname}?${createQueryString({ period: newPeriod })}`);
      } else {
        // Clear custom dates when selecting standard periods
        router.push(
          `${pathname}?${createQueryString({
            period: newPeriod,
            start_date: null,
            end_date: null,
          })}`
        );
      }
    },
    [router, pathname, createQueryString]
  );

  const setDateRange = useCallback(
    (start: string, end: string) => {
      router.push(
        `${pathname}?${createQueryString({
          period: "custom",
          start_date: start,
          end_date: end,
        })}`
      );
    },
    [router, pathname, createQueryString]
  );

  const resetFilters = useCallback(() => {
    router.push(
      `${pathname}?${createQueryString({
        period: "30d",
        start_date: null,
        end_date: null,
      })}`
    );
  }, [router, pathname, createQueryString]);

  const queryString = searchParams.toString();

  return {
    period,
    startDate,
    endDate,
    setPeriod,
    setDateRange,
    resetFilters,
    queryString,
  };
}
