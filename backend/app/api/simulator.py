"""Bot simulator and adversarial testing API endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.schemas.simulator import (
    SimulationRequest, SimulationResponse,
    AdversarialTestRequest, AdversarialTestResponse,
)
from app.simulation.profiles import PROFILES
from app.services.event_processor import create_session, process_batch
from app.automata.product_automaton import ProductAutomaton
from app.detection.scorer import BehavioralScorer

router = APIRouter()
_scorer = BehavioralScorer()


@router.post("/run", response_model=dict)
async def run_simulation(req: SimulationRequest, db: AsyncSession = Depends(get_db)):
    """Run a bot simulation with the specified profile."""
    generator = PROFILES.get(req.profile)
    if not generator:
        return {"error": f"Unknown profile: {req.profile}. Available: {list(PROFILES.keys())}"}

    events = generator(event_count=req.event_count or 50, pages=req.pages)
    session = await create_session(db, is_simulated=req.profile)
    result = await process_batch(db, str(session.id), events)

    return {
        "session_id": str(session.id),
        "profile": req.profile,
        "event_count": len(events),
        "classification": result["score"]["classification"],
        "score": result["score"]["automation_score"],
        "scoring_breakdown": result["score"]["breakdown"],
        "explanations": result["score"]["explanations"],
        "suspicious_counts": result["score"]["suspicious_state_counts"],
    }


@router.get("/profiles")
async def list_profiles():
    """List available simulation profiles."""
    return {
        "profiles": [
            {
                "name": "human_like",
                "description": "Irregular timing, varied navigation, occasional idle periods, natural mouse movement",
            },
            {
                "name": "scripted_bot",
                "description": "Regular timing, deterministic navigation, repeated sequences, minimal idle",
            },
            {
                "name": "aggressive_bot",
                "description": "Extremely rapid events, repeated clicks, predictable linear navigation",
            },
            {
                "name": "slow_bot",
                "description": "Randomized timing but deterministic behavior, low interaction diversity",
            },
            {
                "name": "mixed",
                "description": "Starts human-like, transitions to automated behavior midway",
            },
        ]
    }


@router.post("/adversarial", response_model=dict)
async def run_adversarial_test(req: AdversarialTestRequest, db: AsyncSession = Depends(get_db)):
    """
    Run an adversarial test from the Attack Lab.

    Test types:
    - deterministic: Pure deterministic bot
    - randomized: Bot with randomized timing
    - slow: Deliberately slow bot
    - human_like_scripted: Bot mimicking human patterns
    - human: Actual human-like session
    - mixed: Mixed behavior session
    """
    profile_map = {
        "deterministic": "scripted_bot",
        "randomized": "aggressive_bot",
        "slow": "slow_bot",
        "human_like_scripted": "slow_bot",
        "human": "human_like",
        "mixed": "mixed",
    }

    profile = profile_map.get(req.test_type, "human_like")
    generator = PROFILES[profile]
    events = generator(event_count=req.event_count or 50)

    session = await create_session(db, is_simulated=f"adversarial_{req.test_type}")
    result = await process_batch(db, str(session.id), events)

    # Build explanation
    score = result["score"]
    explanation_parts = []
    if score["classification"] == "automated_like":
        explanation_parts.append(
            f"The session was classified as AUTOMATED-LIKE with a score of {score['automation_score']}/100."
        )
    elif score["classification"] == "human_like":
        explanation_parts.append(
            f"The session was classified as HUMAN-LIKE with a score of {score['automation_score']}/100."
        )
    else:
        explanation_parts.append(
            f"The session was classified as {score['classification'].upper()} "
            f"with a score of {score['automation_score']}/100."
        )

    for exp in score.get("explanations", []):
        explanation_parts.append(exp)

    if req.test_type == "slow" and score["classification"] != "automated_like":
        explanation_parts.append(
            "Note: The slow bot uses randomized timing, which can evade simple speed-based detection. "
            "However, the automata engine also examines navigation patterns, interaction diversity, "
            "and behavioral consistency — not just timing."
        )

    return {
        "session_id": str(session.id),
        "test_type": req.test_type,
        "classification": score["classification"],
        "score": score["automation_score"],
        "scoring_breakdown": score["breakdown"],
        "detections": score.get("explanations", []),
        "suspicious_counts": score["suspicious_state_counts"],
        "explanation": " ".join(explanation_parts),
    }
