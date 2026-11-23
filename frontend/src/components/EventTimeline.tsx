'use client';

import { useState } from 'react';

interface TimelineEvent {
  event_type: string;
  timestamp: number;
  page?: string;
  target?: string;
  sequence_number?: number;
  is_suspicious?: boolean;
}

interface EventTimelineProps {
  events: TimelineEvent[];
  automataStates?: any[];
  maxHeight?: string;
}

export default function EventTimeline({ events, automataStates, maxHeight = '500px' }: EventTimelineProps) {
  const [filter, setFilter] = useState<string>('');

  const filtered = filter
    ? events.filter(e => e.event_type.includes(filter) || e.page?.includes(filter))
    : events;

  const formatTime = (ts: number) => {
    const d = new Date(ts * 1000);
    return d.toLocaleTimeString('en-US', { hour12: false, fractionalSecondDigits: 3 });
  };

  const getDelay = (idx: number): string => {
    if (idx === 0) return '-';
    const delay = (filtered[idx].timestamp - filtered[idx - 1].timestamp) * 1000;
    return `${delay.toFixed(0)}ms`;
  };

  const getEventColor = (type: string) => {
    if (type.includes('click')) return 'text-forest';
    if (type.includes('key') || type.includes('focus') || type.includes('submit')) return 'text-accent-gold';
    if (type.includes('move') || type.includes('scroll') || type.includes('hover')) return 'text-warm-muted';
    if (type.includes('page')) return 'text-forest-light';
    if (type.includes('fail') || type.includes('rapid')) return 'text-accent-red';
    if (type === 'idle') return 'text-accent-amber';
    return 'text-warm-text';
  };

  return (
    <div className="card p-4">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-xs font-mono font-semibold text-warm-text tracking-wide uppercase">Event Timeline</h3>
        <input
          type="text"
          placeholder="Filter events..."
          value={filter}
          onChange={e => setFilter(e.target.value)}
          className="text-xs font-mono bg-cream border border-cream-border rounded px-2 py-1 text-warm-text focus:outline-none focus:border-forest w-40"
        />
      </div>
      <div className="overflow-auto font-mono text-[11px]" style={{ maxHeight }}>
        <table className="w-full">
          <thead className="text-warm-muted sticky top-0 bg-white">
            <tr className="border-b border-cream-border">
              <th className="text-left py-1.5 px-2">#</th>
              <th className="text-left py-1.5 px-2">Time</th>
              <th className="text-left py-1.5 px-2">Event</th>
              <th className="text-left py-1.5 px-2">Target</th>
              <th className="text-right py-1.5 px-2">Delay</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((event, idx) => (
              <tr
                key={idx}
                className={`border-t border-cream-border/50 hover:bg-cream-light ${
                  event.is_suspicious ? 'bg-accent-red/5' : ''
                }`}
              >
                <td className="py-1 px-2 text-warm-muted">{event.sequence_number || idx + 1}</td>
                <td className="py-1 px-2 text-warm-muted">{formatTime(event.timestamp)}</td>
                <td className={`py-1 px-2 font-semibold ${getEventColor(event.event_type)}`}>
                  {event.event_type.toUpperCase()}
                </td>
                <td className="py-1 px-2 text-warm-muted">
                  {event.page && <span className="text-forest/60">{event.page}</span>}
                  {event.target && <span className="ml-1">&rarr; {event.target}</span>}
                </td>
                <td className="py-1 px-2 text-right text-warm-muted">{getDelay(idx)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="mt-2 text-[10px] text-warm-muted font-mono">
        {filtered.length} events {filter && `(filtered from ${events.length})`}
      </div>
    </div>
  );
}
