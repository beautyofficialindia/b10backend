"use client";

import React, { useState } from "react";
import { useAnalyticsFilters, AnalyticsPeriod } from "../../hooks/use-analytics-filters";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { RotateCcw, Download } from "lucide-react";
import { usePathname } from "next/navigation";
import api from "@/lib/axios";

export function AnalyticsFilters() {
  const {
    period,
    startDate,
    endDate,
    setPeriod,
    setDateRange,
    resetFilters,
  } = useAnalyticsFilters();

  const [localStartDate, setLocalStartDate] = useState(startDate);
  const [localEndDate, setLocalEndDate] = useState(endDate);
  const pathname = usePathname();

  const handleApplyCustomDates = () => {
    if (localStartDate && localEndDate) {
      setDateRange(localStartDate, localEndDate);
    }
  };

  const handleExport = async () => {
    try {
      let moduleName = "overview";
      if (pathname.includes("/analytics/leads")) moduleName = "leads";
      else if (pathname.includes("/analytics/crm")) moduleName = "crm";
      else if (pathname.includes("/analytics/chat")) moduleName = "chat";
      else if (pathname.includes("/analytics/knowledge")) moduleName = "knowledge";
      else if (pathname.includes("/analytics/users")) moduleName = "users";

      let url = `/admin/analytics/export/?module=${moduleName}`;
      if (period === "custom") {
        if (startDate) url += `&start_date=${startDate}`;
        if (endDate) url += `&end_date=${endDate}`;
      } else {
        url += `&period=${period}`;
      }

      const response = await api.get(url, { responseType: 'blob' });
      const blobUrl = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = blobUrl;
      link.setAttribute('download', `analytics_${moduleName}.csv`);
      document.body.appendChild(link);
      link.click();
      link.parentNode?.removeChild(link);
    } catch (error) {
      console.error("Export failed", error);
    }
  };

  return (
    <div className="flex flex-col sm:flex-row items-end gap-4 p-4 border rounded-lg bg-card">
      <div className="space-y-1.5 w-full sm:w-[200px]">
        <label className="text-sm font-medium leading-none">Time Period</label>
        <Select 
          value={period} 
          onValueChange={(value) => setPeriod(value as AnalyticsPeriod)}
        >
          <SelectTrigger>
            <SelectValue placeholder="Select period" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="today">Today</SelectItem>
            <SelectItem value="7d">Last 7 Days</SelectItem>
            <SelectItem value="30d">Last 30 Days</SelectItem>
            <SelectItem value="90d">Last 90 Days</SelectItem>
            <SelectItem value="custom">Custom Range</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {period === "custom" && (
        <div className="flex flex-col sm:flex-row items-end gap-2">
          <div className="space-y-1.5">
            <label className="text-sm font-medium leading-none">Start Date</label>
            <Input 
              type="date" 
              value={localStartDate} 
              onChange={(e) => setLocalStartDate(e.target.value)}
            />
          </div>
          <div className="space-y-1.5">
            <label className="text-sm font-medium leading-none">End Date</label>
            <Input 
              type="date" 
              value={localEndDate} 
              onChange={(e) => setLocalEndDate(e.target.value)}
            />
          </div>
          <Button onClick={handleApplyCustomDates}>Apply</Button>
        </div>
      )}

      <div className="flex-1" />

      <Button variant="outline" onClick={handleExport} title="Export CSV" className="gap-2">
        <Download className="h-4 w-4" />
        <span className="hidden sm:inline">Export CSV</span>
      </Button>

      <Button variant="outline" size="icon" onClick={resetFilters} title="Reset Filters">
        <RotateCcw className="h-4 w-4" />
      </Button>
    </div>
  );
}
