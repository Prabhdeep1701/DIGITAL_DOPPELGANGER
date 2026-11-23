# Threat Model

## Scope

Digital Doppelgänger is a **research/educational platform** for behavioral analysis. It is not a production security system.

## What It Detects

The system analyzes behavioral signals to classify sessions on a spectrum from human-like to automated-like:

| Signal | Human | Bot |
|--------|-------|-----|
| Timing variance | High (irregular) | Low (regular) |
| Navigation diversity | High (non-linear) | Low (linear/repeated) |
| Interaction diversity | High (click, hover, scroll, key) | Low (mostly clicks) |
| Idle periods | Present | Absent |
| Sequence repetition | Low | High |
| Behavioral entropy | High | Low |

## Limitations

1. **Not deterministic** — The system provides behavioral scores, not definitive proof
2. **Synthetic testing only** — Experiment results use generated data, not real users
3. **Evasion possible** — A sufficiently sophisticated bot that mimics human behavioral patterns across all dimensions could potentially evade detection
4. **No network analysis** — The system only analyzes behavioral events, not network characteristics
5. **Single-session** — Each session is analyzed independently

## Privacy Considerations

- No passwords or credentials are collected
- No payment information is processed
- No personally identifiable information is stored
- All sessions use anonymous UUIDs
- Event data includes only: type, timestamp, page, target element
