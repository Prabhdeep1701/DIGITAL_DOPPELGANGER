from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from uuid import UUID


class EventCreate(BaseModel):
    session_id: UUID
    event_type: str
    timestamp: float
    page: Optional[str] = None
    target: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class EventResponse(BaseModel):
    id: UUID
    session_id: UUID
    event_type: str
    timestamp: float
    page: Optional[str] = None
    target: Optional[str] = None
    metadata_json: Optional[Dict[str, Any]] = None
    sequence_number: int

    class Config:
        from_attributes = True


class EventBatch(BaseModel):
    events: List[EventCreate]
