# Automata Theory in Digital Doppelgänger

## Why Automata Theory?

User interaction with a web application is naturally represented as a formal language:

| Concept | Mapping |
|---------|---------|
| Events | Alphabet (Σ) |
| Behavior sequence | String over Σ |
| Behavioral rules | Language (L) |
| User state | Automaton state (q ∈ Q) |
| Actions | State transitions (δ) |
| Valid behavior | Accepted by automaton (w ∈ L) |
| Suspicious behavior | Rejected/flagged by automaton |

## Formal Definition

```
DFA = (Q, Σ, δ, q₀, F)

Where for the Navigation Automaton:
  Q  = {START, LANDING, BROWSING, DEEP_BROWSING, NAVIGATING_BACK,
        NAVIGATING_FORWARD, SEARCHING, REPEATED_NAVIGATION,
        LINEAR_NAVIGATION, ERRATIC_NAVIGATION, SUSPICIOUS_NAVIGATION, END}

  Σ  = {START, PAGE_VIEW, MOVE, HOVER, CLICK, KEY, SCROLL, FOCUS,
        SUBMIT, IDLE, BACK, FORWARD, RETRY, SUCCESS, FAILURE,
        RAPID_ACTION, REPEATED_ACTION, END}

  q₀ = START

  F  = {END, LANDING, BROWSING, DEEP_BROWSING, NAVIGATING_BACK, SEARCHING}

  Suspicious States = {REPEATED_NAVIGATION, LINEAR_NAVIGATION,
                       ERRATIC_NAVIGATION, SUSPICIOUS_NAVIGATION}
```

## Multi-Layer Architecture

### Automaton 1: Navigation DFA
Tracks page transition patterns. Humans browse non-linearly with backtracking; bots follow predictable linear paths.

### Automaton 2: Interaction DFA
Tracks click/hover/keyboard/scroll diversity. Humans use varied interactions; bots use minimal types in mechanical patterns.

### Automaton 3: Timing DFA
Processes timing symbols derived from inter-event delays:
- VERY_FAST (< 50ms) → likely automated
- FAST (50-150ms) → possible automation
- NORMAL (150ms-2s) → typical human
- SLOW (2-10s) → reading/thinking
- VERY_SLOW (> 10s) → idle/away
- REGULAR → low variance (suspicious)
- IRREGULAR → high variance (human)

### Automaton 4: Consistency DFA
Processes meta-symbols derived from behavioral window analysis:
- CONSISTENT → matches reference patterns
- DIVERSE → high event type variety
- REPETITIVE → repeated sub-sequences
- LOW_ENTROPY → predictable stream
- HIGH_ENTROPY → natural variation

## Product Automaton

The product automaton computes the Cartesian product:

```
Product State = (q_nav, q_int, q_tim, q_con)

Example:
  Human:    (BROWSING, DIVERSE_INTERACTION, NORMAL_TIMING, CONSISTENT)
  Bot:      (REPEATED_NAVIGATION, MECHANICAL_INTERACTION, RAPID_SEQUENCE, LOW_ENTROPY)
```

The combined state determines the final behavioral classification:
- If any component is in a suspicious state → overall suspicion increases
- Multiple suspicious components compound → high automation score
- All components in accepting states → human-like classification

## Transition Examples

### Normal Human Sequence
```
δ(START, PAGE_VIEW) → LANDING
δ(LANDING, MOVE) → LANDING
δ(LANDING, CLICK) → BROWSING
δ(BROWSING, SCROLL) → BROWSING
δ(BROWSING, BACK) → NAVIGATING_BACK
δ(NAVIGATING_BACK, PAGE_VIEW) → BROWSING
δ(BROWSING, END) → END ✓ (accepted)
```

### Suspicious Bot Sequence
```
δ(START, PAGE_VIEW) → LANDING
δ(LANDING, PAGE_VIEW) → BROWSING
δ(BROWSING, PAGE_VIEW) → DEEP_BROWSING
δ(DEEP_BROWSING, PAGE_VIEW) → LINEAR_NAVIGATION ⚠
δ(LINEAR_NAVIGATION, PAGE_VIEW) → SUSPICIOUS_NAVIGATION ⚠⚠
```

## Counterexample Generation

When a sequence violates expected behavior, the system identifies the exact point of failure:

```
Expected: LOGIN_PAGE → FORM_FOCUS → KEY → SUBMIT
Observed: LOGIN_PAGE → SUBMIT

Violation at event #2:
  Input:    SUBMIT
  Expected: FORM_FOCUS / KEY
  State:    FORM_INPUT
  δ(FORM_INPUT, SUBMIT) → FORM_COMPLETING (skipped expected interaction)
```

## Runtime Verification

The system performs runtime verification by continuously monitoring the product automaton state during a session. Each event is processed in real time, and state transitions are recorded for post-session analysis and replay.
