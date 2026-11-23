'use client';

import { useEffect, useState } from 'react';
import { automataApi } from '@/lib/api';
import AutomataGraph from '@/components/AutomataGraph';

export default function AutomataLabPage() {
  const [definitions, setDefinitions] = useState<any>(null);
  const [selectedAutomaton, setSelectedAutomaton] = useState(0);
  const [generatedSeq, setGeneratedSeq] = useState<any>(null);
  const [counterexample, setCounterexample] = useState<any>(null);
  const [processResult, setProcessResult] = useState<any>(null);
  const [customSequence, setCustomSequence] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    automataApi.definitions()
      .then(setDefinitions)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const generateSequence = async (type: string) => {
    const result = await automataApi.generateSequence(type, 15);
    setGeneratedSeq(result);
  };

  const processCustomSequence = async () => {
    if (!customSequence.trim()) return;
    const symbols = customSequence.split(',').map(s => s.trim());
    const events = symbols.map((s, i) => ({
      event_type: s.toLowerCase(),
      timestamp: Date.now() / 1000 + i * 0.5,
    }));
    const result = await automataApi.processSequence(events);
    setProcessResult(result);

    const ce = await automataApi.counterexample(events);
    setCounterexample(ce);
  };

  if (loading) {
    return (
      <div className="max-w-[1400px] mx-auto px-6 py-10">
        <div className="text-warm-muted font-mono text-sm animate-pulse">Loading automata definitions...</div>
      </div>
    );
  }
  if (!definitions) {
    return (
      <div className="max-w-[1400px] mx-auto px-6 py-10">
        <div className="text-warm-secondary font-mono">Failed to load automata data.</div>
      </div>
    );
  }

  const automaton = definitions.automata?.[selectedAutomaton];

  return (
    <div className="max-w-[1400px] mx-auto px-6 py-8 space-y-6">
      {/* Breadcrumb tags */}
      <div className="flex items-center gap-2 flex-wrap">
        <span className="tag-green">DFA LABORATORY</span>
        <span className="tag-cream">SPECIMEN_CLASS: BEHAVIORAL</span>
        <span className="tag-cream">ENGINE: PRODUCT_AUTOMATON</span>
      </div>

      {/* Main header */}
      <div className="section-bar">
        <span>REGISTRY 04.1</span>
        <span className="opacity-60">|</span>
        <span>CATALOGED SPECIMEN</span>
      </div>
      <div className="bg-white border border-cream-border p-8">
        <h1 className="font-serif text-4xl md:text-5xl font-bold text-warm-text leading-tight">
          SPECIMEN DFA-709 //<br />
          <span className="text-forest">BEHAVIORAL FINITE<br />AUTOMATON ENGINE</span>
        </h1>
        <div className="flex items-center gap-3 mt-4 flex-wrap">
          {definitions.automata?.map((a: any, i: number) => (
            <button
              key={a.name}
              onClick={() => setSelectedAutomaton(i)}
              className={`font-mono text-[10px] font-semibold tracking-wide px-3 py-1 transition-colors ${
                selectedAutomaton === i
                  ? 'bg-forest text-white'
                  : 'bg-cream-dark text-warm-secondary hover:bg-cream-border'
              }`}
            >
              {a.name.toUpperCase()} DFA
            </button>
          ))}
          <span className="tag-cream">Σ = {definitions.alphabet?.length} SYMBOLS</span>
          <span className="tag-cream">PRODUCT: N×I×T×C</span>
        </div>
      </div>

      {/* Main content area */}
      {automaton && (
        <>
          {/* Two column: Graph + Trajectory */}
          <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
            {/* Left: Graph visualization (3 cols) */}
            <div className="lg:col-span-3 space-y-4">
              {/* Tags above graph */}
              <div className="flex items-center gap-2 flex-wrap">
                <span className="tag-green">Q_{'{'}ACTIVE{'}'}</span>
                <span className="tag-cream">EPOCH: {automaton.states.length} STATES</span>
                <span className={automaton.suspicious_states.length > 0 ? 'tag-red' : 'tag-cream'}>
                  SUSPICIOUS: {automaton.suspicious_states.length}
                </span>
              </div>

              <AutomataGraph
                states={automaton.states}
                transitions={automaton.transitions}
                suspiciousStates={automaton.suspicious_states}
                acceptingStates={automaton.accepting_states}
                name={`${automaton.name.charAt(0).toUpperCase() + automaton.name.slice(1)} Automaton`}
              />

              {/* State list below graph */}
              <div className="card p-4">
                <div className="flex items-center gap-2 mb-3">
                  <span className="tag-green">Q (STATES)</span>
                  <span className="text-[10px] font-mono text-warm-muted">{automaton.states.length} total</span>
                </div>
                <div className="flex flex-wrap gap-1">
                  {automaton.states.map((s: string) => (
                    <span
                      key={s}
                      className={`px-2 py-0.5 text-[10px] font-mono font-medium border ${
                        automaton.suspicious_states.includes(s)
                          ? 'bg-accent-red/5 text-accent-red border-accent-red/30'
                          : automaton.accepting_states.includes(s)
                          ? 'bg-forest/5 text-forest border-forest/30'
                          : 'bg-cream-light text-warm-secondary border-cream-border'
                      }`}
                    >
                      {s}
                    </span>
                  ))}
                </div>
              </div>
            </div>

            {/* Right: Trajectory + Details (2 cols) */}
            <div className="lg:col-span-2 space-y-4">
              {/* Continuous Dynamic Trajectory */}
              <div className="card p-4">
                <div className="flex items-center gap-2 mb-3">
                  <span className="tag-green">δ</span>
                  <span className="tag-cream">ACTIVE | TRANSITION MAP</span>
                </div>
                <h3 className="font-serif text-lg font-bold text-warm-text mb-1">Continuous Dynamic Trajectory</h3>
                <p className="text-xs text-warm-secondary mb-3">
                  Staged δ(q,σ) transition function trace. Tracks state evolution through the
                  behavioral input sequence in real-time.
                </p>
                <div className="text-[10px] font-mono text-warm-muted mb-3">
                  Motor: transition frequency: δ &ge; fn
                </div>

                {/* Transition table */}
                <div className="max-h-64 overflow-auto space-y-0.5">
                  {Object.entries(automaton.transitions).map(([state, trans]) => (
                    Object.entries(trans as Record<string, string>)
                      .filter(([sym]) => sym !== '*')
                      .slice(0, 5)
                      .map(([sym, next]) => (
                        <div key={`${state}-${sym}`} className="flex items-center gap-1 text-[11px] font-mono py-0.5">
                          <span className="text-warm-muted">δ(</span>
                          <span className="text-accent-amber">{state}</span>
                          <span className="text-warm-muted">,</span>
                          <span className="text-forest">{sym}</span>
                          <span className="text-warm-muted">) →</span>
                          <span className={automaton.suspicious_states.includes(next as string) ? 'text-accent-red font-semibold' : 'text-forest font-semibold'}>
                            {next as string}
                          </span>
                        </div>
                      ))
                  ))}
                </div>
              </div>

              {/* Formal Definition */}
              <div className="card p-4">
                <div className="flex items-center gap-2 mb-3">
                  <span className="tag-green">FORMAL SPEC</span>
                </div>
                <div className="font-mono text-[11px] space-y-1.5 text-warm-secondary">
                  <div><span className="text-forest font-semibold">DFA</span> = (Q, Σ, δ, q₀, F)</div>
                  <div>
                    <span className="text-forest font-semibold">q₀</span> = <span className="text-accent-amber">{automaton.start_state}</span>
                  </div>
                  <div>
                    <span className="text-forest font-semibold">F</span> = {'{'}{automaton.accepting_states.join(', ')}{'}'}
                  </div>
                </div>
              </div>

              {/* Alphabet */}
              <div className="card p-4">
                <div className="flex items-center gap-2 mb-3">
                  <span className="tag-green">Σ (ALPHABET)</span>
                </div>
                <div className="flex flex-wrap gap-1">
                  {definitions.alphabet?.map((s: string) => (
                    <span key={s} className="px-1.5 py-0.5 bg-forest/5 text-forest border border-forest/20 text-[9px] font-mono">
                      {s}
                    </span>
                  ))}
                </div>
              </div>

              {/* Event Mapping */}
              <div className="card p-4">
                <div className="flex items-center gap-2 mb-3">
                  <span className="tag-cream">EVENT → SYMBOL MAPPING</span>
                </div>
                <div className="max-h-40 overflow-auto space-y-0.5">
                  {Object.entries(definitions.event_mapping || {}).map(([raw, sym]) => (
                    <div key={raw} className="flex items-center gap-2 text-[10px] font-mono">
                      <span className="text-warm-muted w-28 truncate">{raw}</span>
                      <span className="text-warm-muted">→</span>
                      <span className="text-forest font-semibold">{String(sym)}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Bottom stat cards */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="card p-4">
              <div className="flex items-center gap-2 mb-2">
                <span className="tag-green">CURRENT_LETTER</span>
              </div>
              <div className="font-serif text-lg font-bold text-warm-text">{automaton.start_state}</div>
              <div className="text-[10px] font-mono text-warm-muted">Start state</div>
            </div>
            <div className="card p-4">
              <div className="flex items-center gap-2 mb-2">
                <span className="tag-cream">NODE_STATE</span>
              </div>
              <div className="font-serif text-lg font-bold text-warm-text">{automaton.states.length}</div>
              <div className="text-[10px] font-mono text-warm-muted">Total nodes in Q</div>
            </div>
            <div className="card p-4">
              <div className="flex items-center gap-2 mb-2">
                <span className="tag-cream">ACTIVE_CYCLES</span>
              </div>
              <div className="font-serif text-lg font-bold text-forest">
                {Object.keys(automaton.transitions).length}
              </div>
              <div className="text-[10px] font-mono text-warm-muted">Configured states</div>
            </div>
            <div className="card p-4">
              <div className="flex items-center gap-2 mb-2">
                <span className="tag-cream">LATEST_SCOUT</span>
              </div>
              <div className="font-serif text-lg font-bold text-accent-amber">
                {automaton.suspicious_states.length > 0 ? automaton.suspicious_states[0] : 'CLEAR'}
              </div>
              <div className="text-[10px] font-mono text-warm-muted">Scout detection</div>
            </div>
          </div>

          {/* Description */}
          <div className="card p-5 border-l-4 border-l-forest">
            <div className="flex items-center gap-2 mb-2">
              <span className="tag-green">AUTOMATON ID: {automaton.name.toUpperCase()}_DFA_001</span>
            </div>
            <p className="text-xs text-warm-secondary leading-relaxed">
              Specimen DFA-709 demonstrates how deterministic finite automata can model
              behavioral patterns and detect automated interactions. Each state captures a
              behavioral mode, while transitions encode the rules of legitimate user activity.
              Violations of these rules — encoded as transitions to suspicious states — flag
              potential automation.
            </p>
          </div>
        </>
      )}

      {/* Sequence Generator & Tester */}
      <div className="section-bar mt-8">
        <span>SEQUENCE GENERATOR</span>
        <span className="opacity-60">|</span>
        <span>BEHAVIORAL TEST ENGINE</span>
      </div>
      <div className="card p-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Generate */}
          <div className="space-y-3">
            <h3 className="font-serif text-lg font-bold text-warm-text">Generate Test Sequences</h3>
            <p className="text-xs text-warm-secondary">Generate valid, suspicious, or random event sequences for analysis.</p>
            <div className="flex gap-2 flex-wrap">
              <button
                onClick={() => generateSequence('valid')}
                className="px-3 py-1.5 bg-forest/10 text-forest text-xs font-mono font-semibold border border-forest/20 hover:bg-forest/20 transition-colors"
              >
                VALID SEQUENCE
              </button>
              <button
                onClick={() => generateSequence('suspicious')}
                className="px-3 py-1.5 bg-accent-red/10 text-accent-red text-xs font-mono font-semibold border border-accent-red/20 hover:bg-accent-red/20 transition-colors"
              >
                SUSPICIOUS SEQUENCE
              </button>
              <button
                onClick={() => generateSequence('invalid')}
                className="px-3 py-1.5 bg-accent-amber/10 text-accent-amber text-xs font-mono font-semibold border border-accent-amber/20 hover:bg-accent-amber/20 transition-colors"
              >
                RANDOM SEQUENCE
              </button>
            </div>

            {generatedSeq && (
              <div className="bg-cream-light border border-cream-border rounded p-3 font-mono text-xs">
                <div className="text-warm-muted mb-2">{generatedSeq.description}</div>
                <div className="flex flex-wrap gap-1 mb-2">
                  {generatedSeq.sequence.map((s: string, i: number) => (
                    <span key={i} className="px-1.5 py-0.5 bg-forest/10 text-forest border border-forest/20">
                      {s}
                    </span>
                  ))}
                </div>
                <div className={`text-xs font-semibold ${generatedSeq.is_accepted ? 'text-forest' : 'text-accent-red'}`}>
                  {generatedSeq.is_accepted ? '✓ ACCEPTED' : '✗ NOT ACCEPTED'} by navigation automaton
                </div>
              </div>
            )}
          </div>

          {/* Custom sequence */}
          <div className="space-y-3">
            <h3 className="font-serif text-lg font-bold text-warm-text">Custom Sequence Input</h3>
            <p className="text-xs text-warm-secondary">Enter comma-separated event types to process through the automata engine.</p>
            <textarea
              value={customSequence}
              onChange={e => setCustomSequence(e.target.value)}
              placeholder="page_view, mouse_move, mouse_click, form_focus, key_press, form_submit"
              className="w-full bg-cream-light border border-cream-border rounded px-3 py-2 text-xs text-warm-text font-mono focus:outline-none focus:border-forest h-20 resize-none"
            />
            <button
              onClick={processCustomSequence}
              className="px-4 py-2 bg-forest text-white text-xs font-mono font-semibold hover:bg-forest-dark transition-colors"
            >
              PROCESS SEQUENCE
            </button>

            {processResult && (
              <div className="bg-cream-light border border-cream-border rounded p-3 font-mono text-[11px] max-h-48 overflow-auto">
                <div className="text-warm-muted mb-2 font-semibold">Processing Results:</div>
                {processResult.results?.map((r: any, i: number) => (
                  <div key={i} className="flex items-center gap-2 py-0.5">
                    <span className="text-forest font-semibold">{r.symbol}</span>
                    <span className="text-warm-muted">→</span>
                    <span className="text-warm-text">({r.product_state.navigation}, {r.product_state.interaction})</span>
                    {r.is_suspicious && <span className="tag-red">SUSPICIOUS</span>}
                  </div>
                ))}
              </div>
            )}

            {counterexample?.found && (
              <div className="bg-accent-red/5 border border-accent-red/20 rounded p-3 font-mono text-xs">
                <div className="text-accent-red font-semibold mb-2">Counterexample Found</div>
                <div className="space-y-1 text-warm-secondary">
                  <div>Violation at event #{counterexample.violation_index + 1}</div>
                  <div>Input: <span className="text-accent-red font-semibold">{counterexample.actual_symbol}</span></div>
                  <div>Expected: <span className="text-forest font-semibold">{counterexample.expected_symbols?.join(' / ')}</span></div>
                  <div>State: <span className="text-accent-amber font-semibold">{counterexample.automaton_state}</span></div>
                  <div className="mt-2 text-warm-text">{counterexample.transition_detail}</div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="flex items-center justify-between text-[10px] font-mono text-warm-muted pt-4 border-t border-cream-border">
        <span>AUTOMATA ENGINE v1.0</span>
        <span>PRODUCT AUTOMATON: NAVIGATION × INTERACTION × TIMING × CONSISTENCY</span>
      </div>
    </div>
  );
}
