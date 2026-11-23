'use client';

import { useState, useEffect } from 'react';
import { simulatorApi } from '@/lib/api';
import ClassificationBadge from '@/components/ClassificationBadge';
import ScoreBar from '@/components/ScoreBar';
import Link from 'next/link';

export default function SimulatorPage() {
  const [profiles, setProfiles] = useState<any[]>([]);
  const [selectedProfile, setSelectedProfile] = useState('human_like');
  const [eventCount, setEventCount] = useState(50);
  const [running, setRunning] = useState(false);
  const [results, setResults] = useState<any[]>([]);

  useEffect(() => {
    simulatorApi.profiles().then(data => setProfiles(data.profiles)).catch(console.error);
  }, []);

  const runSimulation = async () => {
    setRunning(true);
    try {
      const result = await simulatorApi.run({ profile: selectedProfile, event_count: eventCount });
      setResults(prev => [result, ...prev]);
    } catch (err) {
      console.error('Simulation failed:', err);
    } finally {
      setRunning(false);
    }
  };

  const runAllProfiles = async () => {
    setRunning(true);
    try {
      for (const p of ['human_like', 'scripted_bot', 'aggressive_bot', 'slow_bot', 'mixed']) {
        const result = await simulatorApi.run({ profile: p, event_count: eventCount });
        setResults(prev => [result, ...prev]);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setRunning(false);
    }
  };

  return (
    <div className="max-w-[1400px] mx-auto px-6 py-8 space-y-6">
      <div>
        <h1 className="font-serif text-3xl font-bold text-warm-text">Bot Simulator</h1>
        <p className="text-sm text-warm-secondary mt-1">
          Generate synthetic behavioral profiles and test the detection engine
        </p>
      </div>

      {/* Controls */}
      <div className="card p-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 items-end">
          <div>
            <label className="text-[10px] font-mono text-warm-muted mb-1 block tracking-wide uppercase">Profile</label>
            <select
              value={selectedProfile}
              onChange={e => setSelectedProfile(e.target.value)}
              className="w-full bg-cream border border-cream-border rounded px-3 py-2 text-sm text-warm-text focus:outline-none focus:border-forest"
            >
              {profiles.map(p => (
                <option key={p.name} value={p.name}>{p.name}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="text-[10px] font-mono text-warm-muted mb-1 block tracking-wide uppercase">Event Count</label>
            <input
              type="number"
              value={eventCount}
              onChange={e => setEventCount(Number(e.target.value))}
              min={10}
              max={200}
              className="w-full bg-cream border border-cream-border rounded px-3 py-2 text-sm text-warm-text focus:outline-none focus:border-forest"
            />
          </div>
          <div className="flex gap-2">
            <button
              onClick={runSimulation}
              disabled={running}
              className="flex-1 px-4 py-2 bg-forest text-white text-xs font-mono font-semibold tracking-wide hover:bg-forest-dark transition-colors disabled:opacity-50"
            >
              {running ? 'RUNNING...' : 'RUN SIMULATION'}
            </button>
            <button
              onClick={runAllProfiles}
              disabled={running}
              className="px-4 py-2 bg-cream-dark text-warm-secondary text-xs font-mono font-semibold tracking-wide hover:text-warm-text transition-colors disabled:opacity-50"
            >
              RUN ALL
            </button>
          </div>
        </div>

        {profiles.length > 0 && (
          <div className="mt-4 grid grid-cols-1 md:grid-cols-5 gap-2">
            {profiles.map(p => (
              <div
                key={p.name}
                onClick={() => setSelectedProfile(p.name)}
                className={`p-3 cursor-pointer text-xs transition-all border ${
                  selectedProfile === p.name
                    ? 'bg-forest/5 border-forest'
                    : 'bg-white border-cream-border hover:border-warm-border'
                }`}
              >
                <div className="font-mono font-semibold text-warm-text mb-1">{p.name}</div>
                <div className="text-warm-muted leading-relaxed">{p.description}</div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Results */}
      {results.length > 0 && (
        <div className="space-y-4">
          <h2 className="font-serif text-xl font-bold text-warm-text">Simulation Results</h2>
          {results.map((r, i) => (
            <div key={i} className="card p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-4">
                  <span className="tag-green">{r.profile}</span>
                  <ClassificationBadge classification={r.classification} />
                  <span className="text-sm font-mono font-semibold" style={{
                    color: r.score > 70 ? '#C4432B' : r.score > 40 ? '#B87333' : '#2D5A3D'
                  }}>
                    Score: {r.score}/100
                  </span>
                </div>
                <Link
                  href={`/sessions/${r.session_id}`}
                  className="text-xs text-forest hover:underline font-mono"
                >
                  View Session &rarr;
                </Link>
              </div>

              {r.scoring_breakdown && (
                <div className="grid grid-cols-2 md:grid-cols-3 gap-3 mb-4">
                  {Object.entries(r.scoring_breakdown).map(([key, val]) => (
                    <ScoreBar key={key} label={key.replace(/_/g, ' ')} value={val as number} />
                  ))}
                </div>
              )}

              {r.explanations?.length > 0 && (
                <div className="mt-3 pt-3 border-t border-cream-border">
                  <div className="text-[10px] font-semibold text-warm-text mb-2 font-mono tracking-wide uppercase">Detection Explanations</div>
                  {r.explanations.map((exp: string, j: number) => (
                    <div key={j} className="text-xs text-warm-secondary mb-1 font-mono">&bull; {exp}</div>
                  ))}
                </div>
              )}

              {r.suspicious_counts && (
                <div className="mt-3 pt-3 border-t border-cream-border flex flex-wrap gap-4 text-xs font-mono">
                  {Object.entries(r.suspicious_counts).map(([key, val]) => (
                    <div key={key}>
                      <span className="text-warm-muted">{key}:</span>{' '}
                      <span className={Number(val) > 0 ? 'text-accent-red' : 'text-forest'}>
                        {String(val)}
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
