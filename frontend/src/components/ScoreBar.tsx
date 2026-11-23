'use client';

interface ScoreBarProps {
  label: string;
  value: number;
  max?: number;
  color?: string;
}

export default function ScoreBar({ label, value, max = 100, color }: ScoreBarProps) {
  const pct = Math.min(100, (value / max) * 100);
  const barColor = color || (pct > 70 ? '#C4432B' : pct > 40 ? '#B87333' : '#2D5A3D');

  return (
    <div className="space-y-1">
      <div className="flex justify-between text-[11px] font-mono">
        <span className="text-warm-secondary">{label}</span>
        <span style={{ color: barColor }} className="font-semibold">{value.toFixed(1)}%</span>
      </div>
      <div className="h-1.5 bg-cream-dark rounded-full overflow-hidden">
        <div
          className="h-full rounded-full transition-all duration-1000 ease-out"
          style={{ width: `${pct}%`, backgroundColor: barColor, '--bar-width': `${pct}%` } as any}
        />
      </div>
    </div>
  );
}
