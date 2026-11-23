"""Event collection API endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID

from app.database.session import get_db
from app.schemas.events import EventCreate, EventResponse, EventBatch
from app.services.event_processor import process_event
from app.models.models import Event

router = APIRouter()


@router.post("/", response_model=dict)
async def create_event(event: EventCreate, db: AsyncSession = Depends(get_db)):
    """Process a single behavioral event."""
    result = await process_event(
        db,
        session_id=str(event.session_id),
        event_type=event.event_type,
        timestamp=event.timestamp,
        page=event.page,
        target=event.target,
        metadata=event.metadata,
    )
    return result


@router.post("/batch", response_model=dict)
async def create_events_batch(batch: EventBatch, db: AsyncSession = Depends(get_db)):
    """Process a batch of behavioral events."""
    results = []
    for event in batch.events:
        result = await process_event(
            db,
            session_id=str(event.session_id),
            event_type=event.event_type,
            timestamp=event.timestamp,
            page=event.page,
            target=event.target,
            metadata=event.metadata,
        )
        results.append(result)
    return {"processed": len(results), "results": results}


@router.get("/session/{session_id}", response_model=list)
async def get_session_events(session_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get all events for a session."""
    result = await db.execute(
        select(Event)
        .where(Event.session_id == session_id)
        .order_by(Event.sequence_number)
    )
    events = result.scalars().all()
    return [
        {
            "id": str(e.id),
            "event_type": e.event_type,
            "timestamp": e.timestamp,
            "page": e.page,
            "target": e.target,
            "metadata": e.metadata_json,
            "sequence_number": e.sequence_number,
        }
        for e in events
    ]
