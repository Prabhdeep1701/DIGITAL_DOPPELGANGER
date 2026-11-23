'use client';

import { useEffect, useState, useRef } from 'react';
import { useParams } from 'next/navigation';
import { sessionsApi } from '@/lib/api';
import ClassificationBadge from '@/components/ClassificationBadge';
import ScoreBar from '@/components/ScoreBar';
import EventTimeline from '@/components/EventTimeline';

export default function SessionDetailPage() {
  const { id } = useParams();
  const [session, setSession] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [replayIdx, setReplayIdx] = useState(-1);
  const [replaySpeed, setReplaySpeed] = useState(1);
  const [isPlaying, setIsPlaying] = useState(false);
  const replayTimer = useRef<NodeJS.Timeout>();

  useEffect(() => {
    if (id) {
      sessionsApi.get(id as string)
        .then(setSession)
        .catch(console.error)
        .finally(() => setLoading(false));
    }
  }, [id]);

  useEffect(() => {
    if (isPlaying && session?.events) {
      replayTimer.current = setInterval(() => {
        setReplayIdx(prev => {
          if (prev >= session.events.length - 1) {
            setIsPlaying(false);
            return prev;
          }
          return prev + 1;
        });
      }, 500 / replaySpeed);
    }
    return () => clearInterval(replayTimer.current);
  }, [isPlaying, replaySpeed, session]);

  if (loading) return <div className="max-w-[1400px] mx-auto px-6 py-8 text-warm-muted font-mono text-sm animate-pulse">Loading session...</div>;
  if (!session) return <div className="max-w-[1400px] mx-auto px-6 py-8 text-warm-muted font-mono">Session not found.</div>;

  const scoring = session.scoring_breakdown;
  const replayEvent = replayIdx >= 0 ? session.events[replayIdx] : null;

  const currentStates = replayIdx >= 0 && session.automaton_states
    ? session.automaton_states.filter((s: any) =>
        s.event_id === replayEvent?.id
      )
    : [];

  return (
    <div className="max-w-[1400px] mx-auto px-6 py-8 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="font-serif text-3xl font-bold text-warm-text">Session {String(id).slice(0, 12)}...</h1>
          <div className="flex items-center gap-3 mt-2">
            <ClassificationBadge classification={session.classification} />
            {session.is_simulated && (
              <span className="tag-amber">{session.is_simulated}</span>
            )}
          </div>
        </div>
        <div className="text-right">
          <div className="text-3xl font-bold font-mono" style={{
            color: session.score > 70 ? '#C4432B' : session.score > 40 ? '#B87333' : '#2D5A3D'
          }}>
            {session.score?.toFixed(1)}/100
          </div>
          <div className="text-[10px] text-warm-muted font-mono tracking-wide uppercase">Behavioral Automation Score</div>
        </div>
      </div>

      {/* Session Info */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="card p-4">
          <div className="text-[10px] text-warm-muted font-mono tracking-wide uppercase">Events</div>
          <div className="text-xl font-bold font-mono text-forest mt-1">{session.events?.length || 0}</div>
        </div>
        <div className="card p-4">
          <div className="text-[10px] text-warm-muted font-mono tracking-wide uppercase">Detections</div>
          <div className="text-xl font-bold font-mono text-accent-red mt-1">{session.detections?.length || 0}</div>
        </div>
        <div className="card p-4">
          <div className="text-[10px] text-warm-muted font-mono tracking-wide uppercase">Started</div>
          <div className="text-sm font-mono text-warm-text mt-1">
            {session.started_at ? new Date(session.started_at).toLocaleString() : '-'}
          </div>
        </div>
        <div className="card p-4">
          <div className="text-[10px] text-warm-muted font-mono tracking-wide uppercase">Duration</div>
          <div className="text-sm font-mono text-warm-text mt-1">
            {session.started_at && session.ended_at
              ? `${((new Date(session.ended_at).getTime() - new Date(session.started_at).getTime()) / 1000).toFixed(1)}s`
              : '-'}
          </div>
        </div>
      </div>

      {/* Scoring Breakdown */}
      {scoring && (
        <div className="card p-6">
          <h3 className="text-xs font-mono font-semibold text-warm-text mb-4 tracking-wide uppercase">Scoring Breakdown</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {scoring.breakdown && Object.entries(scoring.breakdown).map(([key, val]) => (
              <ScoreBar key={key} label={key.replace(/_/g, ' ')} value={val as number} />
            ))}
          </div>
          {scoring.explanations?.length > 0 && (
            <div className="mt-4 pt-4 border-t border-cream-border space-y-2">
              <h4 className="text-[10px] font-semibold text-warm-text font-mono tracking-wide uppercase">Explanations</h4>
              {scoring.explanations.map((exp: string, i: number) => (
                <div key={i} className="text-xs text-warm-secondary font-mono flex items-start gap-2">
                  <span className="text-accent-red mt-0.5">!</span>
                  {exp}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Session Replay */}
      <div className="card p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-xs font-mono font-semibold text-warm-text tracking-wide uppercase">Session Replay</h3>
          <div className="flex items-center gap-3">
            <button
              onClick={() => { setReplayIdx(0); setIsPlaying(false); }}
              className="text-xs font-mono text-warm-muted hover:text-warm-text px-2 py-1 bg-cream-dark"
            >
              |&lt;
            </button>
            <button
              onClick={() => setIsPlaying(!isPlaying)}
              className="text-xs font-mono text-white px-3 py-1 bg-forest hover:bg-forest-dark transition-colors"
            >
              {isPlaying ? 'Pause' : 'Play'}
            </button>
            <button
              onClick={() => { setReplayIdx(session.events?.length - 1 || 0); setIsPlaying(false); }}
              className="text-xs font-mono text-warm-muted hover:text-warm-text px-2 py-1 bg-cream-dark"
            >
              &gt;|
            </button>
            <div className="flex gap-1">
              {[0.5, 1, 2, 5].map(speed => (
                <button
                  key={speed}
                  onClick={() => setReplaySpeed(speed)}
                  className={`text-xs font-mono px-2 py-1 ${
                    replaySpeed === speed
                      ? 'bg-forest text-white'
                      : 'bg-cream-dark text-warm-muted hover:text-warm-text'
                  }`}
                >
                  {speed}x
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Replay progress bar */}
        <div className="mb-4">
          <div className="h-1 bg-cream-dark rounded-full overflow-hidden">
            <div
              className="h-full bg-forest rounded-full transition-all"
              style={{ width: `${session.events?.length ? ((replayIdx + 1) / session.events.length) * 100 : 0}%` }}
            />
          </div>
          <div className="flex justify-between text-[10px] font-mono text-warm-muted mt-1">
            <span>Event {replayIdx + 1} / {session.events?.length || 0}</span>
            {replayEvent && (
              <span>
                {replayEvent.event_type} {replayEvent.page && `@ ${replayEvent.page}`}
              </span>
            )}
          </div>
        </div>

        {replayEvent && (
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-cream-light border border-cream-border p-3 font-mono text-xs">
              <div className="text-warm-muted mb-1 text-[10px] tracking-wide uppercase">Current Event</div>
              <div className="text-forest font-semibold">{replayEvent.event_type.toUpperCase()}</div>
              {replayEvent.page && <div className="text-warm-muted">Page: {replayEvent.page}</div>}
              {replayEvent.target && <div className="text-warm-muted">Target: {replayEvent.target}</div>}
            </div>
            <div className="bg-cream-light border border-cream-border p-3 font-mono text-xs">
              <div className="text-warm-muted mb-1 text-[10px] tracking-wide uppercase">Automaton States</div>
              {currentStates.length > 0 ? (
                currentStates.map((s: any, i: number) => (
                  <div key={i} className="flex justify-between">
                    <span className="text-warm-muted">{s.automaton_type}</span>
                    <span className="text-forest">{s.state}</span>
                  </div>
                ))
              ) : (
                <div className="text-warm-muted">-</div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Detections */}
      {session.detections?.length > 0 && (
        <div className="card p-6">
          <h3 className="text-xs font-mono font-semibold text-warm-text mb-4 tracking-wide uppercase">
            Detections ({session.detections.length})
          </h3>
          <div className="space-y-2 max-h-64 overflow-auto">
            {session.detections.map((d: any, i: number) => (
              <div key={i} className="flex items-start gap-3 p-3 bg-accent-red/5 border border-accent-red/20 text-xs font-mono">
                <span className={`px-1.5 py-0.5 text-[10px] font-semibold text-white ${
                  d.severity === 'high' || d.severity === 'critical' ? 'bg-accent-red' : 'bg-accent-amber'
                }`}>
                  {d.severity?.toUpperCase()}
                </span>
                <div className="flex-1 text-warm-secondary">{d.reason}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Event Timeline */}
      <EventTimeline events={session.events || []} maxHeight="500px" />
    </div>
  );
}
