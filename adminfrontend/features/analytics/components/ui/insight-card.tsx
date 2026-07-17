import React from "react";
import { Insight } from "../../types";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface InsightCardProps {
  insight: Insight;
}

export function InsightCard({ insight }: InsightCardProps) {
  if (!insight.enabled) return null;

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">{insight.title}</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="text-xl font-semibold break-words">{insight.value}</div>
      </CardContent>
    </Card>
  );
}
