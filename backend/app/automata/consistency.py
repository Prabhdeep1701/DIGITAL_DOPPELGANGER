"""
Behavioral Consistency Automaton — tracks deviation from reference behavior.

This automaton monitors whether the session's behavioral patterns
are consistent with a learned/reference model of normal human interaction.

It tracks:
- Sequence diversity (how many unique event types used)
- Pattern repetition (same sub-sequences repeating)
- Behavioral entropy
- Deviation from expected event distributions

The automaton processes meta-symbols derived from analyzing
windows of recent events:

    CONSISTENT:    behavior matches reference model
    DIVERSE:       high variety of event types
    REPETITIVE:    repeated sub-sequences detected
    LOW_ENTROPY:   very predictable event stream
    HIGH_ENTROPY:  natural variation
    DEVIATION:     significant departure from reference
"""

from typing import List, Dict, Set
from collections import Counter
import math

from app.automata.base import DFA

STATES = {
    "START",
    "CONSISTENT",
    "DIVERSE",
    "SLIGHTLY_REPETITIVE",
    "HIGHLY_REPETITIVE",
    "LOW_ENTROPY",
    "HIGH_ENTROPY",
    "DEVIATING",
    "SUSPICIOUS_CONSISTENCY",
    "HUMAN_CONSISTENT",
    "END",
}

ACCEPTING = {"END", "CONSISTENT", "DIVERSE", "HIGH_ENTROPY", "HUMAN_CONSISTENT"}
SUSPICIOUS = {"HIGHLY_REPETITIVE", "LOW_ENTROPY", "SUSPICIOUS_CONSISTENCY"}

WINDOW_SIZE = 10
REPETITION_THRESHOLD = 0.6  # 60%+ of n-grams are repeated
ENTROPY_LOW_THRESHOLD = 1.0
DIVERSITY_THRESHOLD = 0.5  # At least 50% unique event types


def compute_entropy(symbols: List[str]) -> float:
    """Compute Shannon entropy of a symbol sequence."""
    if not symbols:
        return 0.0
    counts = Counter(symbols)
    total = len(symbols)
    entropy = 0.0
    for count in counts.values():
        p = count / total
        if p > 0:
            entropy -= p * math.log2(p)
    return entropy


def detect_repetition(symbols: List[str], n: int = 3) -> float:
    """Detect repeated n-grams. Returns ratio of repeated n-grams."""
    if len(symbols) < n:
        return 0.0
    ngrams = []
    for i in range(len(symbols) - n + 1):
        ngrams.append(tuple(symbols[i:i + n]))
    counts = Counter(ngrams)
    repeated = sum(1 for c in counts.values() if c > 1)
    return repeated / len(counts) if counts else 0.0


def compute_diversity(symbols: List[str]) -> float:
    """Compute event type diversity ratio."""
    if not symbols:
        return 0.0
    return len(set(symbols)) / len(symbols)


def classify_consistency(recent_symbols: List[str]) -> str:
    """Classify the consistency of a window of recent symbols."""
    if len(recent_symbols) < 3:
        return "CONSISTENT"

    entropy = compute_entropy(recent_symbols)
    repetition = detect_repetition(recent_symbols)
    diversity = compute_diversity(recent_symbols)

    if repetition > REPETITION_THRESHOLD:
        return "REPETITIVE"
    if entropy < ENTROPY_LOW_THRESHOLD:
        return "LOW_ENTROPY"
    if diversity > DIVERSITY_THRESHOLD and entropy > 2.0:
        return "HIGH_ENTROPY"
    if diversity > DIVERSITY_THRESHOLD:
        return "DIVERSE"
    return "CONSISTENT"


def create_consistency_automaton() -> DFA:
    """
    Build the consistency DFA.

    Humans produce high-entropy, diverse, non-repetitive behavioral streams.
    Bots produce low-entropy, repetitive, predictable streams.
    """
    transitions = {
        "START": {
            "CONSISTENT": "CONSISTENT",
            "DIVERSE": "DIVERSE",
            "REPETITIVE": "SLIGHTLY_REPETITIVE",
            "LOW_ENTROPY": "LOW_ENTROPY",
            "HIGH_ENTROPY": "HIGH_ENTROPY",
            "*": "CONSISTENT",
        },
        "CONSISTENT": {
            "CONSISTENT": "CONSISTENT",
            "DIVERSE": "DIVERSE",
            "REPETITIVE": "SLIGHTLY_REPETITIVE",
            "LOW_ENTROPY": "LOW_ENTROPY",
            "HIGH_ENTROPY": "HUMAN_CONSISTENT",
            "END": "END",
            "*": "CONSISTENT",
        },
        "DIVERSE": {
            "CONSISTENT": "CONSISTENT",
            "DIVERSE": "HUMAN_CONSISTENT",
            "REPETITIVE": "SLIGHTLY_REPETITIVE",
            "LOW_ENTROPY": "CONSISTENT",
            "HIGH_ENTROPY": "HUMAN_CONSISTENT",
            "END": "END",
            "*": "DIVERSE",
        },
        "SLIGHTLY_REPETITIVE": {
            "REPETITIVE": "HIGHLY_REPETITIVE",
            "CONSISTENT": "CONSISTENT",
            "DIVERSE": "DIVERSE",
            "LOW_ENTROPY": "SUSPICIOUS_CONSISTENCY",
            "HIGH_ENTROPY": "CONSISTENT",
            "END": "END",
            "*": "SLIGHTLY_REPETITIVE",
        },
        "HIGHLY_REPETITIVE": {
            "REPETITIVE": "SUSPICIOUS_CONSISTENCY",
            "LOW_ENTROPY": "SUSPICIOUS_CONSISTENCY",
            "CONSISTENT": "SLIGHTLY_REPETITIVE",
            "DIVERSE": "CONSISTENT",
            "HIGH_ENTROPY": "CONSISTENT",
            "END": "END",
            "*": "HIGHLY_REPETITIVE",
        },
        "LOW_ENTROPY": {
            "LOW_ENTROPY": "SUSPICIOUS_CONSISTENCY",
            "REPETITIVE": "SUSPICIOUS_CONSISTENCY",
            "CONSISTENT": "CONSISTENT",
            "DIVERSE": "DIVERSE",
            "HIGH_ENTROPY": "CONSISTENT",
            "END": "END",
            "*": "LOW_ENTROPY",
        },
        "HIGH_ENTROPY": {
            "HIGH_ENTROPY": "HUMAN_CONSISTENT",
            "DIVERSE": "HUMAN_CONSISTENT",
            "CONSISTENT": "CONSISTENT",
            "REPETITIVE": "SLIGHTLY_REPETITIVE",
            "LOW_ENTROPY": "CONSISTENT",
            "END": "END",
            "*": "HIGH_ENTROPY",
        },
        "DEVIATING": {
            "CONSISTENT": "CONSISTENT",
            "DIVERSE": "DIVERSE",
            "REPETITIVE": "SUSPICIOUS_CONSISTENCY",
            "LOW_ENTROPY": "SUSPICIOUS_CONSISTENCY",
            "HIGH_ENTROPY": "CONSISTENT",
            "END": "END",
            "*": "DEVIATING",
        },
        "SUSPICIOUS_CONSISTENCY": {
            "HIGH_ENTROPY": "CONSISTENT",
            "DIVERSE": "CONSISTENT",
            "CONSISTENT": "SLIGHTLY_REPETITIVE",
            "REPETITIVE": "SUSPICIOUS_CONSISTENCY",
            "LOW_ENTROPY": "SUSPICIOUS_CONSISTENCY",
            "END": "END",
            "*": "SUSPICIOUS_CONSISTENCY",
        },
        "HUMAN_CONSISTENT": {
            "CONSISTENT": "CONSISTENT",
            "DIVERSE": "DIVERSE",
            "HIGH_ENTROPY": "HUMAN_CONSISTENT",
            "REPETITIVE": "SLIGHTLY_REPETITIVE",
            "LOW_ENTROPY": "CONSISTENT",
            "END": "END",
            "*": "HUMAN_CONSISTENT",
        },
        "END": {
            "*": "END",
        },
    }

    return DFA(
        name="consistency",
        states=STATES,
        alphabet={"CONSISTENT", "DIVERSE", "REPETITIVE", "LOW_ENTROPY", "HIGH_ENTROPY", "END"},
        transitions=transitions,
        start_state="START",
        accepting_states=ACCEPTING,
        suspicious_states=SUSPICIOUS,
    )
