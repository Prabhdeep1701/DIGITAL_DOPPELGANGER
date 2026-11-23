"""
Product Automaton — combines all four behavioral automata.

The product automaton computes the Cartesian product of the
individual automaton states to form a combined behavioral state:

    (Navigation State × Interaction State × Timing State × Consistency State)

This is the central analytical engine of the system. The combined state
determines the final behavioral classification.

Example combined states:
    (BROWSING, DIVERSE_INTERACTION, NORMAL_TIMING, CONSISTENT) → Human-like
    (REPEATED_NAVIGATION, MECHANICAL_INTERACTION, RAPID_SEQUENCE, LOW_ENTROPY) → Automated-like
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field

from app.automata.base import DFA, TransitionRecord, EVENT_TO_SYMBOL
from app.automata.navigation import create_navigation_automaton
from app.automata.interaction import create_interaction_automaton
from app.automata.timing import create_timing_automaton, classify_delay, classify_regularity
from app.automata.consistency import create_consistency_automaton, classify_consistency, WINDOW_SIZE


@dataclass
class ProductStateSnapshot:
    """A snapshot of all four automaton states at a point in time."""
    navigation: str
    interaction: str
    timing: str
    consistency: str
    timestamp: float
    input_symbol: str
    is_suspicious: bool
    detections: List[str] = field(default_factory=list)

    @property
    def tuple(self) -> Tuple[str, str, str, str]:
        return (self.navigation, self.interaction, self.timing, self.consistency)

    def __str__(self) -> str:
        return f"({self.navigation}, {self.interaction}, {self.timing}, {self.consistency})"


@dataclass
class ProcessingResult:
    """Result from processing a single event through the product automaton."""
    event_type: str
    symbol: str
    timestamp: float
    product_state: ProductStateSnapshot
    transitions: List[TransitionRecord]
    detections: List[str]


class ProductAutomaton:
    """
    Product automaton combining navigation, interaction, timing, and consistency DFAs.

    For each incoming event:
    1. Convert raw event to alphabet symbol
    2. Compute timing symbol from inter-event delay
    3. Compute consistency symbol from recent event window
    4. Feed appropriate symbols to each sub-automaton
    5. Combine states into product state
    6. Assess behavioral classification from product state
    """

    def __init__(self):
        self.navigation = create_navigation_automaton()
        self.interaction = create_interaction_automaton()
        self.timing = create_timing_automaton()
        self.consistency = create_consistency_automaton()

        self.last_timestamp: Optional[float] = None
        self.recent_delays: List[float] = []
        self.recent_symbols: List[str] = []
        self.history: List[ProductStateSnapshot] = []
        self.all_transitions: List[TransitionRecord] = []
        self.all_detections: List[str] = []

    def reset(self):
        """Reset all automata to initial states."""
        self.navigation.reset()
        self.interaction.reset()
        self.timing.reset()
        self.consistency.reset()
        self.last_timestamp = None
        self.recent_delays = []
        self.recent_symbols = []
        self.history = []
        self.all_transitions = []
        self.all_detections = []

    def process_event(self, event_type: str, timestamp: float,
                      page: Optional[str] = None, target: Optional[str] = None) -> ProcessingResult:
        """
        Process a single behavioral event through all four automata.

        Returns the combined product state and any detections.
        """
        # Step 1: Convert event to alphabet symbol
        symbol = EVENT_TO_SYMBOL.get(event_type, event_type.upper())
        self.recent_symbols.append(symbol)

        # Step 2: Process through navigation automaton
        nav_result = self.navigation.transition(symbol, timestamp)

        # Step 3: Process through interaction automaton
        int_result = self.interaction.transition(symbol, timestamp)

        # Step 4: Compute timing symbol and process through timing automaton
        timing_symbol = "NORMAL"
        if self.last_timestamp is not None:
            delay_ms = (timestamp - self.last_timestamp) * 1000
            timing_symbol = classify_delay(delay_ms)
            self.recent_delays.append(delay_ms)

            # Check regularity of recent delays
            regularity = classify_regularity(self.recent_delays)
            if regularity:
                # Feed regularity as a secondary signal
                self.timing.transition(regularity, timestamp)

        timing_result = self.timing.transition(timing_symbol, timestamp)
        self.last_timestamp = timestamp

        # Step 5: Compute consistency symbol and process
        consistency_symbol = classify_consistency(
            self.recent_symbols[-WINDOW_SIZE:]
        )
        cons_result = self.consistency.transition(consistency_symbol, timestamp)

        # Step 6: Build product state
        transitions = [nav_result, int_result, timing_result, cons_result]
        detections = [t.detection_reason for t in transitions if t.detection_reason]

        is_suspicious = any(t.is_suspicious for t in transitions)

        snapshot = ProductStateSnapshot(
            navigation=self.navigation.current_state,
            interaction=self.interaction.current_state,
            timing=self.timing.current_state,
            consistency=self.consistency.current_state,
            timestamp=timestamp,
            input_symbol=symbol,
            is_suspicious=is_suspicious,
            detections=detections,
        )

        self.history.append(snapshot)
        self.all_transitions.extend(transitions)
        self.all_detections.extend(detections)

        return ProcessingResult(
            event_type=event_type,
            symbol=symbol,
            timestamp=timestamp,
            product_state=snapshot,
            transitions=transitions,
            detections=detections,
        )

    def process_sequence(self, events: List[dict]) -> List[ProcessingResult]:
        """
        Process a sequence of events.
        Each event dict should have: event_type, timestamp, and optionally page, target.
        """
        self.reset()
        results = []
        for event in events:
            result = self.process_event(
                event_type=event["event_type"],
                timestamp=event["timestamp"],
                page=event.get("page"),
                target=event.get("target"),
            )
            results.append(result)
        return results

    def get_suspicious_count(self) -> Dict[str, int]:
        """Return suspicious state counts per automaton."""
        return {
            "navigation": self.navigation.suspicious_count,
            "interaction": self.interaction.suspicious_count,
            "timing": self.timing.suspicious_count,
            "consistency": self.consistency.suspicious_count,
            "total": (
                self.navigation.suspicious_count +
                self.interaction.suspicious_count +
                self.timing.suspicious_count +
                self.consistency.suspicious_count
            ),
        }

    def get_state_distribution(self) -> Dict[str, Dict[str, int]]:
        """Return how many times each state was visited per automaton."""
        distribution: Dict[str, Dict[str, int]] = {
            "navigation": {},
            "interaction": {},
            "timing": {},
            "consistency": {},
        }
        for snapshot in self.history:
            for key, state in [
                ("navigation", snapshot.navigation),
                ("interaction", snapshot.interaction),
                ("timing", snapshot.timing),
                ("consistency", snapshot.consistency),
            ]:
                distribution[key][state] = distribution[key].get(state, 0) + 1
        return distribution

    def get_current_product_state(self) -> Optional[ProductStateSnapshot]:
        """Get the current product state."""
        if not self.history:
            return None
        return self.history[-1]

    def get_definitions(self) -> List[dict]:
        """Get formal definitions of all sub-automata."""
        return [
            self.navigation.get_definition(),
            self.interaction.get_definition(),
            self.timing.get_definition(),
            self.consistency.get_definition(),
        ]
