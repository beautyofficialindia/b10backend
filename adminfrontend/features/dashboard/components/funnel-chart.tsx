'use client';


import type { FunnelStage } from '../types';

const FUNNEL_GRADIENTS = [
  { id: 'grad-chats', style: { backgroundImage: 'linear-gradient(to right, #7C5CFF, #5B6CFF)' }, glow: 'rgba(124, 92, 255, 0.3)' },
  { id: 'grad-leads', style: { backgroundImage: 'linear-gradient(to right, #22C1FF, #3B82F6)' }, glow: 'rgba(34, 193, 255, 0.3)' },
  { id: 'grad-qualified', style: { backgroundImage: 'linear-gradient(to right, #22C55E, #10B981)' }, glow: 'rgba(34, 197, 94, 0.3)' },
  { id: 'grad-converted', style: { backgroundImage: 'linear-gradient(to right, #F59E0B, #FB923C)' }, glow: 'rgba(245, 158, 11, 0.3)' },
];

interface FunnelChartProps {
  data?: FunnelStage[];
}

export function FunnelChart({ data }: FunnelChartProps) {
  if (!data || data.length === 0) return null;

  const maxVal = Math.max(...data.map(d => d.value));

  return (
    <div className="flex flex-col gap-6 py-4 px-2 w-full h-[280px] justify-center">
      {data.map((stage, i) => {
        // Safe division; default to 0
        const percentage = maxVal > 0 ? (stage.value / maxVal) * 100 : 0;
        
        // Ensure even tiny values are visibly rendered if they are > 0
        const barWidth = stage.value === 0 ? 0 : Math.max(2, percentage);
        
        const gradient = FUNNEL_GRADIENTS[i % FUNNEL_GRADIENTS.length];

        return (
          <div key={stage.stage} className="grid grid-cols-[130px_1fr_90px] items-center gap-4 group">
            {/* 1. Label Column */}
            <span className="text-[13px] font-medium text-muted-foreground group-hover:text-foreground transition-colors duration-300 truncate tracking-wide">
              {stage.stage}
            </span>

            {/* 2. Bar Area Column */}
            <div className="relative h-[26px] w-full bg-transparent flex items-center">
              {stage.value > 0 ? (
                <div 
                  className="h-full rounded-md transition-all duration-1000 ease-out group-hover:brightness-110"
                  style={{ 
                    ...gradient.style,
                    width: `${barWidth}%`,
                    boxShadow: `0 4px 14px 0 ${gradient.glow}`
                  }}
                />
              ) : (
                <span className="text-muted-foreground/50 font-medium">—</span>
              )}
            </div>

            {/* 3. Value & Percentage Column */}
            <div className="flex items-center justify-end gap-2 text-right">
              <span className="text-sm font-bold text-foreground">
                {stage.value}
              </span>
              <span className="text-xs font-medium text-muted-foreground w-11 text-right">
                ({percentage.toFixed(0)}%)
              </span>
            </div>
          </div>
        );
      })}
    </div>
  );
}
