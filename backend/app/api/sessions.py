"""Session management API endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from uuid import UUID
from typing import Optional

from app.database.session import get_db
from app.schemas.sessions import SessionCreate, SessionResponse, SessionDetail, DashboardStats
from app.services.event_processor import create_session, finalize_session
from app.models.models import Session, Event, AutomatonState, Detection, Classification

router = APIRouter()


@router.post("/", response_model=dict)
async def start_session(req: SessionCreate, db: AsyncSession = Depends(get_db)):
    """Start a new behavioral session."""
    session = await create_session(
        db,
        user_id=str(req.user_id) if req.user_id else None,
        is_simulated=req.is_simulated,
    )
    return {"session_id": str(session.id), "user_id": str(session.user_id)}


@router.post("/{session_id}/end", response_model=dict)
async def end_session(session_id: UUID, db: AsyncSession = Depends(get_db)):
    """End a session and compute final classification."""
    score_result = await finalize_session(db, str(session_id))
    return score_result


@router.get("/", response_model=list)
async def list_sessions(
    limit: int = 50,
    offset: int = 0,
    classification: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """List all sessions with optional filtering."""
    query = select(Session).order_by(desc(Session.started_at))
    if classification:
        query = query.where(Session.classification == classification)
    query = query.offset(offset).limit(limit)

    result = await db.execute(query)
    sessions = result.scalars().all()

    output = []
    for s in sessions:
        # Count events
        event_count = await db.execute(
            select(func.count(Event.id)).where(Event.session_id == s.id)
        )
        output.append({
            "id": str(s.id),
            "user_id": str(s.user_id),
            "started_at": s.started_at.isoformat() if s.started_at else None,
            "ended_at": s.ended_at.isoformat() if s.ended_at else None,
            "classification": s.classification.value if s.classification else "inconclusive",
            "score": s.score or 0,
            "is_simulated": s.is_simulated,
            "event_count": event_count.scalar() or 0,
        })
    return output


@router.get("/dashboard", response_model=dict)
async def get_dashboard_stats(db: AsyncSession = Depends(get_db)):
    """Get dashboard statistics."""
    total = (await db.execute(select(func.count(Session.id)))).scalar() or 0
    active = (await db.execute(
        select(func.count(Session.id)).where(Session.ended_at.is_(None))
    )).scalar() or 0

    classifications = {}
    for c in Classification:
        count = (await db.execute(
            select(func.count(Session.id)).where(Session.classification == c)
        )).scalar() or 0
        classifications[c.value] = count

    avg_score = (await db.execute(
        select(func.avg(Session.score)).where(Session.score.isnot(None))
    )).scalar() or 0

    total_events = (await db.execute(select(func.count(Event.id)))).scalar() or 0
    total_detections = (await db.execute(select(func.count(Detection.id)))).scalar() or 0

    # Recent sessions
    recent_result = await db.execute(
        select(Session).order_by(desc(Session.started_at)).limit(10)
    )
    recent = recent_result.scalars().all()

    return {
        "total_sessions": total,
        "active_sessions": active,
        "human_like": classifications.get("human_like", 0),
        "automated_like": classifications.get("automated_like", 0),
        "suspicious": classifications.get("suspicious", 0),
        "inconclusive": classifications.get("inconclusive", 0),
        "average_score": round(float(avg_score), 1),
        "total_events": total_events,
        "total_detections": total_detections,
        "recent_sessions": [
            {
                "id": str(s.id),
                "user_id": str(s.user_id),
                "started_at": s.started_at.isoformat() if s.started_at else None,
                "ended_at": s.ended_at.isoformat() if s.ended_at else None,
                "classification": s.classification.value if s.classification else "inconclusive",
                "score": s.score or 0,
                "is_simulated": s.is_simulated,
            }
            for s in recent
        ],
    }


@router.get("/{session_id}", response_model=dict)
async def get_session_detail(session_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get detailed session information including events, states, and detections."""
    session = await db.get(Session, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Get events
    events_result = await db.execute(
        select(Event).where(Event.session_id == session_id).order_by(Event.sequence_number)
    )
    events = events_result.scalars().all()

    # Get automaton states
    states_result = await db.execute(
        select(AutomatonState).where(AutomatonState.session_id == session_id)
        .order_by(AutomatonState.timestamp)
    )
    states = states_result.scalars().all()

    # Get detections
    det_result = await db.execute(
        select(Detection).where(Detection.session_id == session_id)
        .order_by(Detection.created_at)
    )
    detections = det_result.scalars().all()

    return {
        "id": str(session.id),
        "user_id": str(session.user_id),
        "started_at": session.started_at.isoformat() if session.started_at else None,
        "ended_at": session.ended_at.isoformat() if session.ended_at else None,
        "classification": session.classification.value if session.classification else "inconclusive",
        "score": session.score or 0,
        "is_simulated": session.is_simulated,
        "scoring_breakdown": session.metadata_json.get("scoring") if session.metadata_json else None,
        "events": [
            {
                "id": str(e.id),
                "event_type": e.event_type,
                "timestamp": e.timestamp,
                "page": e.page,
                "target": e.target,
                "sequence_number": e.sequence_number,
                "metadata": e.metadata_json,
            }
            for e in events
        ],
        "automaton_states": [
            {
                "id": str(s.id),
                "automaton_type": s.automaton_type,
                "state": s.state,
                "previous_state": s.previous_state,
                "input_symbol": s.input_symbol,
                "timestamp": s.timestamp,
                "event_id": str(s.event_id) if s.event_id else None,
            }
            for s in states
        ],
        "detections": [
            {
                "id": str(d.id),
                "reason": d.reason,
                "severity": d.severity.value if d.severity else "low",
                "automaton_type": d.automaton_type,
                "from_state": d.from_state,
                "to_state": d.to_state,
                "input_symbol": d.input_symbol,
                "created_at": d.created_at.isoformat() if d.created_at else None,
                "event_id": str(d.event_id) if d.event_id else None,
            }
            for d in detections
        ],
    }


@router.get("/compare/{session_a_id}/{session_b_id}", response_model=dict)
async def compare_sessions(
    session_a_id: UUID, session_b_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Compare two sessions side by side."""
    # Fetch both sessions with details (reuse get_session_detail logic)
    session_a = await db.get(Session, session_a_id)
    session_b = await db.get(Session, session_b_id)
    if not session_a or not session_b:
        raise HTTPException(status_code=404, detail="One or both sessions not found")

    # Get event counts and stats
    a_events = (await db.execute(
        select(func.count(Event.id)).where(Event.session_id == session_a_id)
    )).scalar() or 0
    b_events = (await db.execute(
        select(func.count(Event.id)).where(Event.session_id == session_b_id)
    )).scalar() or 0

    a_detections = (await db.execute(
        select(func.count(Detection.id)).where(Detection.session_id == session_a_id)
    )).scalar() or 0
    b_detections = (await db.execute(
        select(func.count(Detection.id)).where(Detection.session_id == session_b_id)
    )).scalar() or 0

    scoring_a = session_a.metadata_json.get("scoring", {}) if session_a.metadata_json else {}
    scoring_b = session_b.metadata_json.get("scoring", {}) if session_b.metadata_json else {}

    return {
        "session_a": {
            "id": str(session_a.id),
            "classification": session_a.classification.value if session_a.classification else "inconclusive",
            "score": session_a.score or 0,
            "event_count": a_events,
            "detection_count": a_detections,
            "is_simulated": session_a.is_simulated,
            "scoring_breakdown": scoring_a.get("breakdown", {}),
        },
        "session_b": {
            "id": str(session_b.id),
            "classification": session_b.classification.value if session_b.classification else "inconclusive",
            "score": session_b.score or 0,
            "event_count": b_events,
            "detection_count": b_detections,
            "is_simulated": session_b.is_simulated,
            "scoring_breakdown": scoring_b.get("breakdown", {}),
        },
        "comparison": {
            "score_difference": abs((session_a.score or 0) - (session_b.score or 0)),
            "event_count_difference": abs(a_events - b_events),
            "detection_count_difference": abs(a_detections - b_detections),
            "same_classification": (
                (session_a.classification.value if session_a.classification else "") ==
                (session_b.classification.value if session_b.classification else "")
            ),
        },
    }
