"""
Timing Automaton — tracks inter-event timing patterns.

This automaton doesn't process the event alphabet directly.
Instead, it converts inter-event delays into timing symbols:

    VERY_FAST:   < 50ms   (likely automated)
    FAST:        50-150ms (possible automation)
    NORMAL:      150ms-2s (typical human)
    SLOW:        2-10s    (reading/thinking)
    VERY_SLOW:   > 10s    (idle/away)
    REGULAR:     variance of recent intervals < threshold
    IRREGULAR:   variance of recent intervals > threshold

Monitors:
- Inter-event timing
- Timing regularity (low variance = suspicious)
- Rapid action sequences
- Identical timing intervals
"""

from typing import List, Optional
from app.automata.base import DFA

STATES = {
    "START",
    "NORMAL_TIMING",
    "FAST_TIMING",
    "SLOW_TIMING",
    "RAPID_SEQUENCE",
    "REGULAR_TIMING",
    "IRREGULAR_TIMING",
    "SUSPICIOUS_TIMING",
    "HUMAN_TIMING",
    "END",
}

ACCEPTING = {"END", "NORMAL_TIMING", "SLOW_TIMING", "IRREGULAR_TIMING", "HUMAN_TIMING"}
SUSPICIOUS = {"RAPID_SEQUENCE", "REGULAR_TIMING", "SUSPICIOUS_TIMING"}

# Timing thresholds in milliseconds
VERY_FAST_MS = 50
FAST_MS = 150
NORMAL_MS = 2000
SLOW_MS = 10000
REGULARITY_WINDOW = 5
REGULARITY_THRESHOLD_MS = 30  # std dev below this = suspiciously regular


def classify_delay(delay_ms: float) -> str:
    """Convert a delay in milliseconds to a timing symbol."""
    if delay_ms < VERY_FAST_MS:
        return "VERY_FAST"
    elif delay_ms < FAST_MS:
        return "FAST"
    elif delay_ms < NORMAL_MS:
        return "NORMAL"
    elif delay_ms < SLOW_MS:
        return "SLOW"
    else:
        return "VERY_SLOW"


def classify_regularity(recent_delays: List[float]) -> Optional[str]:
    """Check if recent delays are suspiciously regular."""
    if len(recent_delays) < REGULARITY_WINDOW:
        return None
    window = recent_delays[-REGULARITY_WINDOW:]
    import numpy as np
    std = float(np.std(window))
    if std < REGULARITY_THRESHOLD_MS:
        return "REGULAR"
    return "IRREGULAR"


def create_timing_automaton() -> DFA:
    """
    Build the timing DFA.

    Humans have irregular, varied timing. Bots tend to have
    suspiciously regular intervals or impossibly fast actions.
    """
    transitions = {
        "START": {
            "NORMAL": "NORMAL_TIMING",
            "FAST": "FAST_TIMING",
            "VERY_FAST": "RAPID_SEQUENCE",
            "SLOW": "SLOW_TIMING",
            "VERY_SLOW": "SLOW_TIMING",
            "REGULAR": "REGULAR_TIMING",
            "IRREGULAR": "IRREGULAR_TIMING",
            "*": "NORMAL_TIMING",
        },
        "NORMAL_TIMING": {
            "NORMAL": "NORMAL_TIMING",
            "FAST": "FAST_TIMING",
            "VERY_FAST": "RAPID_SEQUENCE",
            "SLOW": "SLOW_TIMING",
            "VERY_SLOW": "SLOW_TIMING",
            "REGULAR": "REGULAR_TIMING",
            "IRREGULAR": "HUMAN_TIMING",
            "END": "END",
            "*": "NORMAL_TIMING",
        },
        "FAST_TIMING": {
            "NORMAL": "NORMAL_TIMING",
            "FAST": "RAPID_SEQUENCE",  # Two fast events in a row
            "VERY_FAST": "RAPID_SEQUENCE",
            "SLOW": "HUMAN_TIMING",   # Fast then slow = human variation
            "VERY_SLOW": "SLOW_TIMING",
            "REGULAR": "REGULAR_TIMING",
            "IRREGULAR": "NORMAL_TIMING",
            "END": "END",
            "*": "FAST_TIMING",
        },
        "SLOW_TIMING": {
            "NORMAL": "HUMAN_TIMING",
            "FAST": "NORMAL_TIMING",
            "VERY_FAST": "FAST_TIMING",
            "SLOW": "SLOW_TIMING",
            "VERY_SLOW": "SLOW_TIMING",
            "REGULAR": "REGULAR_TIMING",
            "IRREGULAR": "HUMAN_TIMING",
            "END": "END",
            "*": "SLOW_TIMING",
        },
        "RAPID_SEQUENCE": {
            "VERY_FAST": "SUSPICIOUS_TIMING",  # 3+ rapid events = very suspicious
            "FAST": "SUSPICIOUS_TIMING",
            "NORMAL": "NORMAL_TIMING",
            "SLOW": "HUMAN_TIMING",
            "VERY_SLOW": "SLOW_TIMING",
            "REGULAR": "SUSPICIOUS_TIMING",
            "IRREGULAR": "NORMAL_TIMING",
            "END": "END",
            "*": "RAPID_SEQUENCE",
        },
        "REGULAR_TIMING": {
            "REGULAR": "SUSPICIOUS_TIMING",  # Persistent regularity is suspicious
            "IRREGULAR": "NORMAL_TIMING",
            "NORMAL": "NORMAL_TIMING",
            "FAST": "FAST_TIMING",
            "VERY_FAST": "RAPID_SEQUENCE",
            "SLOW": "SLOW_TIMING",
            "END": "END",
            "*": "REGULAR_TIMING",
        },
        "IRREGULAR_TIMING": {
            "IRREGULAR": "HUMAN_TIMING",  # Persistent irregularity = human
            "REGULAR": "NORMAL_TIMING",
            "NORMAL": "NORMAL_TIMING",
            "FAST": "FAST_TIMING",
            "VERY_FAST": "RAPID_SEQUENCE",
            "SLOW": "SLOW_TIMING",
            "END": "END",
            "*": "IRREGULAR_TIMING",
        },
        "SUSPICIOUS_TIMING": {
            "SLOW": "NORMAL_TIMING",      # Slow event de-escalates
            "VERY_SLOW": "SLOW_TIMING",
            "NORMAL": "NORMAL_TIMING",
            "IRREGULAR": "NORMAL_TIMING",
            "VERY_FAST": "SUSPICIOUS_TIMING",
            "FAST": "SUSPICIOUS_TIMING",
            "REGULAR": "SUSPICIOUS_TIMING",
            "END": "END",
            "*": "SUSPICIOUS_TIMING",
        },
        "HUMAN_TIMING": {
            "NORMAL": "NORMAL_TIMING",
            "FAST": "FAST_TIMING",
            "VERY_FAST": "RAPID_SEQUENCE",
            "SLOW": "SLOW_TIMING",
            "VERY_SLOW": "SLOW_TIMING",
            "REGULAR": "REGULAR_TIMING",
            "IRREGULAR": "HUMAN_TIMING",
            "END": "END",
            "*": "HUMAN_TIMING",
        },
        "END": {
            "*": "END",
        },
    }

    return DFA(
        name="timing",
        states=STATES,
        alphabet={"VERY_FAST", "FAST", "NORMAL", "SLOW", "VERY_SLOW", "REGULAR", "IRREGULAR", "END"},
        transitions=transitions,
        start_state="START",
        accepting_states=ACCEPTING,
        suspicious_states=SUSPICIOUS,
    )
