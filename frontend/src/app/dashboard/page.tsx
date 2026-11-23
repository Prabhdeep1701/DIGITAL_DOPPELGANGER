'use client';

import { useEffect, useState } from 'react';
import { sessionsApi } from '@/lib/api';
import ClassificationBadge from '@/components/ClassificationBadge';
import { useWebSocket } from '@/hooks/useWebSocket';
import Link from 'next/link';

export default function DashboardPage() {
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [liveEvents, setLiveEvents] = useState<any[]>([]);

  const { lastMessage } = useWebSocket('/ws/dashboard', {
    onMessage: (data) => {
      setLiveEvents(prev => [data, ...prev].slice(0, 20));
    },
  });

  useEffect(() => {
    sessionsApi.dashboard()
      .then(setStats)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-warm-muted font-mono text-sm animate-pulse">Loading dashboard...</div>
      </div>
    );
  }

  if (!stats) {
    return <div className="text-warm-muted font-mono">Failed to load dashboard data.</div>;
  }

  return (
    <div className="max-w-[1400px] mx-auto px-6 py-8 space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <span className="tag-green">DASHBOARD</span>
          <span className="tag-cream">LIVE MONITORING</span>
        </div>
        <div className="flex items-center gap-2 text-[10px] font-mono text-warm-muted">
          <span className="w-1.5 h-1.5 rounded-full bg-forest animate-pulse" />
          SYSTEM ACTIVE — REAL-TIME FEED
        </div>
      </div>

      {/* Three Metric Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Automation Scoring */}
        <div className="card overflow-hidden">
          <div className="section-bar">
            <span>AUTOMATION SCORING</span>
            <span className="ml-auto text-[9px] opacity-70">COMPOSITE INDEX</span>
          </div>
          <div className="p-6">
            <div className="text-5xl font-serif font-bold text-forest tracking-tight">
              {stats.average_score?.toFixed(1) || '0.0'}%
            </div>
            <div className="mt-3 flex flex-wrap gap-1.5">
              <span className="tag-green">HUMAN: {stats.human_like}</span>
              <span className="tag-red">AUTOMATED: {stats.automated_like}</span>
              <span className="tag-amber">SUSPICIOUS: {stats.suspicious}</span>
            </div>
          </div>
        </div>

        {/* Document Profiles */}
        <div className="card overflow-hidden">
          <div className="section-bar">
            <span>DOCUMENT PROFILES</span>
            <span className="ml-auto text-[9px] opacity-70">TOTAL SESSIONS</span>
          </div>
          <div className="p-6">
            <div className="text-5xl font-serif font-bold text-warm-text tracking-tight">
              {stats.total_sessions?.toLocaleString() || '0'}
            </div>
            <div className="mt-3 flex flex-wrap gap-1.5">
              <span className="tag-cream">ACTIVE: {stats.active_sessions}</span>
              <span className="tag-cream">EVENTS: {stats.total_events?.toLocaleString()}</span>
            </div>
          </div>
        </div>

        {/* Doppler Health */}
        <div className="card overflow-hidden">
          <div className="section-bar">
            <span>DOPPLER HEALTH</span>
            <span className="ml-auto text-[9px] opacity-70">ENGINE STATUS</span>
          </div>
          <div className="p-6">
            <div className="text-5xl font-serif font-bold text-forest tracking-tight">
              99.71%
            </div>
            <div className="mt-3 flex flex-wrap gap-1.5">
              <span className="tag-green">4 DFAs ACTIVE</span>
              <span className="tag-cream">DETECTIONS: {stats.total_detections}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Classification Distribution Bar */}
      <div className="card overflow-hidden">
        <div className="section-bar">
          <span>CLASSIFICATION DISTRIBUTION</span>
        </div>
        <div className="p-4">
          <div className="flex h-3 rounded-sm overflow-hidden gap-0.5">
            {[
              { value: stats.human_like, total: stats.total_sessions, color: '#2D5A3D', label: 'Human' },
              { value: stats.automated_like, total: stats.total_sessions, color: '#C4432B', label: 'Automated' },
              { value: stats.suspicious, total: stats.total_sessions, color: '#B87333', label: 'Suspicious' },
              { value: stats.inconclusive, total: stats.total_sessions, color: '#D4CFC5', label: 'Inconclusive' },
            ].map(item => (
              <div
                key={item.label}
                className="h-full transition-all duration-1000"
                style={{
                  width: `${item.total ? (item.value / item.total) * 100 : 0}%`,
                  backgroundColor: item.color,
                  minWidth: item.value > 0 ? '4px' : '0',
                }}
                title={`${item.label}: ${item.value}`}
              />
            ))}
          </div>
          <div className="mt-2 flex gap-4 text-[10px] font-mono text-warm-muted">
            <span><span className="inline-block w-2 h-2 rounded-sm bg-forest mr-1" />Human: {stats.human_like}</span>
            <span><span className="inline-block w-2 h-2 rounded-sm bg-accent-red mr-1" />Automated: {stats.automated_like}</span>
            <span><span className="inline-block w-2 h-2 rounded-sm bg-accent-amber mr-1" />Suspicious: {stats.suspicious}</span>
            <span><span className="inline-block w-2 h-2 rounded-sm bg-warm-border mr-1" />Inconclusive: {stats.inconclusive}</span>
          </div>
        </div>
      </div>

      {/* Three-column layout */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Left: Terminal Event Feed */}
        <div className="terminal p-4 min-h-[360px]">
          <div className="flex items-center justify-between mb-3">
            <span className="text-[10px] font-semibold tracking-wider text-green-300 uppercase">Live Event Feed</span>
            <span className="text-[9px] terminal-muted">{liveEvents.length} events</span>
          </div>
          <div className="space-y-1 max-h-[300px] overflow-auto">
            {liveEvents.length === 0 ? (
              <div className="terminal-muted text-[11px]">
                &gt; Waiting for events...<br />
                &gt; Start a playground session or run a simulation.
              </div>
            ) : (
              liveEvents.map((evt, i) => (
                <div key={i} className={`flex items-center gap-2 text-[11px] py-0.5 px-1 rounded ${
                  evt.is_suspicious ? 'bg-red-900/20' : ''
                }`}>
                  <span className={`w-1 h-1 rounded-full flex-shrink-0 ${
                    evt.is_suspicious ? 'bg-red-400' : 'bg-green-400'
                  }`} />
                  <span className="terminal-accent font-semibold">{evt.event_type}</span>
                  <span className="terminal-muted">s:{evt.session_id?.slice(0, 6)}</span>
                  {evt.product_state && (
                    <span className="terminal-muted ml-auto text-[10px]">
                      [{evt.product_state.navigation}]
                    </span>
                  )}
                </div>
              ))
            )}
          </div>
        </div>

        {/* Center: System State Overview */}
        <div className="card p-4">
          <div className="flex items-center gap-2 mb-3">
            <span className="tag-green">SYSTEM STATE</span>
          </div>
          <div className="space-y-3">
            {[
              { label: 'Navigation DFA', status: 'ACTIVE', color: '#2D5A3D' },
              { label: 'Interaction DFA', status: 'ACTIVE', color: '#2D5A3D' },
              { label: 'Timing DFA', status: 'ACTIVE', color: '#2D5A3D' },
              { label: 'Consistency DFA', status: 'ACTIVE', color: '#2D5A3D' },
            ].map(dfa => (
              <div key={dfa.label} className="flex items-center justify-between py-2 border-b border-cream-border last:border-0">
                <span className="text-xs font-mono text-warm-secondary">{dfa.label}</span>
                <span className="tag-green">{dfa.status}</span>
              </div>
            ))}
            <div className="pt-2 space-y-2">
              <div className="flex justify-between text-[11px] font-mono">
                <span className="text-warm-muted">Total Events Processed</span>
                <span className="text-forest font-semibold">{stats.total_events?.toLocaleString()}</span>
              </div>
              <div className="flex justify-between text-[11px] font-mono">
                <span className="text-warm-muted">Total Detections</span>
                <span className="text-accent-red font-semibold">{stats.total_detections}</span>
              </div>
              <div className="flex justify-between text-[11px] font-mono">
                <span className="text-warm-muted">Active Sessions</span>
                <span className="text-forest font-semibold">{stats.active_sessions}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Right: Quick Stats */}
        <div className="space-y-4">
          <div className="card p-4">
            <div className="flex items-center gap-2 mb-3">
              <span className="tag-green">SCORING BREAKDOWN</span>
            </div>
            <div className="space-y-3">
              {[
                { label: 'Human-Like', value: stats.human_like, total: stats.total_sessions, color: '#2D5A3D' },
                { label: 'Automated-Like', value: stats.automated_like, total: stats.total_sessions, color: '#C4432B' },
                { label: 'Suspicious', value: stats.suspicious, total: stats.total_sessions, color: '#B87333' },
                { label: 'Inconclusive', value: stats.inconclusive, total: stats.total_sessions, color: '#8A8A7A' },
              ].map(item => (
                <div key={item.label} className="space-y-1">
                  <div className="flex justify-between text-[11px] font-mono">
                    <span className="text-warm-secondary">{item.label}</span>
                    <span style={{ color: item.color }} className="font-semibold">{item.value}</span>
                  </div>
                  <div className="h-1.5 bg-cream-dark rounded-full overflow-hidden">
                    <div
                      className="h-full rounded-full transition-all duration-1000"
                      style={{
                        width: `${item.total ? (item.value / item.total) * 100 : 0}%`,
                        backgroundColor: item.color,
                      }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Recent Sessions Table */}
      <div className="card overflow-hidden">
        <div className="section-bar justify-between">
          <span>RECENT SESSIONS</span>
          <Link href="/sessions" className="text-[9px] text-white/70 hover:text-white tracking-wider">
            VIEW ALL &rarr;
          </Link>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-[11px] font-mono">
            <thead className="text-warm-muted bg-cream-light">
              <tr className="border-b border-cream-border">
                <th className="text-left py-2.5 px-4">Session ID</th>
                <th className="text-left py-2.5 px-4">Started</th>
                <th className="text-left py-2.5 px-4">Type</th>
                <th className="text-left py-2.5 px-4">Classification</th>
                <th className="text-right py-2.5 px-4">Score</th>
              </tr>
            </thead>
            <tbody>
              {stats.recent_sessions?.map((s: any) => (
                <tr key={s.id} className="border-b border-cream-border/50 hover:bg-cream-light/50">
                  <td className="py-2.5 px-4">
                    <Link href={`/sessions/${s.id}`} className="text-forest hover:underline">
                      {s.id.slice(0, 8)}...
                    </Link>
                  </td>
                  <td className="py-2.5 px-4 text-warm-muted">
                    {s.started_at ? new Date(s.started_at).toLocaleString() : '-'}
                  </td>
                  <td className="py-2.5 px-4">
                    {s.is_simulated ? (
                      <span className="tag-amber">{s.is_simulated}</span>
                    ) : (
                      <span className="tag-green">REAL</span>
                    )}
                  </td>
                  <td className="py-2.5 px-4">
                    <ClassificationBadge classification={s.classification} size="sm" />
                  </td>
                  <td className="py-2.5 px-4 text-right font-semibold" style={{
                    color: s.score > 70 ? '#C4432B' : s.score > 40 ? '#B87333' : '#2D5A3D'
                  }}>
                    {s.score?.toFixed(1)}/100
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Footer bar */}
      <div className="flex items-center justify-between text-[10px] font-mono text-warm-muted pt-2">
        <span>AUTOMATA ENGINE — 4 DFAs · PRODUCT AUTOMATON ACTIVE</span>
        <span>DIGITAL DOPPELGÄNGER v2.0</span>
      </div>
    </div>
  );
}
