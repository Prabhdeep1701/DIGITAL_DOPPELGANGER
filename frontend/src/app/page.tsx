'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';

export default function LandingPage() {
  const [mounted, setMounted] = useState(false);
  useEffect(() => setMounted(true), []);

  return (
    <div className="min-h-screen bg-cream">
      {/* Hero Section */}
      <section className="max-w-[1200px] mx-auto px-6 pt-16 pb-12">
        {/* Top tags */}
        <div className="flex items-center gap-2 mb-6">
          <span className="tag-green">DIGITAL_SIGNAL</span>
          <span className="tag-green">FINITE_EXTRACTION</span>
          <span className="tag-cream">LEARN_A_GHOST</span>
        </div>

        {/* Hero title */}
        <div className="max-w-3xl">
          <h1 className="font-serif text-6xl md:text-7xl font-bold tracking-tight text-warm-text leading-[1.05]">
            DIGITAL{' '}
            <span className="italic font-medium">Doppelgänger.</span>
          </h1>
          <p className="mt-6 text-base text-warm-secondary leading-relaxed max-w-2xl">
            Decoding the difference between human behavior and automated intent{' '}
            <span className="text-forest font-medium italic">
              through the mathematics of finite automata.
            </span>
          </p>
        </div>

        {/* CTA Buttons */}
        <div className="mt-8 flex items-center gap-4">
          <Link
            href="/playground"
            className="inline-flex items-center gap-2 px-6 py-2.5 bg-forest text-white text-xs font-mono font-semibold tracking-wider hover:bg-forest-dark transition-colors"
          >
            ENTER THE LAB &gt;
          </Link>
          <Link
            href="/automata"
            className="inline-flex items-center gap-2 px-6 py-2.5 border border-cream-border text-warm-secondary text-xs font-mono font-medium tracking-wider hover:bg-cream-dark transition-colors"
          >
            READ THE COMPENDIUM
          </Link>
        </div>
      </section>

      {/* Somatic vs Synthetic Kinetics */}
      <section className="max-w-[1200px] mx-auto px-6 pb-16">
        <div className="section-bar">
          <span>SOMATIC_NERVE</span>
          <span className="opacity-50">·</span>
          <span>EPISODE_00.1</span>
          <span className="ml-auto text-[10px] opacity-70">TELEMETRY_DATA · GNAC PELLET BOLSTER</span>
        </div>

        <div className="bg-white border border-cream-border border-t-0">
          <h2 className="font-serif text-3xl md:text-4xl font-bold text-warm-text px-8 pt-8 pb-6 leading-tight">
            SOMATIC VS SYNTHETIC KINETICS
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-0 divide-x divide-cream-border">
            {/* Human Intent Column */}
            <div className="px-8 pb-8">
              <div className="flex items-center gap-2 mb-3">
                <span className="tag-green">CONTEXTUAL_RANGE</span>
                <span className="tag-green">ENTROPY_STATE</span>
              </div>
              <h3 className="font-serif text-xl font-bold text-warm-text mb-3">HUMAN INTENT</h3>
              <p className="text-xs text-warm-secondary leading-relaxed mb-6">
                Organic navigation exhibits stochastic page-ordering, variable
                dwell-time distributions, and non-deterministic click trajectories
                that resist finite-state compression.
              </p>

              {/* Chart placeholder */}
              <div className="bg-cream-light border border-cream-border rounded p-4 mb-6 h-40 flex items-end gap-1">
                {mounted && Array.from({ length: 20 }).map((_, i) => (
                  <div
                    key={i}
                    className="flex-1 bg-forest/30 rounded-t transition-all"
                    style={{
                      height: `${20 + Math.random() * 70}%`,
                      backgroundColor: `rgba(45, 90, 61, ${0.2 + Math.random() * 0.4})`,
                    }}
                  />
                ))}
              </div>

              {/* Transition formula */}
              <div className="bg-cream-light border border-cream-border p-3 font-mono text-[11px] text-warm-secondary mb-6">
                <div className="text-[10px] text-warm-muted mb-1 uppercase tracking-wider">Transition Formula</div>
                <div>&delta;(S, e) → S&apos; | P(S&apos;) ~ N(&mu;, &sigma;&sup2;)</div>
                <div className="text-warm-muted mt-1">H(X) = -&Sigma; p(x) log p(x) &gt; 4.0</div>
              </div>

              {/* Bottom metrics */}
              <div className="grid grid-cols-5 gap-2">
                {[
                  { label: 'ENTROPY', value: '0.8428' },
                  { label: 'NAVIGATION', value: '74.3%' },
                  { label: 'COGNITION', value: '0.912' },
                  { label: 'TIMING', value: '1.24s' },
                  { label: 'IDLE', value: '12.6%' },
                ].map(m => (
                  <div key={m.label} className="bg-forest text-white px-2 py-1.5 text-center">
                    <div className="text-[8px] font-mono tracking-wider opacity-80">{m.label}</div>
                    <div className="text-[11px] font-mono font-bold">{m.value}</div>
                  </div>
                ))}
              </div>
            </div>

            {/* Synthetic Intent Column */}
            <div className="px-8 pb-8">
              <div className="flex items-center gap-2 mb-3">
                <span className="tag-red">BINARY_AUTOMATION</span>
                <span className="tag-amber">REPETITION</span>
              </div>
              <h3 className="font-serif text-xl font-bold text-warm-text mb-3">SYNTHETIC INTENT</h3>
              <p className="text-xs text-warm-secondary leading-relaxed mb-6">
                Automated traversal yields deterministic TypedEvent arrays,
                uniform inter-event intervals, and state-transition paths
                collapsible to a low-entropy formal language.
              </p>

              {/* Chart placeholder - more uniform bars */}
              <div className="bg-cream-light border border-cream-border rounded p-4 mb-6 h-40 flex items-end gap-1">
                {mounted && Array.from({ length: 20 }).map((_, i) => (
                  <div
                    key={i}
                    className="flex-1 rounded-t transition-all"
                    style={{
                      height: `${45 + (i % 3) * 8}%`,
                      backgroundColor: `rgba(196, 67, 43, ${0.3 + (i % 2) * 0.15})`,
                    }}
                  />
                ))}
              </div>

              {/* Transition formula */}
              <div className="bg-cream-light border border-cream-border p-3 font-mono text-[11px] text-warm-secondary mb-6">
                <div className="text-[10px] text-warm-muted mb-1 uppercase tracking-wider">Transition Formula</div>
                <div>&delta;(S, e) → S&apos; | &delta; = deterministic</div>
                <div className="text-warm-muted mt-1">H(X) = -&Sigma; p(x) log p(x) &lt; 1.5</div>
              </div>

              {/* Bottom metrics */}
              <div className="grid grid-cols-5 gap-2">
                {[
                  { label: 'ENTROPY', value: '0.1204' },
                  { label: 'REPETITION', value: '94.1%' },
                  { label: 'NAVIGATION', value: '12.0%' },
                  { label: 'TIMING', value: '0.05s' },
                  { label: 'IDLE', value: '0.0%' },
                ].map(m => (
                  <div key={m.label} className="bg-accent-red text-white px-2 py-1.5 text-center">
                    <div className="text-[8px] font-mono tracking-wider opacity-80">{m.label}</div>
                    <div className="text-[11px] font-mono font-bold">{m.value}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Three Laws of Behavioral Entropy */}
      <section className="max-w-[1200px] mx-auto px-6 pb-16">
        <div className="flex items-center gap-3 mb-2">
          <span className="tag-green">TRANS_HUMANOID</span>
          <span className="tag-cream">LEXICON_BK_32</span>
        </div>

        <h2 className="font-serif text-3xl md:text-4xl font-bold text-warm-text mb-2 leading-tight">
          THE THREE LAWS OF<br />BEHAVIORAL ENTROPY
        </h2>
        <p className="text-xs text-warm-muted mb-8 max-w-lg">
          Where deterministic machines mathematically extrapolated entropy.
          Finite state transitions expose synthetic actions that stimulate
          humanity.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Law 1 */}
          <div className="card p-6">
            <div className="flex items-center gap-3 mb-4">
              <span className="text-3xl font-serif font-bold text-forest">01</span>
              <span className="tag-green">STATE_LOCK</span>
            </div>
            <h3 className="font-serif text-lg font-bold text-warm-text mb-3">DETERMINISTIC TRAPPING</h3>
            <p className="text-xs text-warm-secondary leading-relaxed mb-4">
              Deterministic Finite Automata (DFA) map
              every observable user-interaction state
              events. Bot scripts operating on static
              code paths inevitably trap in a recognizable
              absorbing sub-chain of the browser
              interaction graph.
            </p>
            <div className="text-[11px] font-mono text-forest">
              STATEGROUND: q_TRAP &rarr;
            </div>
          </div>

          {/* Law 2 */}
          <div className="card p-6">
            <div className="flex items-center gap-3 mb-4">
              <span className="text-3xl font-serif font-bold text-forest">02</span>
              <span className="tag-green">KINETIC_EST</span>
            </div>
            <h3 className="font-serif text-lg font-bold text-warm-text mb-3">KINETIC ANTHROPOLOGY</h3>
            <p className="text-xs text-warm-secondary leading-relaxed mb-4">
              Biological hands contain inertia, stochasticity and
              micro-corrections that the optimal-time-to-task fits
              established by the peak-trough principle of Hick&apos;s
              law exhibit but finite-state equivalents cannot.
            </p>
            <div className="text-[11px] font-mono text-forest">
              &Delta;t_REACTION ~ N(0.34s, 0.12s)
            </div>
          </div>

          {/* Law 3 */}
          <div className="card p-6">
            <div className="flex items-center gap-3 mb-4">
              <span className="text-3xl font-serif font-bold text-accent-amber">03</span>
              <span className="tag-amber">DOPPELGÄNGER</span>
            </div>
            <h3 className="font-serif text-lg font-bold text-warm-text mb-3">THE LIMINAL DOPPELGÄNGER</h3>
            <p className="text-xs text-warm-secondary leading-relaxed mb-4">
              For every covert automation, one might argue,
              a human operator somewhere is running the script.
              The physical mimicry of random jitter, diverse
              clickstreams reveals the emulation beneath.
            </p>
            <div className="text-[11px] font-mono text-accent-amber">
              BASELINE DELTA: 0.012-0.084
            </div>
          </div>
        </div>
      </section>

      {/* Extracted Telemetry */}
      <section className="max-w-[1200px] mx-auto px-6 pb-16">
        <div className="section-bar mb-0">
          <span>EXTRACTED_TELEMETRY</span>
          <span className="opacity-50">·</span>
          <span>VOLUME_507</span>
        </div>

        <div className="bg-white border border-cream-border border-t-0 p-8">
          <h3 className="font-serif text-xl font-bold text-warm-text mb-6">
            FINITE AUTOMATON STATE MAP [TEST BASE: Q_0 → Q_ACCEPT]
          </h3>

          {/* State map visualization */}
          <div className="grid grid-cols-5 md:grid-cols-9 gap-2 mb-6">
            {['PAGE_VIEW', 'MOVE', 'HOVER', 'CLICK', 'KEY', 'SCROLL', 'SUBMIT', 'IDLE', 'END'].map((symbol, i) => (
              <div key={symbol} className={`text-center p-2 ${i < 5 ? 'bg-forest text-white' : 'bg-cream-dark text-warm-text'}`}>
                <div className="text-[9px] font-mono font-semibold tracking-wide">{symbol}</div>
              </div>
            ))}
          </div>

          <div className="flex items-center gap-4 mb-4">
            <span className="tag-green">BEHAVIORAL_VECTOR</span>
            <span className="tag-cream">ENTROPY MAPPING IN AUTOMATA ORDO STREAM.</span>
          </div>

          {/* State transition path */}
          <div className="bg-cream-light border border-cream-border p-4 font-mono text-[11px] text-warm-secondary overflow-x-auto">
            <div className="flex items-center gap-2 flex-wrap">
              <span className="text-forest font-semibold">q₀</span>
              <span className="text-warm-muted">&rarr;</span>
              <span>LANDING</span>
              <span className="text-warm-muted">&rarr;</span>
              <span>BROWSING</span>
              <span className="text-warm-muted">&rarr;</span>
              <span>INTERACTING</span>
              <span className="text-warm-muted">&rarr;</span>
              <span>FORM_INPUT</span>
              <span className="text-warm-muted">&rarr;</span>
              <span className="text-forest font-semibold">COMPLETING</span>
              <span className="text-warm-muted">&rarr;</span>
              <span className="font-semibold text-forest">q_ACCEPT</span>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="dark-section">
        <div className="max-w-[1200px] mx-auto px-6 py-16">
          <div className="flex items-center gap-2 mb-4">
            <span className="tag-green">INCOG_PROTOCOL_ACCESS</span>
          </div>
          <h2 className="font-serif text-3xl md:text-4xl font-bold text-cream-light mb-4 leading-tight">
            TEST YOUR PLATFORM&apos;S<br />SHADOW
          </h2>
          <p className="text-sm text-cream-border max-w-lg mb-8 leading-relaxed">
            Connect your telemetry stream or small file lightweight
            order-identity automated threats, exploit synthetic
            transactions, and prevent legitimate human-traffic.
          </p>
          <div className="flex items-center gap-4">
            <Link
              href="/playground"
              className="inline-flex items-center gap-2 px-6 py-2.5 bg-forest text-white text-xs font-mono font-semibold tracking-wider hover:bg-forest-light transition-colors"
            >
              INITIALIZE SANDBOX
            </Link>
            <Link
              href="/analytics"
              className="inline-flex items-center gap-2 px-6 py-2.5 border border-cream-border/30 text-cream-dark text-xs font-mono font-medium tracking-wider hover:bg-white/5 transition-colors"
            >
              READ THE COMPENDIUM
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-cream-border">
        <div className="max-w-[1200px] mx-auto px-6 py-8">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 mb-8">
            <div>
              <h4 className="font-serif font-bold text-sm text-warm-text mb-3">DIGITAL DOPPELGÄNGER</h4>
              <p className="text-[11px] text-warm-muted leading-relaxed">
                Automata-based behavioral intelligence for detecting automated interaction patterns.
              </p>
            </div>
            <div>
              <h4 className="text-[10px] font-mono font-semibold text-warm-secondary mb-3 tracking-wider">TELEMETRY</h4>
              <div className="space-y-1.5">
                <Link href="/dashboard" className="block text-[11px] text-warm-muted hover:text-forest">Dashboard</Link>
                <Link href="/sessions" className="block text-[11px] text-warm-muted hover:text-forest">Sessions</Link>
                <Link href="/analytics" className="block text-[11px] text-warm-muted hover:text-forest">Analytics</Link>
              </div>
            </div>
            <div>
              <h4 className="text-[10px] font-mono font-semibold text-warm-secondary mb-3 tracking-wider">RESEARCH</h4>
              <div className="space-y-1.5">
                <Link href="/automata" className="block text-[11px] text-warm-muted hover:text-forest">Automata Lab</Link>
                <Link href="/attack-lab" className="block text-[11px] text-warm-muted hover:text-forest">Attack Lab</Link>
                <Link href="/simulator" className="block text-[11px] text-warm-muted hover:text-forest">Simulator</Link>
              </div>
            </div>
            <div>
              <h4 className="text-[10px] font-mono font-semibold text-warm-secondary mb-3 tracking-wider">ENGAGE</h4>
              <div className="space-y-1.5">
                <Link href="/playground" className="block text-[11px] text-warm-muted hover:text-forest">Playground</Link>
                <Link href="/compare" className="block text-[11px] text-warm-muted hover:text-forest">Compare Sessions</Link>
              </div>
            </div>
          </div>

          <div className="flex items-center justify-between pt-6 border-t border-cream-border text-[10px] font-mono text-warm-muted">
            <span>© 2026 DIGITAL DOPPELGÄNGER LAB · FORENSIC COMPUTATION &amp; AUTOMATA METABOLISM</span>
            <span>PROTOCOLS: REST+WS · LAB 27-003-002</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
