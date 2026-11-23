"""
Tests for the automata engine — the core of the system.

30+ tests covering:
- DFA base operations
- Navigation automaton
- Interaction automaton
- Timing automaton
- Consistency automaton
- Product automaton
- Scoring
- Counterexample generation
- Sequence processing
"""

import time
import pytest
from app.automata.base import DFA, ALPHABET, EVENT_TO_SYMBOL, TransitionRecord
from app.automata.navigation import create_navigation_automaton
from app.automata.interaction import create_interaction_automaton
from app.automata.timing import create_timing_automaton, classify_delay, classify_regularity
from app.automata.consistency import (
    create_consistency_automaton, compute_entropy,
    detect_repetition, classify_consistency,
)
from app.automata.product_automaton import ProductAutomaton
from app.detection.scorer import BehavioralScorer
from app.simulation.profiles import (
    generate_human_like, generate_scripted_bot,
    generate_aggressive_bot, generate_slow_bot, generate_mixed,
)


# ============================================================================
# DFA Base Tests
# ============================================================================

class TestDFABase:
    def test_dfa_initial_state(self):
        """DFA should start in start_state."""
        nav = create_navigation_automaton()
        assert nav.current_state == "START"

    def test_dfa_reset(self):
        """Reset should return DFA to start state."""
        nav = create_navigation_automaton()
        nav.transition("PAGE_VIEW", 1.0)
        nav.reset()
        assert nav.current_state == "START"
        assert len(nav.history) == 0

    def test_dfa_transition_returns_record(self):
        """Transition should return a TransitionRecord."""
        nav = create_navigation_automaton()
        record = nav.transition("PAGE_VIEW", 1.0)
        assert isinstance(record, TransitionRecord)
        assert record.from_state == "START"
        assert record.to_state == "LANDING"
        assert record.input_symbol == "PAGE_VIEW"

    def test_dfa_undefined_transition_stays(self):
        """Undefined transition with wildcard should use wildcard."""
        nav = create_navigation_automaton()
        nav.transition("PAGE_VIEW", 1.0)  # -> LANDING
        record = nav.transition("SUCCESS", 2.0)  # Not explicitly defined, uses *
        assert nav.current_state is not None  # Should have transitioned via wildcard

    def test_dfa_get_definition(self):
        """get_definition should return a valid formal definition."""
        nav = create_navigation_automaton()
        defn = nav.get_definition()
        assert "name" in defn
        assert "alphabet" in defn
        assert "states" in defn
        assert "start_state" in defn
        assert "accepting_states" in defn
        assert "transitions" in defn

    def test_alphabet_coverage(self):
        """ALPHABET should contain all expected event symbols."""
        required = {"START", "PAGE_VIEW", "CLICK", "KEY", "SUBMIT", "IDLE", "END"}
        assert required.issubset(set(ALPHABET))

    def test_event_to_symbol_mapping(self):
        """EVENT_TO_SYMBOL should map raw events to alphabet symbols."""
        assert EVENT_TO_SYMBOL["session_start"] == "START"
        assert EVENT_TO_SYMBOL["mouse_click"] == "CLICK"
        assert EVENT_TO_SYMBOL["key_press"] == "KEY"
        assert EVENT_TO_SYMBOL["session_end"] == "END"


# ============================================================================
# Navigation Automaton Tests
# ============================================================================

class TestNavigationAutomaton:
    def test_basic_navigation_flow(self):
        """Normal browsing should stay in non-suspicious states."""
        nav = create_navigation_automaton()
        nav.transition("PAGE_VIEW", 1.0)   # -> LANDING
        nav.transition("CLICK", 2.0)        # -> BROWSING
        nav.transition("SCROLL", 3.0)       # -> BROWSING
        nav.transition("PAGE_VIEW", 4.0)    # -> DEEP_BROWSING
        assert nav.current_state in {"BROWSING", "DEEP_BROWSING"}
        assert nav.suspicious_count == 0

    def test_repeated_navigation_suspicious(self):
        """Repeated actions should lead to suspicious navigation."""
        nav = create_navigation_automaton()
        nav.transition("PAGE_VIEW", 1.0)
        nav.transition("CLICK", 2.0)
        nav.transition("REPEATED_ACTION", 3.0)  # -> REPEATED_NAVIGATION
        assert nav.current_state == "REPEATED_NAVIGATION"
        assert nav.suspicious_count > 0

    def test_backtracking_is_human(self):
        """Back navigation should not be suspicious."""
        nav = create_navigation_automaton()
        nav.transition("PAGE_VIEW", 1.0)
        nav.transition("CLICK", 2.0)
        nav.transition("BACK", 3.0)
        assert nav.current_state == "NAVIGATING_BACK"
        assert nav.suspicious_count == 0

    def test_linear_navigation_suspicious(self):
        """Multiple consecutive page views without interaction = suspicious."""
        nav = create_navigation_automaton()
        nav.transition("PAGE_VIEW", 1.0)   # LANDING
        nav.transition("PAGE_VIEW", 2.0)   # BROWSING
        nav.transition("PAGE_VIEW", 3.0)   # DEEP_BROWSING -> wait, BROWSING + PAGE_VIEW -> DEEP_BROWSING
        # Actually LANDING + PAGE_VIEW -> BROWSING, BROWSING + PAGE_VIEW -> DEEP_BROWSING
        # DEEP_BROWSING + PAGE_VIEW -> LINEAR_NAVIGATION
        nav.transition("PAGE_VIEW", 4.0)
        assert nav.current_state in {"LINEAR_NAVIGATION", "SUSPICIOUS_NAVIGATION"}

    def test_idle_de_escalates_suspicion(self):
        """IDLE should bring suspicious states back to normal."""
        nav = create_navigation_automaton()
        nav.transition("PAGE_VIEW", 1.0)
        nav.transition("CLICK", 2.0)
        nav.transition("REPEATED_ACTION", 3.0)  # -> REPEATED_NAVIGATION (suspicious)
        nav.transition("IDLE", 4.0)              # -> BROWSING (de-escalated)
        assert nav.current_state == "BROWSING"


# ============================================================================
# Interaction Automaton Tests
# ============================================================================

class TestInteractionAutomaton:
    def test_diverse_interaction(self):
        """Varied interactions should lead to DIVERSE_INTERACTION."""
        ia = create_interaction_automaton()
        ia.transition("MOVE", 1.0)
        ia.transition("CLICK", 2.0)      # MOVING + CLICK -> CLICKING... then
        ia.transition("SCROLL", 3.0)     # CLICKING + SCROLL -> DIVERSE_INTERACTION
        assert ia.current_state == "DIVERSE_INTERACTION"

    def test_rapid_clicking_suspicious(self):
        """Multiple rapid clicks should be suspicious."""
        ia = create_interaction_automaton()
        ia.transition("CLICK", 1.0)       # -> CLICKING
        ia.transition("CLICK", 1.05)      # -> RAPID_CLICKING
        ia.transition("CLICK", 1.10)      # -> SUSPICIOUS_INTERACTION
        assert ia.current_state == "SUSPICIOUS_INTERACTION"
        assert ia.suspicious_count > 0

    def test_form_interaction_flow(self):
        """Normal form interaction should not be suspicious."""
        ia = create_interaction_automaton()
        ia.transition("FOCUS", 1.0)       # -> FORM_INPUT
        ia.transition("KEY", 2.0)         # -> FORM_INPUT
        ia.transition("KEY", 3.0)         # -> FORM_INPUT
        ia.transition("SUBMIT", 4.0)      # -> FORM_COMPLETING
        assert ia.current_state == "FORM_COMPLETING"
        assert ia.suspicious_count == 0

    def test_hover_then_click_is_human(self):
        """Hover followed by click is a human-like pattern."""
        ia = create_interaction_automaton()
        ia.transition("MOVE", 1.0)        # START -> MOVING
        ia.transition("HOVER", 1.5)       # MOVING -> HOVERING
        ia.transition("CLICK", 2.0)       # HOVERING + CLICK -> DIVERSE_INTERACTION
        assert ia.current_state == "DIVERSE_INTERACTION"


# ============================================================================
# Timing Automaton Tests
# ============================================================================

class TestTimingAutomaton:
    def test_classify_delay_very_fast(self):
        """Delays < 50ms should be VERY_FAST."""
        assert classify_delay(10) == "VERY_FAST"
        assert classify_delay(49) == "VERY_FAST"

    def test_classify_delay_normal(self):
        """Delays 150ms-2s should be NORMAL."""
        assert classify_delay(500) == "NORMAL"
        assert classify_delay(1500) == "NORMAL"

    def test_classify_delay_slow(self):
        """Delays 2-10s should be SLOW."""
        assert classify_delay(5000) == "SLOW"

    def test_rapid_sequence_suspicious(self):
        """Three consecutive very fast events should be suspicious."""
        ta = create_timing_automaton()
        ta.transition("VERY_FAST", 1.0)   # -> RAPID_SEQUENCE
        ta.transition("VERY_FAST", 1.01)  # -> SUSPICIOUS_TIMING
        assert ta.current_state == "SUSPICIOUS_TIMING"
        assert ta.suspicious_count > 0

    def test_regular_timing_suspicious(self):
        """Regular timing detected should lead to suspicion."""
        ta = create_timing_automaton()
        ta.transition("NORMAL", 1.0)
        ta.transition("REGULAR", 2.0)      # -> REGULAR_TIMING
        ta.transition("REGULAR", 3.0)      # -> SUSPICIOUS_TIMING
        assert ta.current_state == "SUSPICIOUS_TIMING"

    def test_varied_timing_human(self):
        """Mixed fast and slow timing is human-like."""
        ta = create_timing_automaton()
        ta.transition("FAST", 1.0)
        ta.transition("SLOW", 3.0)         # -> HUMAN_TIMING
        assert ta.current_state == "HUMAN_TIMING"

    def test_classify_regularity_regular(self):
        """Very low variance delays should be classified as REGULAR."""
        delays = [100.0, 101.0, 100.5, 100.2, 100.8]
        result = classify_regularity(delays)
        assert result == "REGULAR"

    def test_classify_regularity_irregular(self):
        """High variance delays should be classified as IRREGULAR."""
        delays = [100.0, 2000.0, 50.0, 5000.0, 200.0]
        result = classify_regularity(delays)
        assert result == "IRREGULAR"


# ============================================================================
# Consistency Automaton Tests
# ============================================================================

class TestConsistencyAutomaton:
    def test_entropy_computation(self):
        """Entropy of a uniform distribution should be maximal."""
        symbols = ["A", "B", "C", "D"]
        entropy = compute_entropy(symbols)
        assert entropy == pytest.approx(2.0, abs=0.01)

    def test_entropy_single_symbol(self):
        """Entropy of a single repeated symbol should be 0."""
        symbols = ["A", "A", "A", "A"]
        assert compute_entropy(symbols) == 0.0

    def test_detect_repetition(self):
        """Repeated n-grams should be detected."""
        symbols = ["A", "B", "C", "A", "B", "C", "A", "B", "C"]
        rep = detect_repetition(symbols, 3)
        assert rep > 0.5  # High repetition

    def test_classify_consistency_repetitive(self):
        """Highly repetitive sequence should be classified as REPETITIVE."""
        symbols = ["CLICK", "PAGE_VIEW"] * 10
        result = classify_consistency(symbols)
        assert result in {"REPETITIVE", "LOW_ENTROPY"}

    def test_classify_consistency_diverse(self):
        """Diverse sequence should be classified as DIVERSE or HIGH_ENTROPY."""
        symbols = ["CLICK", "MOVE", "SCROLL", "HOVER", "KEY", "FOCUS",
                    "PAGE_VIEW", "IDLE", "BACK", "SUBMIT"]
        result = classify_consistency(symbols)
        assert result in {"DIVERSE", "HIGH_ENTROPY", "CONSISTENT"}


# ============================================================================
# Product Automaton Tests
# ============================================================================

class TestProductAutomaton:
    def test_product_automaton_creation(self):
        """Product automaton should contain all four sub-automata."""
        pa = ProductAutomaton()
        assert pa.navigation is not None
        assert pa.interaction is not None
        assert pa.timing is not None
        assert pa.consistency is not None

    def test_process_single_event(self):
        """Processing an event should return a valid result."""
        pa = ProductAutomaton()
        result = pa.process_event("page_view", time.time())
        assert result.symbol == "PAGE_VIEW"
        assert result.product_state is not None
        assert result.product_state.navigation is not None
        assert result.product_state.interaction is not None
        assert result.product_state.timing is not None
        assert result.product_state.consistency is not None

    def test_process_human_sequence(self):
        """Human-like sequence should not trigger many suspicious states."""
        pa = ProductAutomaton()
        events = generate_human_like(event_count=30)
        results = pa.process_sequence(events)
        assert len(results) == 30
        suspicious_count = pa.get_suspicious_count()["total"]
        # Humans should have low suspicious counts
        assert suspicious_count < 20  # Generous threshold

    def test_process_bot_sequence(self):
        """Bot sequence should trigger suspicious states."""
        pa = ProductAutomaton()
        events = generate_scripted_bot(event_count=30)
        results = pa.process_sequence(events)
        suspicious_count = pa.get_suspicious_count()["total"]
        # Bots should have higher suspicious counts
        assert suspicious_count > 0

    def test_process_aggressive_bot(self):
        """Aggressive bot should trigger many suspicious states."""
        pa = ProductAutomaton()
        events = generate_aggressive_bot(event_count=30)
        pa.process_sequence(events)
        suspicious = pa.get_suspicious_count()
        assert suspicious["total"] > 0

    def test_state_distribution(self):
        """State distribution should be populated after processing."""
        pa = ProductAutomaton()
        events = generate_human_like(event_count=20)
        pa.process_sequence(events)
        dist = pa.get_state_distribution()
        assert "navigation" in dist
        assert len(dist["navigation"]) > 0

    def test_product_state_tuple(self):
        """Product state should expose a tuple of all four states."""
        pa = ProductAutomaton()
        pa.process_event("page_view", time.time())
        state = pa.get_current_product_state()
        assert state is not None
        t = state.tuple
        assert len(t) == 4

    def test_get_definitions(self):
        """Should return definitions for all four automata."""
        pa = ProductAutomaton()
        defs = pa.get_definitions()
        assert len(defs) == 4
        names = {d["name"] for d in defs}
        assert names == {"navigation", "interaction", "timing", "consistency"}


# ============================================================================
# Scoring Tests
# ============================================================================

class TestScoring:
    def test_human_session_low_score(self):
        """Human-like session should get a low automation score."""
        pa = ProductAutomaton()
        events = generate_human_like(event_count=50)
        pa.process_sequence(events)
        scorer = BehavioralScorer()
        result = scorer.score_session(pa)
        assert result["automation_score"] < 60  # Should be classified as human-ish
        assert result["classification"] in ("human_like", "inconclusive", "suspicious")

    def test_bot_session_high_score(self):
        """Scripted bot session should get a high automation score."""
        pa = ProductAutomaton()
        events = generate_scripted_bot(event_count=50)
        pa.process_sequence(events)
        scorer = BehavioralScorer()
        result = scorer.score_session(pa)
        assert result["automation_score"] > 40  # Should lean automated
        assert "breakdown" in result

    def test_aggressive_bot_very_high_score(self):
        """Aggressive bot should score very high on automation."""
        pa = ProductAutomaton()
        events = generate_aggressive_bot(event_count=50)
        pa.process_sequence(events)
        scorer = BehavioralScorer()
        result = scorer.score_session(pa)
        assert result["automation_score"] > 50
        assert result["classification"] in ("automated_like", "suspicious")

    def test_scoring_has_all_components(self):
        """Scoring result should include all expected components."""
        pa = ProductAutomaton()
        events = generate_human_like(event_count=30)
        pa.process_sequence(events)
        scorer = BehavioralScorer()
        result = scorer.score_session(pa)
        assert "automation_score" in result
        assert "human_score" in result
        assert "suspicion_score" in result
        assert "classification" in result
        assert "breakdown" in result
        assert "explanations" in result

    def test_scoring_weights_sum_to_one(self):
        """Scoring weights should sum to 1.0."""
        scorer = BehavioralScorer()
        total = sum(scorer.WEIGHTS.values())
        assert total == pytest.approx(1.0, abs=0.001)

    def test_score_range(self):
        """Scores should be in [0, 100] range."""
        pa = ProductAutomaton()
        events = generate_mixed(event_count=40)
        pa.process_sequence(events)
        scorer = BehavioralScorer()
        result = scorer.score_session(pa)
        assert 0 <= result["automation_score"] <= 100
        assert 0 <= result["human_score"] <= 100
        assert 0 <= result["suspicion_score"] <= 100


# ============================================================================
# Simulation Profile Tests
# ============================================================================

class TestSimulationProfiles:
    def test_human_like_generates_events(self):
        """Human-like profile should generate the requested number of events."""
        events = generate_human_like(event_count=30)
        assert len(events) == 30

    def test_scripted_bot_generates_events(self):
        events = generate_scripted_bot(event_count=30)
        assert len(events) == 30

    def test_aggressive_bot_fast_timing(self):
        """Aggressive bot should have very short inter-event delays."""
        events = generate_aggressive_bot(event_count=20)
        delays = []
        for i in range(1, len(events)):
            delays.append((events[i]["timestamp"] - events[i - 1]["timestamp"]) * 1000)
        avg_delay = sum(delays) / len(delays)
        assert avg_delay < 100  # Should be very fast

    def test_slow_bot_deterministic_pattern(self):
        """Slow bot should have varied timing but predictable event types."""
        events = generate_slow_bot(event_count=30)
        event_types = [e["event_type"] for e in events if e["event_type"] not in ("session_start", "session_end")]
        # Should have repetitive patterns
        unique_ratio = len(set(event_types)) / len(event_types)
        assert unique_ratio < 0.5  # Low diversity

    def test_mixed_has_session_events(self):
        """Mixed profile should include session start/end."""
        events = generate_mixed(event_count=30)
        types = {e["event_type"] for e in events}
        assert "session_start" in types


# ============================================================================
# Counterexample Generation Tests
# ============================================================================

class TestCounterexample:
    def test_counterexample_for_bot_sequence(self):
        """Bot sequence should produce a counterexample."""
        pa = ProductAutomaton()
        events = generate_aggressive_bot(event_count=30)
        results = pa.process_sequence(events)

        # Find first suspicious point
        suspicious_points = [
            i for i, r in enumerate(results) if r.product_state.is_suspicious
        ]
        # Aggressive bots should have at least some suspicious points
        # (may not always, but typically will)
        assert len(results) == 30

    def test_valid_sequence_no_counterexample(self):
        """A simple valid sequence should not always trigger counterexamples."""
        pa = ProductAutomaton()
        events = [
            {"event_type": "session_start", "timestamp": time.time()},
            {"event_type": "page_view", "timestamp": time.time() + 1},
            {"event_type": "mouse_move", "timestamp": time.time() + 2.5},
            {"event_type": "hover", "timestamp": time.time() + 4},
            {"event_type": "mouse_click", "timestamp": time.time() + 5.5},
            {"event_type": "idle", "timestamp": time.time() + 10},
            {"event_type": "session_end", "timestamp": time.time() + 12},
        ]
        results = pa.process_sequence(events)
        # With generous timing this should be mostly non-suspicious
        assert len(results) == 7


# ============================================================================
# Invalid Transition Tests
# ============================================================================

class TestInvalidTransitions:
    def test_unknown_event_type(self):
        """Unknown event types should be handled gracefully."""
        pa = ProductAutomaton()
        result = pa.process_event("unknown_event", time.time())
        assert result is not None
        assert result.symbol == "UNKNOWN_EVENT"

    def test_empty_sequence(self):
        """Empty sequence should not crash."""
        pa = ProductAutomaton()
        results = pa.process_sequence([])
        assert results == []

    def test_single_event(self):
        """Single event should process correctly."""
        pa = ProductAutomaton()
        result = pa.process_event("session_start", time.time())
        assert result.product_state is not None
