# Digital Doppelgänger — Project Summary

## What Is It?

Digital Doppelgänger is a behavioural intelligence platform that analyses user interaction sequences in web applications to determine whether observed behaviour is **human-like** or **automated/bot-like**. The core detection engine is built entirely on **Automata Theory** — using Deterministic Finite Automata (DFA), product automata, and formal language recognition — making every classification decision traceable and explainable.

---

## Problem Statement

Automated bots interacting with web applications pose significant security, analytics, and business risks. Traditional detection approaches rely either on network-level signals (IP reputation, rate limiting) or opaque machine-learning models. This project demonstrates a **transparent, formally grounded** alternative: using the mathematical framework of finite automata to model and classify behavioural patterns.

---

## Core Theory — How It Works

### Automata-Theoretic Approach

User interactions (clicks, scrolls, keystrokes, page views) are treated as a **formal language**:

| Automata Concept | Maps To |
|------------------|---------|
| Alphabet (Σ) | 18 event symbols (START, PAGE_VIEW, CLICK, KEY, SCROLL, HOVER, IDLE, etc.) |
| String over Σ | A user's interaction sequence during one session |
| Automaton states (Q) | Behavioural states (BROWSING, RAPID_INTERACTION, etc.) |
| Transition function (δ) | Rules mapping (current state + event) → next state |
| Accepting states (F) | Human-like behavioural endpoints |
| Suspicious states | Bot-like/anomalous behavioural states |

### The Four DFAs

The system employs **four specialised DFAs**, each analysing a different behavioural dimension:

1. **Navigation DFA (12 states)** — Tracks page browsing patterns. Humans browse non-linearly with backtracking; bots follow predictable linear paths. Flags: `LINEAR_NAVIGATION`, `REPEATED_NAVIGATION`, `SUSPICIOUS_NAVIGATION`.

2. **Interaction DFA (13 states)** — Tracks action type diversity. Humans use varied interactions (click + hover + scroll + keyboard); bots use minimal types. Flags: `CLICK_ONLY`, `RAPID_INTERACTION`, `MECHANICAL_INTERACTION`.

3. **Timing DFA** — Classifies inter-event delays into categories (VERY_FAST <50ms, FAST 50–150ms, NORMAL 150ms–2s, SLOW 2–10s, VERY_SLOW >10s) and measures regularity. Bots exhibit metronomic timing; humans have irregular delays. Flags: `MACHINE_TIMING`, `REGULAR_TIMING`.

4. **Consistency DFA** — Computes Shannon entropy and detects repetition patterns. Low entropy + high repetition = bot-like. Flags: `HIGH_REPETITION`, `LOW_ENTROPY`.

### Product Automaton

All four DFAs are combined via **Cartesian product construction**:

```
Product State = (Navigation State × Interaction State × Timing State × Consistency State)
```

Every event is processed by all 4 DFAs simultaneously. The composite state captures multi-dimensional behaviour — e.g., a session can have human-like navigation but suspicious timing.

### Behavioural Scoring

A weighted scorer analyses 6 factors to produce a 0–100 automation score:

| Factor | Weight | What It Measures |
|--------|--------|------------------|
| Timing Regularity | 20% | Coefficient of variation of inter-event delays |
| Navigation Diversity | 20% | Shannon entropy of navigation states visited |
| Interaction Diversity | 20% | Ratio of unique event types to total events |
| Repetition | 15% | N-gram repetition rate in event sequences |
| Idle Behaviour | 10% | Presence of natural pauses (humans pause; bots don't) |
| Sequence Consistency | 15% | Proportion of time spent in suspicious automata states |

**Final Classification:** Human-like | Suspicious | Automated-like | Inconclusive

---

## Architecture

```
Frontend (Next.js 14 / React / TypeScript / Tailwind CSS)
       ↓ REST API + WebSocket
Backend (FastAPI / Python / Async)
       ↓
  Event Processor → Symbol Conversion → 4 DFAs (Product Automaton) → Scorer → Classification
       ↓
PostgreSQL (sessions, events, automaton_states, detections)
```

### Data Model

- **Session** — One user visit (anonymous UUID, start/end time, classification, score)
- **Event** — One interaction (type, timestamp, page, target element)
- **AutomatonState** — State of each DFA at each event
- **Detection** — Flagged anomaly (severity, reason, automaton that triggered it)

### Real-Time Processing

- Events stream via **WebSocket** to `/ws/events/{session_id}`
- Backend processes each event through the automata engine instantly
- State transitions are sent back to the client in real time
- Dashboard listeners at `/ws/dashboard` receive aggregated live updates

---

## Platform Features (10 Pages)

### 1. Landing Page (`/`)
Editorial introduction to the platform. Explains the Somatic vs Synthetic Kinetics concept, the Three Laws of Behavioural Entropy, and shows extracted telemetry state maps.

### 2. Dashboard (`/dashboard`)
Real-time monitoring — live WebSocket event feed, session counts, classification distribution bars, recent sessions table, and system statistics (total events, detections, active DFAs).

### 3. Playground (`/playground`)
**DoppelShop** — a simulated e-commerce store. Every user interaction (click a product, hover a banner, fill a form, scroll, navigate, idle) generates real behavioural events processed live through the automata engine. Shows the product automaton state and final score in real time.

### 4. Simulator (`/simulator`)
Run pre-built bot profiles against the detection engine:
- **human_like** — Irregular timing, varied navigation, idle periods
- **scripted_bot** — Fixed sequence, regular timing, no variation
- **aggressive_bot** — Rapid-fire actions, minimal diversity
- **slow_bot** — Deliberately slow with randomised timing
- **mixed** — Starts human-like, transitions to automated mid-session

### 5. Session Explorer (`/sessions`)
Browse all recorded sessions. Filter by classification (Human-like / Automated / Suspicious / Inconclusive). Shows session ID, start time, type, classification badge, score, and event count.

### 6. Session Detail (`/sessions/[id]`)
Deep-dive into a single session:
- Event-by-event **replay** with playback controls (play/pause, speed 0.5x–5x)
- Full **scoring breakdown** with per-factor bars and explanations
- **Detection alerts** (severity-tagged reasons)
- Complete **event timeline** (filterable, with delays and automaton state annotations)

### 7. Compare (`/compare`)
Side-by-side comparison of two sessions — scores, event counts, detection counts, scoring breakdowns, and whether they received the same classification.

### 8. Automata Lab (`/automata`)
Explore formal DFA definitions:
- Full alphabet (Σ), state sets (Q), transition functions (δ), accepting and suspicious states
- **Visual graph** of each automaton (interactive node/edge diagram)
- **Sequence generator** — generate valid, suspicious, or random event sequences
- **Custom sequence tester** — input your own event sequence and see the product automaton trace
- **Counterexample finder** — identifies the exact event where a sequence violates expected behaviour

### 9. Attack Lab (`/attack-lab`)
Six adversarial tests that challenge the detection engine:
1. Pure deterministic bot
2. Randomised bot
3. Slow bot (proves "fast = bot" is insufficient)
4. Human-like scripted bot
5. Human control session
6. Mixed-behaviour session

Shows per-test scores, scoring breakdowns, and a comparison summary table.

### 10. Analytics (`/analytics`)
Batch experiment framework:
- Configure: N human sessions + N bot sessions + N adversarial sessions
- Run all sessions through the full automata pipeline
- Get: **Accuracy, Precision, Recall, F1 Score**, False Positive/Negative rates
- **Confusion matrix** (TP, TN, FP, FN)
- **Per-profile breakdown** (average/min/max scores, classification distribution)

---

## Technology Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 14, React 18, TypeScript, Tailwind CSS, ReactFlow, Recharts |
| Backend | Python, FastAPI, SQLAlchemy (async), Pydantic |
| Database | PostgreSQL 16 |
| Real-time | WebSockets (FastAPI native) |
| Testing | pytest (53 tests across 10 test classes) |
| Deployment | Docker Compose (3 containers: frontend, backend, postgres) |

---

## Key Files

| File | Purpose |
|------|---------|
| `backend/app/automata/base.py` | DFA base class, alphabet, symbol mapping |
| `backend/app/automata/navigation.py` | Navigation DFA (12 states) |
| `backend/app/automata/interaction.py` | Interaction DFA (13 states) |
| `backend/app/automata/timing.py` | Timing DFA with delay classification |
| `backend/app/automata/consistency.py` | Consistency DFA with entropy/repetition |
| `backend/app/automata/product_automaton.py` | Product automaton combining all 4 DFAs |
| `backend/app/detection/scorer.py` | 6-factor weighted behavioural scorer |
| `backend/app/simulation/profiles.py` | 5 bot simulation profiles |
| `backend/app/services/event_processor.py` | Central event processing pipeline |
| `backend/tests/test_automata.py` | 53 automated tests |

---

## Running the Project

### Docker (Recommended)
```bash
docker compose up --build
```
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Local Development
```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend
npm install
npm run dev
```

---

## Why This Approach Matters

1. **Transparency** — Unlike neural network black boxes, every DFA transition is traceable. You can replay the exact state path and see why a session was classified as automated.

2. **Formal foundation** — Built on well-understood mathematical theory (DFA, product automata, formal languages) rather than heuristic rules or opaque ML models.

3. **Multi-dimensional** — Combining 4 DFAs via product construction captures the interaction between navigation, action types, timing, and consistency — simple "fast = bot" rules fail where this succeeds.

4. **Explainability** — Every score component is visible, weighted, and explained in human-readable terms.

---

## Disclaimer

This system uses automata-based heuristics to assess behavioural patterns. It does **not** claim to definitively identify bots. Results are labelled as "Human-like", "Automated-like", "Suspicious", or "Inconclusive". Experiment results apply to synthetic test datasets only and do not establish real-world detection accuracy. This is a research/educational platform, not a production security system.
