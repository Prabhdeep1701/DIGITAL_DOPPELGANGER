"""Experiment framework API endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.schemas.experiments import ExperimentRequest, ExperimentResult
from app.simulation.profiles import PROFILES
from app.automata.product_automaton import ProductAutomaton
from app.detection.scorer import BehavioralScorer
from app.services.event_processor import create_session, process_batch

router = APIRouter()
_scorer = BehavioralScorer()


@router.post("/run", response_model=dict)
async def run_experiment(req: ExperimentRequest, db: AsyncSession = Depends(get_db)):
    """
    Run a reproducible experiment with synthetic sessions.

    Generates human, bot, and adversarial sessions, runs the detector,
    and computes accuracy, precision, recall, F1, and confusion matrix.

    DISCLAIMER: These results apply to the synthetic/test dataset only
    and do not establish real-world bot-detection accuracy.
    """
    results = {
        "human_like": [],
        "scripted_bot": [],
        "aggressive_bot": [],
        "slow_bot": [],
        "mixed": [],
    }

    # Generate and classify sessions
    configs = [
        ("human_like", req.human_count, True),     # True = expected human
        ("scripted_bot", req.bot_count // 2, False),
        ("aggressive_bot", req.bot_count // 2, False),
        ("slow_bot", req.adversarial_count // 2, False),
        ("mixed", req.adversarial_count // 2, False),
    ]

    all_predictions = []

    for profile_name, count, is_human in configs:
        generator = PROFILES[profile_name]
        for i in range(count):
            try:
                events = generator(event_count=50)

                # Process through automata
                pa = ProductAutomaton()
                pa_results = pa.process_sequence(events)
                score = _scorer.score_session(pa)

                predicted_human = score["classification"] in ("human_like", "inconclusive")
                all_predictions.append({
                    "profile": profile_name,
                    "actual_human": is_human,
                    "predicted_human": predicted_human,
                    "classification": score["classification"],
                    "score": score["automation_score"],
                })

                results[profile_name].append({
                    "classification": score["classification"],
                    "score": score["automation_score"],
                })
            except Exception:
                pass

    # Compute metrics
    tp = sum(1 for p in all_predictions if p["actual_human"] and p["predicted_human"])
    tn = sum(1 for p in all_predictions if not p["actual_human"] and not p["predicted_human"])
    fp = sum(1 for p in all_predictions if not p["actual_human"] and p["predicted_human"])
    fn = sum(1 for p in all_predictions if p["actual_human"] and not p["predicted_human"])

    total = tp + tn + fp + fn
    accuracy = (tp + tn) / total if total > 0 else 0
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0
    fnr = fn / (fn + tp) if (fn + tp) > 0 else 0

    # Per-profile stats
    per_profile = {}
    for profile_name, profile_results in results.items():
        if profile_results:
            scores = [r["score"] for r in profile_results]
            classifications = {}
            for r in profile_results:
                c = r["classification"]
                classifications[c] = classifications.get(c, 0) + 1
            per_profile[profile_name] = {
                "count": len(profile_results),
                "avg_score": round(sum(scores) / len(scores), 1),
                "min_score": round(min(scores), 1),
                "max_score": round(max(scores), 1),
                "classifications": classifications,
            }

    return {
        "total_sessions": total,
        "accuracy": round(accuracy, 4),
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1_score": round(f1, 4),
        "false_positive_rate": round(fpr, 4),
        "false_negative_rate": round(fnr, 4),
        "confusion_matrix": {
            "true_positive": tp,
            "true_negative": tn,
            "false_positive": fp,
            "false_negative": fn,
        },
        "per_profile": per_profile,
        "disclaimer": (
            "These results apply to the synthetic/test dataset only and do not "
            "establish real-world bot-detection accuracy."
        ),
    }
