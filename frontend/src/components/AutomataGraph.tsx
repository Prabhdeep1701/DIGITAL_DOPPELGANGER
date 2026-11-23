'use client';

import { useMemo } from 'react';
import ReactFlow, {
  Node,
  Edge,
  Background,
  Controls,
  MarkerType,
  Position,
} from 'reactflow';
import 'reactflow/dist/style.css';

interface AutomataGraphProps {
  states: string[];
  transitions: Record<string, Record<string, string>>;
  currentState?: string;
  suspiciousStates?: string[];
  acceptingStates?: string[];
  recentTransition?: { from: string; to: string; symbol: string };
  name?: string;
}

export default function AutomataGraph({
  states,
  transitions,
  currentState,
  suspiciousStates = [],
  acceptingStates = [],
  recentTransition,
  name = 'Automaton',
}: AutomataGraphProps) {
  const { nodes, edges } = useMemo(() => {
    const cols = Math.ceil(Math.sqrt(states.length));
    const nodeList: Node[] = states.map((state, i) => {
      const row = Math.floor(i / cols);
      const col = i % cols;
      const isCurrent = state === currentState;
      const isSuspicious = suspiciousStates.includes(state);
      const isAccepting = acceptingStates.includes(state);

      let bgColor = '#FFFFFF';
      let borderColor = '#E0D8CC';
      let textColor = '#1A1A1A';
      if (isCurrent) {
        bgColor = '#E8F5EC';
        borderColor = '#2D5A3D';
        textColor = '#2D5A3D';
      }
      if (isSuspicious) {
        bgColor = isCurrent ? '#FDE8E4' : '#FFF5F3';
        borderColor = '#C4432B';
        textColor = '#C4432B';
      }
      if (isAccepting && !isSuspicious) {
        bgColor = isCurrent ? '#E8F5EC' : '#F0F8F3';
        borderColor = isCurrent ? '#2D5A3D' : '#4A7C5C';
        textColor = '#2D5A3D';
      }

      return {
        id: state,
        position: { x: col * 200, y: row * 140 },
        data: {
          label: (
            <div className="text-center">
              <div className="font-mono text-[10px] font-semibold" style={{ color: textColor }}>
                {state}
              </div>
              {isAccepting && <div className="text-[8px] text-forest mt-0.5">accepting</div>}
              {isSuspicious && <div className="text-[8px] text-accent-red mt-0.5">suspicious</div>}
            </div>
          ),
        },
        style: {
          background: bgColor,
          border: `2px solid ${borderColor}`,
          borderRadius: '4px',
          padding: '8px 12px',
          fontSize: '11px',
          boxShadow: isCurrent ? `0 0 8px ${borderColor}40` : 'none',
        },
        sourcePosition: Position.Right,
        targetPosition: Position.Left,
      };
    });

    const edgeList: Edge[] = [];
    const edgeSet = new Set<string>();

    for (const [fromState, trans] of Object.entries(transitions)) {
      for (const [symbol, toState] of Object.entries(trans)) {
        if (symbol === '*' || fromState === toState) continue;
        const key = `${fromState}-${toState}`;
        if (edgeSet.has(key)) continue;
        edgeSet.add(key);

        const isActive = recentTransition?.from === fromState && recentTransition?.to === toState;
        const isSusEdge = suspiciousStates.includes(toState);

        edgeList.push({
          id: `e-${fromState}-${toState}`,
          source: fromState,
          target: toState,
          animated: isActive,
          style: {
            stroke: isActive ? '#2D5A3D' : isSusEdge ? '#C4432B60' : '#D4CFC5',
            strokeWidth: isActive ? 2 : 1,
          },
          markerEnd: { type: MarkerType.ArrowClosed, color: isActive ? '#2D5A3D' : '#D4CFC5' },
          label: isActive ? recentTransition?.symbol : undefined,
          labelStyle: { fill: '#2D5A3D', fontSize: 10, fontFamily: 'monospace' },
          labelBgStyle: { fill: '#FFFFFF', fillOpacity: 0.9 },
        });
      }
    }

    return { nodes: nodeList, edges: edgeList };
  }, [states, transitions, currentState, suspiciousStates, acceptingStates, recentTransition]);

  return (
    <div className="card p-4">
      <h3 className="text-xs font-mono font-semibold text-warm-text mb-2 tracking-wide uppercase">{name}</h3>
      <div style={{ height: 400 }} className="rounded overflow-hidden border border-cream-border">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          fitView
          attributionPosition="bottom-left"
          proOptions={{ hideAttribution: true }}
        >
          <Background color="#E0D8CC" gap={20} />
          <Controls
            style={{ background: '#FFFFFF', border: '1px solid #E0D8CC', borderRadius: '4px' }}
          />
        </ReactFlow>
      </div>
    </div>
  );
}
