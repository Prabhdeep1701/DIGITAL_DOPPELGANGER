# Experimental Evaluation

## Methodology

The experiment framework generates synthetic sessions of three types:

1. **Human-like sessions** (ground truth: human) — Irregular timing, varied navigation, occasional idle periods
2. **Bot sessions** (ground truth: bot) — Scripted and aggressive automation profiles
3. **Adversarial sessions** (ground truth: bot) — Slow bots and mixed-behavior sessions designed to evade simple detection

Each session is processed through the full automata pipeline and classified.

## Metrics

| Metric | Definition |
|--------|-----------|
| Accuracy | (TP + TN) / Total |
| Precision | TP / (TP + FP) |
| Recall | TP / (TP + FN) |
| F1 Score | 2 × Precision × Recall / (Precision + Recall) |
| False Positive Rate | FP / (FP + TN) |
| False Negative Rate | FN / (FN + TP) |

Where:
- TP = Human correctly classified as human
- TN = Bot correctly classified as bot
- FP = Bot incorrectly classified as human
- FN = Human incorrectly classified as bot

## Running Experiments

### Via API
```bash
curl -X POST http://localhost:8000/api/experiments/run \
  -H "Content-Type: application/json" \
  -d '{"human_count": 100, "bot_count": 100, "adversarial_count": 100}'
```

### Via Web Interface
Navigate to `/analytics` and configure the experiment parameters.

## Disclaimer

**These results apply to the synthetic/test dataset only and do not establish real-world bot-detection accuracy.**

The synthetic profiles are designed to represent broad categories of behavior. Real-world interaction patterns are significantly more complex and varied. The experiment framework is intended for evaluating the automata engine's design, not for making production detection claims.

## Adversarial Analysis

The Attack Lab (`/attack-lab`) specifically tests edge cases:

1. **Deterministic Bot** — Should be reliably detected via repetition and low diversity
2. **Randomized Bot** — Tests whether speed alone triggers detection
3. **Slow Bot** — Demonstrates that "fast = bot" is insufficient; the automata also examine navigation patterns, interaction diversity, and consistency
4. **Human-Like Scripted** — Tests the limits of behavioral mimicry
5. **Mixed Behavior** — Tests detection of behavioral transitions within a session
