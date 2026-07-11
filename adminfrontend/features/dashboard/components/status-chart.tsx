'use client';

import { useState } from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Sector } from 'recharts';
import { cn } from '@/lib/utils';
import type { LeadSummary } from '../types';

const COLORS: Record<string, string> = {
  gathering: '#8B5CF6',
  qualified: '#22C55E',
  converted: '#3B82F6',
  lost: '#EF4444',
  escalated: '#F59E0B',
};

interface StatusChartProps {
  data?: LeadSummary;
}

const renderActiveShape = (props: any) => {
  const { cx, cy, innerRadius, outerRadius, startAngle, endAngle, fill } = props;
  return (
    <g filter="url(#donut-shadow)">
      <Sector
        cx={cx}
        cy={cy}
        innerRadius={innerRadius}
        outerRadius={outerRadius + 8}
        startAngle={startAngle}
        endAngle={endAngle}
        fill={fill}
        cornerRadius={6}
      />
    </g>
  );
};

export function StatusChart({ data }: StatusChartProps) {
  const [activeIndex, setActiveIndex] = useState<number | undefined>();

  if (!data) return null;

  const chartData = Object.entries(data)
    .filter(([key]) => key !== 'total_leads' && Number(data[key as keyof LeadSummary]) > 0)
    .map(([key, value]) => ({ 
      name: key.charAt(0).toUpperCase() + key.slice(1), 
      value: Number(value), 
      key 
    }));

  const onPieEnter = (_: any, index: number) => setActiveIndex(index);
  const onPieLeave = () => setActiveIndex(undefined);

  return (
    <div className="flex h-full w-full items-center gap-6 py-4">
      {/* Donut Chart with Permanent Center Text */}
      <div className="relative h-[240px] flex-1">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <defs>
              <filter id="donut-shadow" x="-20%" y="-20%" width="140%" height="140%">
                <feGaussianBlur stdDeviation="4" result="blur" />
                <feComposite in="SourceGraphic" in2="blur" operator="over" />
              </filter>
            </defs>
            <Pie 
              data={chartData} 
              innerRadius="65%" 
              outerRadius="90%" 
              dataKey="value" 
              stroke="none"
              paddingAngle={4}
              cornerRadius={6}
              // @ts-expect-error - Recharts types missing activeIndex
              activeIndex={activeIndex}
              activeShape={renderActiveShape}
              onMouseEnter={onPieEnter}
              onMouseLeave={onPieLeave}
              isAnimationActive={true}
              animationDuration={800}
            >
              {chartData.map((entry, index) => (
                <Cell 
                  key={`cell-${index}`} 
                  fill={COLORS[entry.key] || '#3B82F6'} 
                  className="transition-opacity duration-300"
                  opacity={activeIndex === undefined || activeIndex === index ? 1 : 0.4}
                />
              ))}
            </Pie>
            {/* Tooltip completely removed to prevent overlapping the central text */}
          </PieChart>
        </ResponsiveContainer>
        <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
          <span className="text-5xl font-bold text-white tracking-tight leading-none">{data.total_leads}</span>
          <span className="text-xs font-medium text-muted-foreground uppercase tracking-widest mt-2">Total Leads</span>
        </div>
      </div>

      {/* Premium Legend with Progress Bars */}
      <div className="flex flex-1 flex-col gap-5 border-l border-border/50 pl-8">
        {chartData.map((item, index) => {
          const percentage = data.total_leads > 0 ? (item.value / data.total_leads) * 100 : 0;
          const isHovered = activeIndex === index;
          
          return (
            <div 
              key={item.key} 
              className={cn(
                "flex flex-col gap-2 transition-all duration-300 cursor-default",
                isHovered ? "scale-105" : (activeIndex !== undefined && !isHovered) ? "opacity-40" : "opacity-100"
              )}
              onMouseEnter={() => setActiveIndex(index)}
              onMouseLeave={() => setActiveIndex(undefined)}
            >
              <div className="flex justify-between items-center text-sm">
                <span className="flex items-center gap-2.5 font-medium text-muted-foreground">
                  <div className="h-3 w-3 rounded-full shadow-sm" style={{ backgroundColor: COLORS[item.key] }} />
                  <span className={cn("transition-colors", isHovered && "text-foreground")}>{item.name}</span>
                </span>
                <span className="font-semibold text-foreground">
                  {item.value} 
                  <span className="text-muted-foreground font-normal ml-1.5 text-xs">({percentage.toFixed(0)}%)</span>
                </span>
              </div>
              <div className="h-2 w-full bg-muted/50 rounded-full overflow-hidden">
                <div 
                  className="h-full rounded-full transition-all duration-700 ease-out" 
                  style={{ width: `${percentage}%`, backgroundColor: COLORS[item.key] }} 
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
