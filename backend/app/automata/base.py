"""
Base Finite Automaton implementation.

This module provides the DFA (Deterministic Finite Automaton) base class
that all behavioral automata extend. The automaton processes event symbols
from the behavioral alphabet and tracks state transitions.

Formally:
    DFA = (Q, Σ, δ, q0, F)
    Q  = finite set of states
    Σ  = input alphabet (event symbols)
    δ  = transition function Q × Σ → Q
    q0 = start state
    F  = set of accepting states
"""

from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field


# The behavioral event alphabet
ALPHABET = [
    "START", "PAGE_VIEW", "MOVE", "HOVER", "CLICK", "KEY", "SCROLL",
    "FOCUS", "SUBMIT", "IDLE", "BACK", "FORWARD", "RETRY", "SUCCESS",
    "FAILURE", "RAPID_ACTION", "REPEATED_ACTION", "END"
]

# Map raw event types to alphabet symbols
EVENT_TO_SYMBOL = {
    "session_start": "START",
    "page_view": "PAGE_VIEW",
    "mouse_move": "MOVE",
    "hover": "HOVER",
    "mouse_click": "CLICK",
    "click": "CLICK",
    "key_press": "KEY",
    "scroll": "SCROLL",
    "form_focus": "FOCUS",
    "form_submit": "SUBMIT",
    "idle": "IDLE",
    "back_navigation": "BACK",
    "forward_navigation": "FORWARD",
    "retry": "RETRY",
    "successful_action": "SUCCESS",
    "failed_action": "FAILURE",
    "rapid_action": "RAPID_ACTION",
    "repeated_action": "REPEATED_ACTION",
    "session_end": "END",
}


@dataclass
class TransitionRecord:
    """Records a single state transition for auditing."""
    automaton_type: str
    from_state: str
    input_symbol: str
    to_state: str
    timestamp: float
    is_suspicious: bool = False
    detection_reason: Optional[str] = None


@dataclass
class DFA:
    """
    Deterministic Finite Automaton for behavioral analysis.

    Each behavioral automaton inherits from this and defines its own
    states, transitions, accepting states, and suspicious states.
    """
    name: str
    states: Set[str]
    alphabet: Set[str]
    transitions: Dict[str, Dict[str, str]]  # state -> {symbol -> next_state}
    start_state: str
    accepting_states: Set[str]
    suspicious_states: Set[str] = field(default_factory=set)

    # Runtime state
    current_state: str = ""
    history: List[TransitionRecord] = field(default_factory=list)
    suspicious_count: int = 0

    def __post_init__(self):
        self.current_state = self.start_state

    def reset(self):
        """Reset automaton to initial state."""
        self.current_state = self.start_state
        self.history = []
        self.suspicious_count = 0

    def transition(self, symbol: str, timestamp: float = 0.0) -> TransitionRecord:
        """
        Process an input symbol and transition to the next state.

        δ(current_state, symbol) → next_state

        If no transition is defined for (current_state, symbol),
        the automaton stays in current_state and flags it.
        """
        prev_state = self.current_state
        state_transitions = self.transitions.get(self.current_state, {})

        if symbol in state_transitions:
            self.current_state = state_transitions[symbol]
        elif "*" in state_transitions:
            # Wildcard transition — catches unmatched symbols
            self.current_state = state_transitions["*"]
        # else: stay in current state (undefined transition)

        is_suspicious = self.current_state in self.suspicious_states
        detection_reason = None

        if is_suspicious:
            self.suspicious_count += 1
            detection_reason = (
                f"Automaton '{self.name}' entered suspicious state "
                f"'{self.current_state}' via δ({prev_state}, {symbol})"
            )

        record = TransitionRecord(
            automaton_type=self.name,
            from_state=prev_state,
            input_symbol=symbol,
            to_state=self.current_state,
            timestamp=timestamp,
            is_suspicious=is_suspicious,
            detection_reason=detection_reason,
        )
        self.history.append(record)
        return record

    def is_in_accepting_state(self) -> bool:
        """Check if the automaton is currently in an accepting state."""
        return self.current_state in self.accepting_states

    def is_in_suspicious_state(self) -> bool:
        """Check if the automaton is currently in a suspicious state."""
        return self.current_state in self.suspicious_states

    def get_definition(self) -> dict:
        """Return the formal definition of this automaton."""
        return {
            "name": self.name,
            "alphabet": sorted(self.alphabet),
            "states": sorted(self.states),
            "start_state": self.start_state,
            "accepting_states": sorted(self.accepting_states),
            "suspicious_states": sorted(self.suspicious_states),
            "transitions": {
                state: dict(sorted(trans.items()))
                for state, trans in sorted(self.transitions.items())
            },
        }

    def process_sequence(self, symbols: List[str], timestamps: Optional[List[float]] = None) -> List[TransitionRecord]:
        """Process a sequence of symbols and return all transition records."""
        self.reset()
        results = []
        for i, symbol in enumerate(symbols):
            ts = timestamps[i] if timestamps else float(i)
            results.append(self.transition(symbol, ts))
        return results

    def generate_valid_sequence(self, length: int = 10) -> List[str]:
        """Generate a sequence that leads to an accepting state."""
        import random
        sequence = []
        state = self.start_state
        for _ in range(length):
            trans = self.transitions.get(state, {})
            if not trans:
                break
            # Prefer non-suspicious transitions
            safe_symbols = [
                s for s, next_s in trans.items()
                if s != "*" and next_s not in self.suspicious_states
            ]
            if not safe_symbols:
                safe_symbols = [s for s in trans if s != "*"]
            if not safe_symbols:
                break
            symbol = random.choice(safe_symbols)
            sequence.append(symbol)
            state = trans[symbol]
        return sequence

    def generate_suspicious_sequence(self, length: int = 10) -> List[str]:
        """Generate a sequence that enters suspicious states."""
        import random
        sequence = []
        state = self.start_state
        for _ in range(length):
            trans = self.transitions.get(state, {})
            if not trans:
                break
            # Prefer transitions leading to suspicious states
            sus_symbols = [
                s for s, next_s in trans.items()
                if s != "*" and next_s in self.suspicious_states
            ]
            if sus_symbols:
                symbol = random.choice(sus_symbols)
            else:
                symbols = [s for s in trans if s != "*"]
                if not symbols:
                    break
                symbol = random.choice(symbols)
            sequence.append(symbol)
            state = trans[symbol]
        return sequence
