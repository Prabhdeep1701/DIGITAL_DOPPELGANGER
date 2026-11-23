# Architecture

## System Overview

Digital Doppelgänger is a three-tier application:

```
┌─────────────────────────────────────────────────────────┐
│                     Frontend (Next.js)                   │
│  Landing │ Dashboard │ Playground │ Simulator │ Lab      │
└─────────────────────┬───────────────────────────────────┘
                      │ REST / WebSocket
┌─────────────────────▼───────────────────────────────────┐
│                     Backend (FastAPI)                     │
│                                                          │
│  ┌──────────┐  ┌───────────────┐  ┌─────────────────┐  │
│  │ Event    │  │ Automata      │  │ Detection       │  │
│  │ Processor│→│ Engine        │→│ & Scoring       │  │
│  └──────────┘  │               │  └─────────────────┘  │
│                │ ┌───────────┐ │                        │
│                │ │Navigation │ │                        │
│                │ │DFA        │ │                        │
│                │ ├───────────┤ │                        │
│                │ │Interaction│ │                        │
│                │ │DFA        │ │                        │
│                │ ├───────────┤ │                        │
│                │ │Timing     │ │                        │
│                │ │DFA        │ │                        │
│                │ ├───────────┤ │                        │
│                │ │Consistency│ │                        │
│                │ │DFA        │ │                        │
│                │ └───────────┘ │                        │
│                │       ↓       │                        │
│                │ ┌───────────┐ │                        │
│                │ │ Product   │ │                        │
│                │ │ Automaton │ │                        │
│                │ └───────────┘ │                        │
│                └───────────────┘                        │
└─────────────────────┬───────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────┐
│                   PostgreSQL                             │
│  users │ sessions │ events │ automaton_states │ detections│
└─────────────────────────────────────────────────────────┘
```

## Event Processing Pipeline

```
Raw User Event (click, move, key, etc.)
        ↓
Symbol Conversion (EVENT_TO_SYMBOL mapping)
        ↓
Navigation Automaton  → δ(state, symbol) → new state
Interaction Automaton → δ(state, symbol) → new state
Timing Automaton      → δ(state, timing_symbol) → new state
Consistency Automaton → δ(state, consistency_symbol) → new state
        ↓
Product State = (nav_state, int_state, tim_state, con_state)
        ↓
Behavioral Scorer (weighted 6-factor analysis)
        ↓
Classification: Human-like | Automated-like | Suspicious | Inconclusive
```

## Data Model

### Entity Relationships

```
User 1──N Session 1──N Event
                   1──N AutomatonState
                   1──N Detection
```

## Real-Time Architecture

WebSocket connections enable real-time event processing:

1. Client sends events via WebSocket to `/ws/events/{session_id}`
2. Backend processes through automata engine
3. Backend sends back state transitions in real time
4. Dashboard listeners at `/ws/dashboard` receive aggregated updates

## Scoring System

Six weighted factors (summing to 100%):

| Factor | Weight | Measures |
|--------|--------|----------|
| Timing Regularity | 20% | Coefficient of variation of inter-event delays |
| Navigation Diversity | 20% | Shannon entropy of navigation states |
| Interaction Diversity | 20% | Unique event types / total events |
| Repetition | 15% | N-gram repetition rate |
| Idle Behavior | 10% | Presence of natural pauses |
| Sequence Consistency | 15% | Automata consistency state visits |
