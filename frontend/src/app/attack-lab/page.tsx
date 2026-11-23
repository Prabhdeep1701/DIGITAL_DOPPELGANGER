'use client';

import { useState } from 'react';
import { simulatorApi } from '@/lib/api';
import ClassificationBadge from '@/components/ClassificationBadge';
import ScoreBar from '@/components/ScoreBar';
import Link from 'next/link';

const TESTS = [
  {
    type: 'deterministic',
    name: 'Test 1: Pure Deterministic Bot',
    description: 'Fixed sequence, regular timing, no variation.',
  },
  {
    type: 'randomized',
    name: 'Test 2: Randomized Bot',
    description: 'Aggressive automation with slightly randomized actions.',
  },
  {
    type: 'slow',
    name: 'Test 3: Slow Bot',
    description: 'Deliberately slow with randomized timing. Tests if "fast = bot" rule is insufficient.',
  },
  {
    type: 'human_like_scripted',
    name: 'Test 4: Human-Like Scripted Bot',
    description: 'Bot that mimics human timing patterns but maintains deterministic behavior.',
  },
  {
    type: 'human',
    name: 'Test 5: Human Session',
    description: 'Synthetic human-like session as a control.',
  },
  {
    type: 'mixed',
    name: 'Test 6: Mixed Behavior',
    description: 'Starts human-like, transitions to automated behavior midway.',
  },
];

export default function AttackLabPage() {
  const [results, setResults] = useState<Record<string, any>>({});
  const [running, setRunning] = useState<string | null>(null);
  const [runningAll, setRunningAll] = useState(false);

  const runTest = async (testType: string) => {
    setRunning(testType);
    try {
      const result = await simulatorApi.adversarial({ test_type: testType, event_count: 60 });
      setResults(prev => ({ ...prev, [testType]: result }));
    } catch (err) {
      console.error(err);
    } finally {
      setRunning(null);
    }
  };

  const runAll = async () => {
    setRunningAll(true);
    for (const test of TESTS) {
      await runTest(test.type);
    }
    setRunningAll(false);
  };

  return (
    <div className="max-w-[1400px] mx-auto px-6 py-8 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="font-serif text-3xl font-bold text-warm-text">Adversarial Behavior Lab</h1>
          <p className="text-sm text-warm-secondary mt-1">
            Challenge the detection engine with synthetic adversarial sessions
          </p>
        </div>
        <button
          onClick={runAll}
          disabled={runningAll}
          className="px-4 py-2 bg-accent-red text-white text-xs font-mono font-semibold tracking-wide hover:bg-accent-red/90 transition-colors disabled:opacity-50"
        >
          {runningAll ? 'RUNNING ALL TESTS...' : 'RUN ALL TESTS'}
        </button>
      </div>

      {/* Key Insight */}
      <div className="card p-4 border-l-4 border-l-accent-amber">
        <div className="text-[10px] text-accent-amber font-mono font-semibold mb-1 tracking-wide uppercase">Key Insight</div>
        <p className="text-xs text-warm-secondary">
          Simple rules like &quot;fast = bot&quot; are insufficient for reliable detection. The automata
          engine combines multiple behavioral signals — navigation patterns, interaction diversity,
          timing regularity, and sequence consistency — to form a holistic assessment.
        </p>
      </div>

      {/* Tests Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {TESTS.map(test => {
          const result = results[test.type];
          return (
            <div key={test.type} className="card p-6">
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-sm font-semibold text-warm-text">{test.name}</h3>
                {!result ? (
                  <button
                    onClick={() => runTest(test.type)}
                    disabled={running === test.type}
                    className="px-3 py-1 text-[10px] font-mono font-semibold bg-forest text-white hover:bg-forest-dark transition-colors disabled:opacity-50"
                  >
                    {running === test.type ? 'RUNNING...' : 'RUN'}
                  </button>
                ) : (
                  <ClassificationBadge classification={result.classification} size="sm" />
                )}
              </div>
              <p className="text-xs text-warm-muted mb-3">{test.description}</p>

              {result && (
                <div className="space-y-3">
                  <div className="flex items-center gap-4">
                    <div className="text-2xl font-bold font-mono" style={{
                      color: result.score > 70 ? '#C4432B' : result.score > 40 ? '#B87333' : '#2D5A3D'
                    }}>
                      {result.score}/100
                    </div>
                    <div className="text-[10px] text-warm-muted font-mono tracking-wide uppercase">Automation Score</div>
                  </div>

                  {result.scoring_breakdown && (
                    <div className="space-y-2">
                      {Object.entries(result.scoring_breakdown).map(([key, val]) => (
                        <ScoreBar key={key} label={key.replace(/_/g, ' ')} value={val as number} />
                      ))}
                    </div>
                  )}

                  {result.explanation && (
                    <div className="mt-3 pt-3 border-t border-cream-border">
                      <div className="text-xs text-warm-secondary font-mono leading-relaxed">
                        {result.explanation}
                      </div>
                    </div>
                  )}

                  <Link
                    href={`/sessions/${result.session_id}`}
                    className="inline-block text-xs text-forest hover:underline font-mono mt-2"
                  >
                    View Full Session &rarr;
                  </Link>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Summary Table */}
      {Object.keys(results).length > 1 && (
        <div className="card p-6">
          <h3 className="text-xs font-mono font-semibold text-warm-text mb-4 tracking-wide uppercase">Results Summary</h3>
          <table className="w-full text-xs font-mono">
            <thead className="text-warm-muted">
              <tr className="border-b border-cream-border">
                <th className="text-left py-2 tracking-wide uppercase">Test</th>
                <th className="text-left py-2 tracking-wide uppercase">Classification</th>
                <th className="text-right py-2 tracking-wide uppercase">Score</th>
                <th className="text-right py-2 tracking-wide uppercase">Timing</th>
                <th className="text-right py-2 tracking-wide uppercase">Repetition</th>
                <th className="text-right py-2 tracking-wide uppercase">Nav Diversity</th>
              </tr>
            </thead>
            <tbody>
              {TESTS.filter(t => results[t.type]).map(test => {
                const r = results[test.type];
                return (
                  <tr key={test.type} className="border-b border-cream-border/50">
                    <td className="py-2 text-warm-text">{test.name.split(':')[0]}</td>
                    <td className="py-2"><ClassificationBadge classification={r.classification} size="sm" /></td>
                    <td className="py-2 text-right font-semibold" style={{
                      color: r.score > 70 ? '#C4432B' : r.score > 40 ? '#B87333' : '#2D5A3D'
                    }}>{r.score}</td>
                    <td className="py-2 text-right text-warm-muted">
                      {r.scoring_breakdown?.timing_regularity?.toFixed(0)}
                    </td>
                    <td className="py-2 text-right text-warm-muted">
                      {r.scoring_breakdown?.repetition?.toFixed(0)}
                    </td>
                    <td className="py-2 text-right text-warm-muted">
                      {r.scoring_breakdown?.navigation_diversity?.toFixed(0)}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
