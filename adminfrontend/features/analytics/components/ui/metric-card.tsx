import React from "react";
import { Metric } from "../../types";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ArrowDownIcon, ArrowUpIcon } from "lucide-react";
import { cn } from "@/lib/utils";

interface MetricCardProps {
  metric: Metric;
}

export function MetricCard({ metric }: MetricCardProps) {
  if (!metric.enabled) return null;

  const isPositive = (metric.growth_percentage || 0) > 0;
  const isNegative = (metric.growth_percentage || 0) < 0;

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">{metric.title}</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{metric.value}</div>
        {metric.growth_percentage !== undefined && metric.growth_percentage !== null && (
          <p className={cn("flex items-center text-xs mt-1", isPositive ? "text-emerald-500" : isNegative ? "text-rose-500" : "text-muted-foreground")}>
            {isPositive && <ArrowUpIcon className="mr-1 h-3 w-3" />}
            {isNegative && <ArrowDownIcon className="mr-1 h-3 w-3" />}
            {Math.abs(metric.growth_percentage)}% from previous period
          </p>
        )}
      </CardContent>
    </Card>
  );
}
