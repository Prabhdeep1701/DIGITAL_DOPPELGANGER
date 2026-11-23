from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class SimulationRequest(BaseModel):
    profile: str  # human_like, scripted_bot, aggressive_bot, slow_bot, mixed
    event_count: Optional[int] = 50
    pages: Optional[List[str]] = None


class SimulationResponse(BaseModel):
    session_id: str
    profile: str
    event_count: int
    classification: str
    score: float
    events_summary: Dict[str, Any]


class AdversarialTestRequest(BaseModel):
    test_type: str  # deterministic, randomized, slow, human_like_scripted, human, mixed
    event_count: Optional[int] = 50


class AdversarialTestResponse(BaseModel):
    session_id: str
    test_type: str
    classification: str
    score: float
    scoring_breakdown: Dict[str, float]
    detections: List[Dict[str, Any]]
    explanation: str
