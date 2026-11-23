"""
Event Processor — the central pipeline that connects events to the automata engine.

Flow:
    Raw Event → Symbol Conversion → Product Automaton → Scoring → Detection → Storage
"""

import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.models import Session, Event, AutomatonState, Detection, User, Classification, Severity
from app.automata.product_automaton import ProductAutomaton, ProcessingResult
from app.automata.base import EVENT_TO_SYMBOL
from app.detection.scorer import BehavioralScorer


# In-memory session automata (for real-time processing)
_active_automata: Dict[str, ProductAutomaton] = {}
_scorer = BehavioralScorer()


def get_or_create_automaton(session_id: str) -> ProductAutomaton:
    """Get or create a product automaton for a session."""
    if session_id not in _active_automata:
        _active_automata[session_id] = ProductAutomaton()
    return _active_automata[session_id]


def remove_automaton(session_id: str):
    """Remove an automaton when session ends."""
    _active_automata.pop(session_id, None)


async def create_session(db: AsyncSession, user_id: Optional[str] = None,
                         is_simulated: Optional[str] = None) -> Session:
    """Create a new session and its associated user if needed."""
    if user_id:
        uid = uuid.UUID(user_id)
    else:
        uid = uuid.uuid4()
        user = User(id=uid)
        db.add(user)

    session = Session(
        id=uuid.uuid4(),
        user_id=uid,
        is_simulated=is_simulated,
    )
    db.add(session)
    await db.flush()
    return session


async def process_event(db: AsyncSession, session_id: str, event_type: str,
                        timestamp: float, page: Optional[str] = None,
                        target: Optional[str] = None,
                        metadata: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Process a single event through the automata pipeline.

    1. Store the event
    2. Feed it to the product automaton
    3. Record automaton state transitions
    4. Record any detections
    5. Return real-time result for WebSocket broadcast
    """
    sid = str(session_id)
    automaton = get_or_create_automaton(sid)

    # Count existing events for sequence number
    count_result = await db.execute(
        select(func.count(Event.id)).where(Event.session_id == uuid.UUID(sid))
    )
    seq_num = (count_result.scalar() or 0) + 1

    # Store event
    event = Event(
        id=uuid.uuid4(),
        session_id=uuid.UUID(sid),
        event_type=event_type,
        timestamp=timestamp,
        page=page,
        target=target,
        metadata_json=metadata,
        sequence_number=seq_num,
    )
    db.add(event)

    # Process through product automaton
    result: ProcessingResult = automaton.process_event(
        event_type=event_type,
        timestamp=timestamp,
        page=page,
        target=target,
    )

    # Store automaton state transitions
    for tr in result.transitions:
        state_record = AutomatonState(
            id=uuid.uuid4(),
            session_id=uuid.UUID(sid),
            automaton_type=tr.automaton_type,
            state=tr.to_state,
            previous_state=tr.from_state,
            input_symbol=tr.input_symbol,
            timestamp=timestamp,
            event_id=event.id,
        )
        db.add(state_record)

    # Store detections
    for detection_reason in result.detections:
        detection = Detection(
            id=uuid.uuid4(),
            session_id=uuid.UUID(sid),
            reason=detection_reason,
            severity=Severity.MEDIUM if not result.product_state.is_suspicious else Severity.HIGH,
            event_id=event.id,
            automaton_type="product",
            from_state=str(result.product_state),
            to_state=str(result.product_state),
            input_symbol=result.symbol,
        )
        db.add(detection)

    await db.flush()

    # Build real-time response
    return {
        "event_id": str(event.id),
        "session_id": sid,
        "event_type": event_type,
        "symbol": result.symbol,
        "timestamp": timestamp,
        "page": page,
        "target": target,
        "sequence_number": seq_num,
        "product_state": {
            "navigation": result.product_state.navigation,
            "interaction": result.product_state.interaction,
            "timing": result.product_state.timing,
            "consistency": result.product_state.consistency,
        },
        "is_suspicious": result.product_state.is_suspicious,
        "detections": result.detections,
        "transitions": [
            {
                "automaton": t.automaton_type,
                "from": t.from_state,
                "symbol": t.input_symbol,
                "to": t.to_state,
                "suspicious": t.is_suspicious,
            }
            for t in result.transitions
        ],
    }


async def finalize_session(db: AsyncSession, session_id: str) -> Dict[str, Any]:
    """
    Finalize a session: compute final scores and classification.
    """
    sid = str(session_id)
    automaton = get_or_create_automaton(sid)

    # Score the session
    score_result = _scorer.score_session(automaton)

    # Update session in DB
    session = await db.get(Session, uuid.UUID(sid))
    if session:
        session.ended_at = datetime.utcnow()
        session.score = score_result["automation_score"]
        session.classification = Classification(score_result["classification"])
        session.metadata_json = {
            "scoring": score_result,
            "state_distribution": automaton.get_state_distribution(),
            "suspicious_counts": automaton.get_suspicious_count(),
        }
        await db.flush()

    remove_automaton(sid)

    return score_result


async def process_batch(db: AsyncSession, session_id: str,
                        events: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Process a batch of events for a session (used by simulator)."""
    results = []
    for event in events:
        result = await process_event(
            db, session_id,
            event_type=event["event_type"],
            timestamp=event["timestamp"],
            page=event.get("page"),
            target=event.get("target"),
            metadata=event.get("metadata"),
        )
        results.append(result)

    # Finalize
    score_result = await finalize_session(db, session_id)

    return {
        "session_id": session_id,
        "event_count": len(events),
        "score": score_result,
        "last_state": results[-1] if results else None,
    }
