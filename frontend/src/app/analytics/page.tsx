'use client';

import { useState } from 'react';
import { experimentsApi } from '@/lib/api';

export default function AnalyticsPage() {
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [config, setConfig] = useState({ human: 100, bot: 100, adversarial: 100 });

  const runExperiment = async () => {
    setLoading(true);
    try {
      const data = await experimentsApi.run({
        human_count: config.human,
        bot_count: config.bot,
        adversarial_count: config.adversarial,
      });
      setResult(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const getScoreColor = (val: number) => {
    if (val >= 0.8) return '#2D5A3D';
    if (val >= 0.6) return '#B87333';
    return '#C4432B';
  };

  return (
    <div className="max-w-[1400px] mx-auto px-6 py-8 space-y-8">
      {/* Page breadcrumb */}
      <div className="flex items-center gap-2 text-[10px] font-mono text-warm-muted">
        <span>DD → ANALYTICS</span>
        <span>/</span>
        <span>EXPERIMENTS</span>
      </div>

      {/* Header Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2">
          <div className="flex flex-wrap gap-1.5 mb-4">
            <span className="tag-green">BEHAVIORAL_FORENSICS</span>
            <span className="tag-green">DFA_v2.1</span>
            <span className="tag-cream">SYNTHETIC DATA ONLY</span>
          </div>
          <h1 className="font-serif text-4xl md:text-5xl font-bold text-warm-text leading-tight">
            AUTOMATON VS.<br />BIOLOGICAL
          </h1>
          <p className="font-serif text-xl md:text-2xl italic text-forest-light mt-2">
            kinetic discriminator matrix
          </p>
          <p className="text-xs text-warm-muted mt-3 font-mono">↓</p>
        </div>

        {/* Right side: quick metrics if results exist */}
        {result && (
          <div className="space-y-3">
            <div className="card p-4 text-center">
              <div className="text-[10px] font-mono text-warm-muted tracking-wide uppercase mb-1">ACCURACY_METRIC</div>
              <div className="font-serif text-4xl font-bold" style={{ color: getScoreColor(result.accuracy) }}>
                {result.accuracy.toFixed(3)}
              </div>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div className="card p-3 text-center">
                <div className="text-[10px] font-mono text-warm-muted mb-1">PRECISION</div>
                <div className="font-serif text-2xl font-bold text-forest">{(result.precision * 100).toFixed(1)}%</div>
              </div>
              <div className="card p-3 text-center">
                <div className="text-[10px] font-mono text-warm-muted mb-1">RECALL</div>
                <div className="font-serif text-2xl font-bold text-forest">{(result.recall * 100).toFixed(1)}%</div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Results: Metrics + Confusion Matrix */}
      {result && (
        <div className="space-y-8">
          {/* Key Metrics Row */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[
              { label: 'ACCURACY', value: result.accuracy, fmt: (v: number) => (v * 100).toFixed(1) + '%' },
              { label: 'PRECISION', value: result.precision, fmt: (v: number) => (v * 100).toFixed(1) + '%' },
              { label: 'RECALL', value: result.recall, fmt: (v: number) => (v * 100).toFixed(1) + '%' },
              { label: 'F1 SCORE', value: result.f1_score, fmt: (v: number) => (v * 100).toFixed(1) + '%' },
            ].map(m => (
              <div key={m.label} className="card p-5 text-center">
                <div className="text-[10px] font-mono text-warm-muted tracking-wide mb-2">{m.label}</div>
                <div className="font-serif text-3xl font-bold" style={{ color: getScoreColor(m.value) }}>
                  {m.fmt(m.value)}
                </div>
              </div>
            ))}
          </div>

          {/* Additional Metrics */}
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            <div className="card p-4">
              <div className="text-[10px] font-mono text-warm-muted tracking-wide">TOTAL SESSIONS</div>
              <div className="text-xl font-mono font-bold text-forest mt-1">{result.total_sessions}</div>
            </div>
            <div className="card p-4">
              <div className="text-[10px] font-mono text-warm-muted tracking-wide">FALSE POSITIVE RATE</div>
              <div className="text-xl font-mono font-bold text-accent-red mt-1">
                {(result.false_positive_rate * 100).toFixed(1)}%
              </div>
            </div>
            <div className="card p-4">
              <div className="text-[10px] font-mono text-warm-muted tracking-wide">FALSE NEGATIVE RATE</div>
              <div className="text-xl font-mono font-bold text-accent-amber mt-1">
                {(result.false_negative_rate * 100).toFixed(1)}%
              </div>
            </div>
          </div>

          {/* Confusion Matrix */}
          <div className="card p-6">
            <div className="section-bar mb-4 -mx-6 -mt-6 px-6 pt-3 pb-3">
              CONFUSION MATRIX
            </div>
            <div className="max-w-md mx-auto mt-4">
              <table className="w-full text-sm font-mono text-center">
                <thead>
                  <tr>
                    <th className="p-3"></th>
                    <th className="p-3 text-[10px] text-forest font-semibold tracking-wide">PREDICTED HUMAN</th>
                    <th className="p-3 text-[10px] text-accent-red font-semibold tracking-wide">PREDICTED BOT</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td className="p-3 text-[10px] text-forest font-semibold tracking-wide">ACTUAL HUMAN</td>
                    <td className="p-3">
                      <div className="bg-forest/10 border border-forest/20 rounded p-3">
                        <span className="text-2xl font-bold text-forest">{result.confusion_matrix.true_positive}</span>
                        <div className="text-[9px] text-warm-muted mt-1">TP</div>
                      </div>
                    </td>
                    <td className="p-3">
                      <div className="bg-accent-red/10 border border-accent-red/20 rounded p-3">
                        <span className="text-2xl font-bold text-accent-red">{result.confusion_matrix.false_negative}</span>
                        <div className="text-[9px] text-warm-muted mt-1">FN</div>
                      </div>
                    </td>
                  </tr>
                  <tr>
                    <td className="p-3 text-[10px] text-accent-red font-semibold tracking-wide">ACTUAL BOT</td>
                    <td className="p-3">
                      <div className="bg-accent-amber/10 border border-accent-amber/20 rounded p-3">
                        <span className="text-2xl font-bold text-accent-amber">{result.confusion_matrix.false_positive}</span>
                        <div className="text-[9px] text-warm-muted mt-1">FP</div>
                      </div>
                    </td>
                    <td className="p-3">
                      <div className="bg-forest/10 border border-forest/20 rounded p-3">
                        <span className="text-2xl font-bold text-forest">{result.confusion_matrix.true_negative}</span>
                        <div className="text-[9px] text-warm-muted mt-1">TN</div>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          {/* Per-Profile Results */}
          <div className="card p-6">
            <div className="section-bar mb-4 -mx-6 -mt-6 px-6 pt-3 pb-3">
              PER-PROFILE BREAKDOWN
            </div>
            <div className="space-y-4 mt-4">
              {Object.entries(result.per_profile || {}).map(([profile, data]: [string, any]) => (
                <div key={profile} className="bg-cream-light border border-cream-border rounded p-4">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-2">
                      <span className="w-2 h-2 rounded-full bg-forest" />
                      <span className="text-sm font-mono font-semibold text-warm-text">{profile}</span>
                    </div>
                    <span className="tag-cream">{data.count} SESSIONS</span>
                  </div>
                  <div className="grid grid-cols-3 gap-4 text-xs font-mono mb-3">
                    <div>
                      <span className="text-warm-muted">Avg Score:</span>{' '}
                      <span className="text-warm-text font-semibold">{data.avg_score}</span>
                    </div>
                    <div>
                      <span className="text-warm-muted">Min:</span>{' '}
                      <span className="text-warm-text font-semibold">{data.min_score}</span>
                    </div>
                    <div>
                      <span className="text-warm-muted">Max:</span>{' '}
                      <span className="text-warm-text font-semibold">{data.max_score}</span>
                    </div>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {Object.entries(data.classifications || {}).map(([cls, count]) => (
                      <span key={cls} className={`px-2 py-0.5 rounded text-[10px] font-mono font-semibold ${
                        cls === 'human_like' ? 'bg-forest/10 text-forest' :
                        cls === 'automated_like' ? 'bg-accent-red/10 text-accent-red' :
                        cls === 'suspicious' ? 'bg-accent-amber/10 text-accent-amber' :
                        'bg-warm-muted/10 text-warm-muted'
                      }`}>
                        {cls}: {String(count)}
                      </span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Disclaimer */}
          <div className="card p-4 border-l-4 border-l-accent-amber">
            <p className="text-xs text-warm-secondary font-mono leading-relaxed">{result.disclaimer}</p>
          </div>
        </div>
      )}

      {/* Experiment Configuration — "SYNTHETIC BEHAVIORAL BENCHMARK ENGINE" */}
      <div className="card p-6">
        <div className="section-bar mb-6 -mx-6 -mt-6 px-6 pt-3 pb-3">
          SUBSYSTEM 03.3 &middot; SYNTHETIC BEHAVIORAL BENCHMARK ENGINE
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mt-4">
          {/* Config controls */}
          <div className="space-y-5">
            <h3 className="font-serif text-lg font-bold text-warm-text">BEST OF BREED PROMPT FOR SIMULATION</h3>

            <div className="space-y-4">
              {[
                { label: 'Human Sessions', key: 'human' as const, color: '#2D5A3D', desc: 'Genuine human-like behavioral patterns with natural variance and entropy' },
                { label: 'Bot Sessions', key: 'bot' as const, color: '#C4432B', desc: 'Automated scripted sessions with deterministic timing and repetitive sequences' },
                { label: 'Adversarial Sessions', key: 'adversarial' as const, color: '#B87333', desc: 'Human-mimicking bots designed to evade the detection engine' },
              ].map(item => (
                <div key={item.key} className="flex items-start gap-3 bg-cream-light border border-cream-border rounded p-3">
                  <span className="w-2.5 h-2.5 rounded-full mt-1 flex-shrink-0" style={{ backgroundColor: item.color }} />
                  <div className="flex-1">
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-xs font-mono font-semibold text-warm-text">{item.label}</span>
                      <input
                        type="number"
                        value={config[item.key]}
                        onChange={e => setConfig(prev => ({ ...prev, [item.key]: Number(e.target.value) }))}
                        min={10}
                        max={500}
                        className="w-20 bg-white border border-cream-border rounded px-2 py-1 text-xs text-warm-text font-mono focus:outline-none focus:border-forest text-right"
                      />
                    </div>
                    <p className="text-[10px] text-warm-muted leading-relaxed">{item.desc}</p>
                  </div>
                </div>
              ))}
            </div>

            <button
              onClick={runExperiment}
              disabled={loading}
              className="w-full px-6 py-3 bg-forest text-white font-mono text-xs font-semibold tracking-wider hover:bg-forest-dark transition-colors disabled:opacity-50"
            >
              {loading ? 'EXECUTING SIMULATION...' : 'EXECUTE SET SIMULATION RUN'}
            </button>

            {loading && (
              <div className="text-[10px] text-warm-muted font-mono animate-pulse">
                Processing {config.human + config.bot + config.adversarial} synthetic sessions through the automata engine...
              </div>
            )}
          </div>

          {/* Terminal preview */}
          <div className="terminal p-4 text-[11px]">
            <div className="text-[10px] text-[#5A7A66] mb-2 tracking-wide">FORENSIC CONSOLE // SIMULATION STATUS</div>
            <div className="space-y-1">
              <div className="terminal-accent">&gt; automata_engine.init()</div>
              <div className="terminal-muted">  Loading 4 DFA modules: navigation, interaction, timing, consistency</div>
              <div className="terminal-accent">&gt; product_automaton.build()</div>
              <div className="terminal-muted">  Product state space: Nav × Int × Tim × Con</div>
              {result ? (
                <>
                  <div className="terminal-accent">&gt; experiment.complete()</div>
                  <div className="terminal-line">  Sessions processed: {result.total_sessions}</div>
                  <div className="terminal-line">  Accuracy: {(result.accuracy * 100).toFixed(1)}%</div>
                  <div className="terminal-line">  F1 Score: {(result.f1_score * 100).toFixed(1)}%</div>
                  <div className={result.false_positive_rate > 0.1 ? 'terminal-red' : 'terminal-line'}>
                    &nbsp; FPR: {(result.false_positive_rate * 100).toFixed(1)}% | FNR: {(result.false_negative_rate * 100).toFixed(1)}%
                  </div>
                </>
              ) : (
                <>
                  <div className="terminal-muted">&gt; awaiting simulation parameters...</div>
                  <div className="terminal-muted">  Configure session counts and execute when ready.</div>
                </>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Footer note */}
      <div className="text-center py-6 border-t border-cream-border">
        <p className="text-[10px] font-mono text-warm-muted">
          AUTOMATED DATA &middot; PURELY SYNTHETIC TEST TRAFFIC &middot; Influence discrimination biases
          are inherent in any deterministic classification system. The automata engine measures
          the physiological underpinning and cannot, by design, factor subjective intent.
        </p>
      </div>
    </div>
  );
}
