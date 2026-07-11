'use client';

import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import type { AnalyticsTimeline } from '../types';

interface TimelineChartProps {
  data?: AnalyticsTimeline;
}

export function TimelineChart({ data }: TimelineChartProps) {
  if (!data) return null;

  const chartData = Object.entries(data).map(([date, metrics]) => {
    const d = new Date(date);
    const label = isNaN(d.getTime()) ? date : d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    return {
      date,
      label,
      ...metrics,
    };
  }).sort((a, b) => a.date.localeCompare(b.date));

  const keys = chartData.length > 0 
    ? Object.keys(chartData[0]).filter(k => k !== 'date' && k !== 'label')
    : [];

  const primaryKey = keys[0];
  const secondaryKey = keys[1];

  return (
    <div className="w-full h-[280px] py-2">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
          <defs>
            <linearGradient id="colorTimeline1" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="hsl(var(--primary))" stopOpacity={0.3} />
              <stop offset="95%" stopColor="hsl(var(--primary))" stopOpacity={0} />
            </linearGradient>
            <linearGradient id="colorTimeline2" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="var(--color-chart-2)" stopOpacity={0.3} />
              <stop offset="95%" stopColor="var(--color-chart-2)" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="4 4" vertical={false} stroke="hsl(var(--border))" strokeOpacity={0.5} />
          <XAxis 
            dataKey="label" 
            axisLine={false} 
            tickLine={false} 
            tick={{ fontSize: 12, fill: 'hsl(var(--muted-foreground))' }}
            dy={10}
          />
          <YAxis 
            axisLine={false} 
            tickLine={false} 
            tick={{ fontSize: 12, fill: 'hsl(var(--muted-foreground))' }}
          />
          <Tooltip 
            contentStyle={{ 
              borderRadius: '12px', 
              border: '1px solid hsl(var(--border))', 
              backgroundColor: 'hsl(var(--card))',
              fontSize: '13px',
              color: 'hsl(var(--card-foreground))',
              boxShadow: '0 4px 12px rgba(0,0,0,0.1)'
            }}
            itemStyle={{ color: 'hsl(var(--card-foreground))', textTransform: 'capitalize' }}
            labelStyle={{ color: 'hsl(var(--muted-foreground))', marginBottom: '8px' }}
          />
          {primaryKey && (
            <Area 
              type="monotone" 
              dataKey={primaryKey} 
              stroke="hsl(var(--primary))" 
              fillOpacity={1} 
              fill="url(#colorTimeline1)" 
              strokeWidth={2}
              activeDot={{ r: 6, strokeWidth: 0, fill: 'hsl(var(--primary))' }}
            />
          )}
          {secondaryKey && (
            <Area 
              type="monotone" 
              dataKey={secondaryKey} 
              stroke="var(--color-chart-2)" 
              fillOpacity={1} 
              fill="url(#colorTimeline2)" 
              strokeWidth={2}
              activeDot={{ r: 6, strokeWidth: 0, fill: 'var(--color-chart-2)' }}
            />
          )}
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
