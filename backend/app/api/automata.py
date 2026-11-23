"""Automata laboratory API endpoints."""

from fastapi import APIRouter
from app.automata.product_automaton import ProductAutomaton
from app.automata.base import ALPHABET, EVENT_TO_SYMBOL
from app.schemas.automata import (
    SequenceGenerationRequest, SequenceGenerationResponse,
    CounterexampleResponse,
)

router = APIRouter()


@router.get("/definitions")
async def get_automata_definitions():
    """Get formal definitions of all automata (Σ, Q, q0, δ, F)."""
    pa = ProductAutomaton()
    definitions = pa.get_definitions()
    return {
        "alphabet": sorted(ALPHABET),
        "event_mapping": EVENT_TO_SYMBOL,
        "automata": definitions,
        "product_description": (
            "Product Automaton = Navigation × Interaction × Timing × Consistency. "
            "The combined state (q_nav, q_int, q_tim, q_con) determines the behavioral classification."
        ),
    }


@router.post("/process-sequence")
async def process_sequence(events: list[dict]):
    """Process a sequence of events through the product automaton and return all state transitions."""
    pa = ProductAutomaton()
    results = pa.process_sequence(events)
    return {
        "results": [
            {
                "event_type": r.event_type,
                "symbol": r.symbol,
                "timestamp": r.timestamp,
                "product_state": {
                    "navigation": r.product_state.navigation,
                    "interaction": r.product_state.interaction,
                    "timing": r.product_state.timing,
                    "consistency": r.product_state.consistency,
                },
                "is_suspicious": r.product_state.is_suspicious,
                "detections": r.detections,
                "transitions": [
                    {
                        "automaton": t.automaton_type,
                        "from": t.from_state,
                        "symbol": t.input_symbol,
                        "to": t.to_state,
                        "suspicious": t.is_suspicious,
                    }
                    for t in r.transitions
                ],
            }
            for r in results
        ],
        "final_state": {
            "navigation": pa.navigation.current_state,
            "interaction": pa.interaction.current_state,
            "timing": pa.timing.current_state,
            "consistency": pa.consistency.current_state,
        },
        "suspicious_counts": pa.get_suspicious_count(),
        "state_distribution": pa.get_state_distribution(),
    }


@router.post("/generate-sequence")
async def generate_sequence(req: SequenceGenerationRequest):
    """Generate test sequences (valid, suspicious, or invalid)."""
    pa = ProductAutomaton()

    if req.sequence_type == "valid":
        seq = pa.navigation.generate_valid_sequence(req.length or 20)
        desc = "A valid sequence that follows expected human-like behavioral patterns."
    elif req.sequence_type == "suspicious":
        seq = pa.navigation.generate_suspicious_sequence(req.length or 20)
        desc = "A sequence designed to trigger suspicious state transitions."
    else:
        # Generate invalid sequence: random symbols
        import random
        seq = random.choices(ALPHABET, k=req.length or 20)
        desc = "A random sequence that may cause unexpected transitions."

    # Process to get expected states
    pa2 = ProductAutomaton()
    import time
    events = [{"event_type": s.lower(), "timestamp": time.time() + i * 0.5} for i, s in enumerate(seq)]
    results = pa2.process_sequence(events)
    states = [str(r.product_state) for r in results]
    is_accepted = pa2.navigation.is_in_accepting_state()

    return {
        "sequence": seq,
        "expected_states": states,
        "is_accepted": is_accepted,
        "description": desc,
    }


@router.post("/counterexample")
async def find_counterexample(events: list[dict]):
    """
    Analyze a sequence and find the first point where behavior deviates
    from expected patterns (counterexample generation).
    """
    pa = ProductAutomaton()
    results = pa.process_sequence(events)

    # Find first suspicious transition
    for i, r in enumerate(results):
        if r.product_state.is_suspicious:
            # Find which automaton triggered it
            suspicious_transitions = [t for t in r.transitions if t.is_suspicious]
            if suspicious_transitions:
                t = suspicious_transitions[0]
                # Determine what symbols would be expected (non-suspicious)
                automaton_map = {
                    "navigation": pa.navigation,
                    "interaction": pa.interaction,
                    "timing": pa.timing,
                    "consistency": pa.consistency,
                }
                aut = automaton_map.get(t.automaton_type)
                expected = []
                if aut:
                    state_trans = aut.transitions.get(t.from_state, {})
                    expected = [
                        sym for sym, next_s in state_trans.items()
                        if sym != "*" and next_s not in aut.suspicious_states
                    ]

                return {
                    "found": True,
                    "violation_index": i,
                    "observed_sequence": [r2.symbol for r2 in results[:i + 1]],
                    "actual_symbol": t.input_symbol,
                    "expected_symbols": expected,
                    "automaton_state": t.from_state,
                    "automaton_type": t.automaton_type,
                    "transition_detail": (
                        f"δ({t.from_state}, {t.input_symbol}) → {t.to_state} "
                        f"[SUSPICIOUS in {t.automaton_type} automaton]"
                    ),
                    "explanation": t.detection_reason or "Suspicious transition detected.",
                }

    return {
        "found": False,
        "message": "No counterexample found — the sequence appears consistent with expected behavior.",
        "observed_sequence": [r.symbol for r in results],
    }
