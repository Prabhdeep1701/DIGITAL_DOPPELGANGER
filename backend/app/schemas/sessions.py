from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime


class SessionCreate(BaseModel):
    user_id: Optional[UUID] = None
    is_simulated: Optional[str] = None


class SessionResponse(BaseModel):
    id: UUID
    user_id: UUID
    started_at: datetime
    ended_at: Optional[datetime] = None
    classification: str
    score: float
    is_simulated: Optional[str] = None
    event_count: Optional[int] = None

    class Config:
        from_attributes = True


class SessionDetail(SessionResponse):
    events: List[Dict[str, Any]] = []
    automaton_states: List[Dict[str, Any]] = []
    detections: List[Dict[str, Any]] = []
    scoring_breakdown: Optional[Dict[str, Any]] = None


class SessionComparison(BaseModel):
    session_a: SessionDetail
    session_b: SessionDetail
    comparison: Dict[str, Any]


class DashboardStats(BaseModel):
    total_sessions: int
    active_sessions: int
    human_like: int
    automated_like: int
    suspicious: int
    inconclusive: int
    average_score: float
    total_events: int
    total_detections: int
    recent_sessions: List[SessionResponse]
