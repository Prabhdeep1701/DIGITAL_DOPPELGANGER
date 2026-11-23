from pydantic import BaseModel
from typing import Dict, List, Optional, Any
from uuid import UUID


class AutomatonDefinition(BaseModel):
    name: str
    alphabet: List[str]
    states: List[str]
    start_state: str
    accepting_states: List[str]
    suspicious_states: List[str]
    transitions: Dict[str, Dict[str, str]]  # state -> {symbol -> next_state}


class AutomatonStateResponse(BaseModel):
    id: UUID
    session_id: UUID
    automaton_type: str
    state: str
    previous_state: Optional[str]
    input_symbol: Optional[str]
    timestamp: float

    class Config:
        from_attributes = True


class TransitionResult(BaseModel):
    automaton_type: str
    previous_state: str
    input_symbol: str
    new_state: str
    is_suspicious: bool
    detection: Optional[str] = None


class ProductState(BaseModel):
    navigation: str
    interaction: str
    timing: str
    consistency: str


class AutomataLabData(BaseModel):
    automata: List[AutomatonDefinition]
    product_description: str


class SequenceGenerationRequest(BaseModel):
    sequence_type: str  # valid, suspicious, invalid
    length: Optional[int] = 20


class SequenceGenerationResponse(BaseModel):
    sequence: List[str]
    expected_states: List[str]
    is_accepted: bool
    description: str


class CounterexampleResponse(BaseModel):
    observed_sequence: List[str]
    violation_index: int
    expected_symbols: List[str]
    actual_symbol: str
    automaton_state: str
    transition_detail: str
