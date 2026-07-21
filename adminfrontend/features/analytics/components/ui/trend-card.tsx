"use client";

import React from "react";
import { Trend } from "../../types";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { LineChart, Line, BarChart, Bar, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { ChartTooltip } from "./chart-tooltip";

interface TrendCardProps {
  trend: Trend;
  type?: "line" | "bar";
}

export function TrendCard({ trend, type = "line" }: TrendCardProps) {
  if (!trend.labels || trend.labels.length === 0) return null;

  const data = trend.labels.map((label, index) => ({
    name: label,
    value: trend.values[index] || 0,
  }));

  return (
    <Card className="col-span-full md:col-span-2">
      <CardHeader>
        <CardTitle className="text-sm font-medium">{trend.title}</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="h-[200px] w-full mt-4">
          <ResponsiveContainer width="100%" height="100%">
            {type === "line" ? (
              <LineChart data={data}>
                <XAxis dataKey="name" stroke="#888888" fontSize={12} tickLine={false} axisLine={false} />
                <YAxis stroke="#888888" fontSize={12} tickLine={false} axisLine={false} tickFormatter={(value) => `${value}`} />
                <Tooltip content={<ChartTooltip title={trend.title} />} cursor={{ fill: 'transparent' }} />
                <Line type="monotone" dataKey="value" stroke="currentColor" strokeWidth={2} activeDot={{ r: 4 }} className="stroke-primary" />
              </LineChart>
            ) : (
              <BarChart data={data}>
                <XAxis dataKey="name" stroke="#888888" fontSize={12} tickLine={false} axisLine={false} />
                <YAxis stroke="#888888" fontSize={12} tickLine={false} axisLine={false} tickFormatter={(value) => `${value}`} />
                <Tooltip content={<ChartTooltip title={trend.title} />} cursor={{ fill: 'var(--muted)', opacity: 0.2 }} />
                <Bar dataKey="value" fill="currentColor" radius={[4, 4, 0, 0]} className="fill-primary" />
              </BarChart>
            )}
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  );
}
