'use client';

import { useState, useEffect } from 'react';
import { sessionsApi } from '@/lib/api';
import ClassificationBadge from '@/components/ClassificationBadge';
import ScoreBar from '@/components/ScoreBar';

export default function ComparePage() {
  const [sessions, setSessions] = useState<any[]>([]);
  const [sessionA, setSessionA] = useState('');
  const [sessionB, setSessionB] = useState('');
  const [comparison, setComparison] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    sessionsApi.list({ limit: 50 }).then(setSessions).catch(console.error);
  }, []);

  const compare = async () => {
    if (!sessionA || !sessionB) return;
    setLoading(true);
    try {
      const result = await sessionsApi.compare(sessionA, sessionB);
      setComparison(result);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-[1400px] mx-auto px-6 py-8 space-y-6">
      <div>
        <h1 className="font-serif text-3xl font-bold text-warm-text">Session Comparison</h1>
        <p className="text-sm text-warm-secondary mt-1">Compare two sessions side by side</p>
      </div>

      {/* Selection */}
      <div className="card p-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 items-end">
          <div>
            <label className="text-[10px] font-mono text-warm-muted mb-1 block tracking-wide uppercase">Session A</label>
            <select
              value={sessionA}
              onChange={e => setSessionA(e.target.value)}
              className="w-full bg-cream border border-cream-border rounded px-3 py-2 text-sm text-warm-text font-mono focus:outline-none focus:border-forest"
            >
              <option value="">Select session...</option>
              {sessions.map(s => (
                <option key={s.id} value={s.id}>
                  {s.id.slice(0, 12)} — {s.classification} ({s.score?.toFixed(0)}) {s.is_simulated ? `[${s.is_simulated}]` : ''}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="text-[10px] font-mono text-warm-muted mb-1 block tracking-wide uppercase">Session B</label>
            <select
              value={sessionB}
              onChange={e => setSessionB(e.target.value)}
              className="w-full bg-cream border border-cream-border rounded px-3 py-2 text-sm text-warm-text font-mono focus:outline-none focus:border-forest"
            >
              <option value="">Select session...</option>
              {sessions.map(s => (
                <option key={s.id} value={s.id}>
                  {s.id.slice(0, 12)} — {s.classification} ({s.score?.toFixed(0)}) {s.is_simulated ? `[${s.is_simulated}]` : ''}
                </option>
              ))}
            </select>
          </div>
          <button
            onClick={compare}
            disabled={!sessionA || !sessionB || loading}
            className="px-4 py-2 bg-forest text-white text-xs font-mono font-semibold tracking-wide hover:bg-forest-dark transition-colors disabled:opacity-50"
          >
            {loading ? 'COMPARING...' : 'COMPARE SESSIONS'}
          </button>
        </div>
      </div>

      {/* Comparison Results */}
      {comparison && (
        <div className="space-y-6">
          {/* Overview */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {['session_a', 'session_b'].map((key, idx) => {
              const s = comparison[key];
              return (
                <div key={key} className="card p-6">
                  <div className="flex items-center justify-between mb-4">
                    <div>
                      <div className="text-[10px] font-mono text-warm-muted mb-1 tracking-wide uppercase">
                        Session {idx === 0 ? 'A' : 'B'}
                      </div>
                      <div className="text-sm font-mono text-forest">{s.id.slice(0, 12)}...</div>
                    </div>
                    <ClassificationBadge classification={s.classification} />
                  </div>

                  <div className="text-center mb-4">
                    <div className="text-4xl font-bold font-mono" style={{
                      color: s.score > 70 ? '#C4432B' : s.score > 40 ? '#B87333' : '#2D5A3D'
                    }}>
                      {s.score?.toFixed(1)}
                    </div>
                    <div className="text-[10px] text-warm-muted font-mono tracking-wide uppercase">Automation Score</div>
                  </div>

                  <div className="grid grid-cols-2 gap-3 text-xs font-mono mb-4">
                    <div className="bg-cream-light border border-cream-border p-2">
                      <span className="text-warm-muted">Events:</span>{' '}
                      <span className="text-warm-text">{s.event_count}</span>
                    </div>
                    <div className="bg-cream-light border border-cream-border p-2">
                      <span className="text-warm-muted">Detections:</span>{' '}
                      <span className="text-accent-red">{s.detection_count}</span>
                    </div>
                  </div>

                  {s.scoring_breakdown && Object.entries(s.scoring_breakdown).map(([k, v]) => (
                    <ScoreBar key={k} label={k.replace(/_/g, ' ')} value={v as number} />
                  ))}
                </div>
              );
            })}
          </div>

          {/* Comparison Summary */}
          <div className="card p-6">
            <h3 className="text-xs font-mono font-semibold text-warm-text mb-4 tracking-wide uppercase">Comparison Analysis</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-cream-light border border-cream-border p-3 text-center">
                <div className="text-[10px] text-warm-muted font-mono tracking-wide uppercase">Score Difference</div>
                <div className="text-xl font-bold font-mono text-forest mt-1">
                  {comparison.comparison.score_difference?.toFixed(1)}
                </div>
              </div>
              <div className="bg-cream-light border border-cream-border p-3 text-center">
                <div className="text-[10px] text-warm-muted font-mono tracking-wide uppercase">Event Count Diff</div>
                <div className="text-xl font-bold font-mono text-accent-amber mt-1">
                  {comparison.comparison.event_count_difference}
                </div>
              </div>
              <div className="bg-cream-light border border-cream-border p-3 text-center">
                <div className="text-[10px] text-warm-muted font-mono tracking-wide uppercase">Detection Count Diff</div>
                <div className="text-xl font-bold font-mono text-accent-red mt-1">
                  {comparison.comparison.detection_count_difference}
                </div>
              </div>
              <div className="bg-cream-light border border-cream-border p-3 text-center">
                <div className="text-[10px] text-warm-muted font-mono tracking-wide uppercase">Same Classification</div>
                <div className={`text-xl font-bold font-mono mt-1 ${
                  comparison.comparison.same_classification ? 'text-forest' : 'text-accent-red'
                }`}>
                  {comparison.comparison.same_classification ? 'YES' : 'NO'}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
