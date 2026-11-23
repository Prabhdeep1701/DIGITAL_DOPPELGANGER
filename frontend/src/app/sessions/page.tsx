'use client';

import { useEffect, useState } from 'react';
import { sessionsApi } from '@/lib/api';
import ClassificationBadge from '@/components/ClassificationBadge';
import Link from 'next/link';

export default function SessionsPage() {
  const [sessions, setSessions] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<string>('');

  useEffect(() => {
    sessionsApi.list({ limit: 100 })
      .then(setSessions)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const filtered = filter
    ? sessions.filter(s => s.classification === filter)
    : sessions;

  return (
    <div className="max-w-[1400px] mx-auto px-6 py-8 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="font-serif text-3xl font-bold text-warm-text">Session Explorer</h1>
          <p className="text-sm text-warm-secondary mt-1">{sessions.length} sessions recorded</p>
        </div>
        <div className="flex gap-1">
          {['', 'human_like', 'automated_like', 'suspicious', 'inconclusive'].map(f => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`px-3 py-1.5 text-[10px] font-mono font-medium tracking-wide transition-colors ${
                filter === f
                  ? 'bg-forest text-white'
                  : 'bg-cream-dark text-warm-secondary hover:text-warm-text'
              }`}
            >
              {(f || 'All').toUpperCase()}
            </button>
          ))}
        </div>
      </div>

      {loading ? (
        <div className="text-warm-muted font-mono text-sm animate-pulse">Loading sessions...</div>
      ) : (
        <div className="card overflow-hidden">
          <table className="w-full text-xs font-mono">
            <thead className="text-warm-muted bg-cream-light">
              <tr className="border-b border-cream-border">
                <th className="text-left py-3 px-4 tracking-wide uppercase">Session ID</th>
                <th className="text-left py-3 px-4 tracking-wide uppercase">Started</th>
                <th className="text-left py-3 px-4 tracking-wide uppercase">Type</th>
                <th className="text-left py-3 px-4 tracking-wide uppercase">Classification</th>
                <th className="text-right py-3 px-4 tracking-wide uppercase">Score</th>
                <th className="text-right py-3 px-4 tracking-wide uppercase">Events</th>
                <th className="text-right py-3 px-4 tracking-wide uppercase">Actions</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map(s => (
                <tr key={s.id} className="border-b border-cream-border/50 hover:bg-cream-light/50">
                  <td className="py-3 px-4">
                    <Link href={`/sessions/${s.id}`} className="text-forest hover:underline">
                      {s.id.slice(0, 12)}...
                    </Link>
                  </td>
                  <td className="py-3 px-4 text-warm-muted">
                    {s.started_at ? new Date(s.started_at).toLocaleString() : '-'}
                  </td>
                  <td className="py-3 px-4">
                    {s.is_simulated ? (
                      <span className="tag-amber">{s.is_simulated}</span>
                    ) : (
                      <span className="tag-green">real</span>
                    )}
                  </td>
                  <td className="py-3 px-4">
                    <ClassificationBadge classification={s.classification} size="sm" />
                  </td>
                  <td className="py-3 px-4 text-right font-semibold" style={{
                    color: s.score > 70 ? '#C4432B' : s.score > 40 ? '#B87333' : '#2D5A3D'
                  }}>
                    {s.score?.toFixed(1)}
                  </td>
                  <td className="py-3 px-4 text-right text-warm-muted">{s.event_count}</td>
                  <td className="py-3 px-4 text-right">
                    <Link
                      href={`/sessions/${s.id}`}
                      className="text-forest hover:underline"
                    >
                      Details
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {filtered.length === 0 && (
            <div className="p-8 text-center text-warm-muted text-sm">
              No sessions found. Run a simulation or use the playground to generate sessions.
            </div>
          )}
        </div>
      )}
    </div>
  );
}
