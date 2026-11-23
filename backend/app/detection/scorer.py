"""
Behavioral Scoring System — transparent, weighted scoring.

Computes a behavioral automation score from multiple signals,
each derived from the automata engine's analysis.

Score components (weights):
    Timing irregularity      20%
    Navigation diversity     20%
    Interaction diversity    20%
    Repetition               15%
    Idle behavior            10%
    Sequence consistency     15%

Scores are 0-100 where:
    0  = Fully human-like
    100 = Fully automated-like

The system does NOT claim probabilistic certainty.
Scores are labeled as "Behavioral Automation Score" not "probability".
"""

from typing import Dict, List, Tuple, Optional
from collections import Counter
import math
import numpy as np

from app.automata.product_automaton import ProductAutomaton, ProductStateSnapshot
from app.automata.consistency import compute_entropy, detect_repetition


class BehavioralScorer:
    """Computes transparent behavioral automation scores."""

    WEIGHTS = {
        "timing_regularity": 0.20,
        "navigation_diversity": 0.20,
        "interaction_diversity": 0.20,
        "repetition": 0.15,
        "idle_behavior": 0.10,
        "sequence_consistency": 0.15,
    }

    def score_session(self, automaton: ProductAutomaton) -> Dict:
        """
        Score a session that has been processed through the product automaton.

        Returns a dict with:
        - automation_score: 0-100
        - human_score: 0-100
        - suspicion_score: 0-100
        - classification: str
        - breakdown: dict of individual factor scores
        - explanations: list of human-readable explanations
        """
        breakdown = {}
        explanations = []

        # 1. Timing regularity (0-100, high = more automated)
        timing_score, timing_explanation = self._score_timing(automaton)
        breakdown["timing_regularity"] = timing_score
        if timing_explanation:
            explanations.append(timing_explanation)

        # 2. Navigation diversity (0-100, high = more automated / less diverse)
        nav_score, nav_explanation = self._score_navigation_diversity(automaton)
        breakdown["navigation_diversity"] = nav_score
        if nav_explanation:
            explanations.append(nav_explanation)

        # 3. Interaction diversity (0-100, high = more automated)
        int_score, int_explanation = self._score_interaction_diversity(automaton)
        breakdown["interaction_diversity"] = int_score
        if int_explanation:
            explanations.append(int_explanation)

        # 4. Repetition (0-100, high = more automated)
        rep_score, rep_explanation = self._score_repetition(automaton)
        breakdown["repetition"] = rep_score
        if rep_explanation:
            explanations.append(rep_explanation)

        # 5. Idle behavior (0-100, high = more automated / no idle)
        idle_score, idle_explanation = self._score_idle_behavior(automaton)
        breakdown["idle_behavior"] = idle_score
        if idle_explanation:
            explanations.append(idle_explanation)

        # 6. Sequence consistency via automata states (0-100, high = more automated)
        cons_score, cons_explanation = self._score_sequence_consistency(automaton)
        breakdown["sequence_consistency"] = cons_score
        if cons_explanation:
            explanations.append(cons_explanation)

        # Weighted automation score
        automation_score = sum(
            breakdown[key] * weight
            for key, weight in self.WEIGHTS.items()
        )
        automation_score = min(100.0, max(0.0, automation_score))
        human_score = 100.0 - automation_score

        # Suspicion score — elevated by suspicious state visits
        suspicious_counts = automaton.get_suspicious_count()
        total_events = len(automaton.history) or 1
        suspicion_ratio = suspicious_counts["total"] / (total_events * 4)  # 4 automata
        suspicion_score = min(100.0, suspicion_ratio * 200)

        # Classification
        classification = self._classify(automation_score, suspicion_score)

        return {
            "automation_score": round(automation_score, 1),
            "human_score": round(human_score, 1),
            "suspicion_score": round(suspicion_score, 1),
            "classification": classification,
            "breakdown": {k: round(v, 1) for k, v in breakdown.items()},
            "weights": self.WEIGHTS,
            "explanations": explanations,
            "suspicious_state_counts": suspicious_counts,
        }

    def _score_timing(self, automaton: ProductAutomaton) -> Tuple[float, Optional[str]]:
        """Score timing regularity. Regular timing = more automated."""
        delays = automaton.recent_delays
        if len(delays) < 3:
            return 50.0, None

        delays_arr = np.array(delays)
        std_dev = float(np.std(delays_arr))
        mean_delay = float(np.mean(delays_arr))
        cv = std_dev / mean_delay if mean_delay > 0 else 0  # Coefficient of variation

        # Low CV = regular timing = suspicious
        # Human CV is typically 0.5-1.5+
        # Bot CV is typically 0.0-0.3
        if cv < 0.1:
            score = 95.0
            explanation = f"Timing is extremely regular (CV={cv:.3f}). Median delay: {np.median(delays_arr):.0f}ms."
        elif cv < 0.3:
            score = 75.0
            explanation = f"Timing is suspiciously regular (CV={cv:.3f})."
        elif cv < 0.5:
            score = 50.0
            explanation = None
        elif cv < 1.0:
            score = 25.0
            explanation = None
        else:
            score = 10.0
            explanation = None

        # Very fast median = additional suspicion
        median = float(np.median(delays_arr))
        if median < 50:
            score = min(100, score + 30)
            explanation = f"Median inter-event time is {median:.0f}ms (impossibly fast for humans)."
        elif median < 150:
            score = min(100, score + 15)

        # Check timing automaton suspicious visits
        timing_sus = automaton.timing.suspicious_count
        if timing_sus > 3:
            score = min(100, score + 10)

        return score, explanation

    def _score_navigation_diversity(self, automaton: ProductAutomaton) -> Tuple[float, Optional[str]]:
        """Score navigation diversity. Low diversity = more automated."""
        distribution = automaton.get_state_distribution()
        nav_states = distribution.get("navigation", {})

        if not nav_states:
            return 50.0, None

        total = sum(nav_states.values())
        unique_states = len(nav_states)
        entropy = compute_entropy(
            [s.navigation for s in automaton.history]
        )

        # Low navigation entropy = bot-like linear navigation
        max_entropy = math.log2(max(unique_states, 1)) if unique_states > 0 else 1
        normalized_entropy = entropy / max_entropy if max_entropy > 0 else 0

        score = max(0, 100 - normalized_entropy * 100)

        # Check for suspicious navigation states
        nav_sus = automaton.navigation.suspicious_count
        if nav_sus > 2:
            score = min(100, score + 15)

        explanation = None
        if score > 70:
            explanation = f"Navigation entropy is low ({entropy:.2f} bits). Only {unique_states} unique navigation states visited."
        return score, explanation

    def _score_interaction_diversity(self, automaton: ProductAutomaton) -> Tuple[float, Optional[str]]:
        """Score interaction diversity. Low diversity = more automated."""
        symbols = automaton.recent_symbols
        if not symbols:
            return 50.0, None

        unique = len(set(symbols))
        total = len(symbols)
        diversity_ratio = unique / total

        # Also check interaction automaton state diversity
        distribution = automaton.get_state_distribution()
        int_states = distribution.get("interaction", {})
        int_diversity = len(int_states)

        # Humans use 5+ different interaction types; bots may use 2-3
        if diversity_ratio < 0.1:
            score = 90.0
        elif diversity_ratio < 0.2:
            score = 70.0
        elif diversity_ratio < 0.3:
            score = 50.0
        elif diversity_ratio < 0.5:
            score = 30.0
        else:
            score = 10.0

        # Adjust for interaction state diversity
        if int_diversity <= 2:
            score = min(100, score + 20)
        elif int_diversity <= 4:
            score = min(100, score + 10)

        explanation = None
        if score > 70:
            explanation = f"Only {unique} unique event types in {total} events. Interaction diversity is very low."
        return score, explanation

    def _score_repetition(self, automaton: ProductAutomaton) -> Tuple[float, Optional[str]]:
        """Score sequence repetition. High repetition = more automated."""
        symbols = automaton.recent_symbols
        if len(symbols) < 6:
            return 50.0, None

        # Check for repeated 3-grams
        rep_3 = detect_repetition(symbols, 3)
        # Check for repeated 5-grams
        rep_5 = detect_repetition(symbols, 5)

        score = min(100, rep_3 * 80 + rep_5 * 60)

        # Count how many times the same exact sub-sequence of length 4+ repeats
        ngram_counts = Counter()
        for n in range(4, min(8, len(symbols))):
            for i in range(len(symbols) - n + 1):
                ngram = tuple(symbols[i:i + n])
                ngram_counts[ngram] += 1

        max_repeat = max(ngram_counts.values()) if ngram_counts else 1
        if max_repeat > 5:
            score = min(100, score + 25)

        explanation = None
        if score > 60:
            if max_repeat > 3:
                # Find the most repeated sequence
                most_common = ngram_counts.most_common(1)[0]
                seq_str = " → ".join(most_common[0])
                explanation = (
                    f"The sequence [{seq_str}] repeated {most_common[1]} times. "
                    f"3-gram repetition rate: {rep_3:.0%}."
                )
            else:
                explanation = f"3-gram repetition rate: {rep_3:.0%}."

        return score, explanation

    def _score_idle_behavior(self, automaton: ProductAutomaton) -> Tuple[float, Optional[str]]:
        """Score idle behavior. No idle periods = more automated."""
        symbols = automaton.recent_symbols
        if not symbols:
            return 50.0, None

        idle_count = symbols.count("IDLE")
        total = len(symbols)
        idle_ratio = idle_count / total

        # Also count slow delays as implicit idle
        slow_delays = sum(1 for d in automaton.recent_delays if d > 2000)
        slow_ratio = slow_delays / max(len(automaton.recent_delays), 1)

        combined_idle = (idle_ratio + slow_ratio) / 2

        # Humans typically have 5-15% idle/slow periods
        if combined_idle < 0.01:
            score = 85.0
            explanation = "No idle periods detected. Sessions without pauses are unusual for humans."
        elif combined_idle < 0.05:
            score = 60.0
            explanation = None
        elif combined_idle < 0.15:
            score = 20.0
            explanation = None
        else:
            score = 10.0
            explanation = None

        return score, explanation

    def _score_sequence_consistency(self, automaton: ProductAutomaton) -> Tuple[float, Optional[str]]:
        """Score based on automata consistency state visits."""
        distribution = automaton.get_state_distribution()
        cons_states = distribution.get("consistency", {})

        if not cons_states:
            return 50.0, None

        total = sum(cons_states.values())
        suspicious_visits = sum(
            cons_states.get(s, 0)
            for s in ["HIGHLY_REPETITIVE", "LOW_ENTROPY", "SUSPICIOUS_CONSISTENCY"]
        )
        human_visits = sum(
            cons_states.get(s, 0)
            for s in ["HUMAN_CONSISTENT", "HIGH_ENTROPY", "DIVERSE"]
        )

        sus_ratio = suspicious_visits / total
        human_ratio = human_visits / total

        score = min(100, max(0, (sus_ratio - human_ratio + 0.5) * 100))

        explanation = None
        if sus_ratio > 0.3:
            explanation = (
                f"Consistency automaton was in suspicious states {suspicious_visits}/{total} times "
                f"({sus_ratio:.0%})."
            )

        return score, explanation

    def _classify(self, automation_score: float, suspicion_score: float) -> str:
        """Classify session based on automation and suspicion scores."""
        if automation_score >= 70 or suspicion_score >= 60:
            return "automated_like"
        elif automation_score >= 45 or suspicion_score >= 35:
            return "suspicious"
        elif automation_score <= 30 and suspicion_score <= 20:
            return "human_like"
        else:
            return "inconclusive"
