import uuid
from datetime import datetime

from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey, JSON, Text, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum

from app.database.session import Base


class Classification(str, enum.Enum):
    HUMAN_LIKE = "human_like"
    AUTOMATED_LIKE = "automated_like"
    SUSPICIOUS = "suspicious"
    INCONCLUSIVE = "inconclusive"


class Severity(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")


class Session(Base):
    __tablename__ = "sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    ended_at = Column(DateTime, nullable=True)
    classification = Column(SAEnum(Classification), default=Classification.INCONCLUSIVE)
    score = Column(Float, default=0.0)
    is_simulated = Column(String(50), nullable=True)  # null=real, else profile name
    metadata_json = Column(JSON, nullable=True)

    user = relationship("User", back_populates="sessions")
    events = relationship("Event", back_populates="session", cascade="all, delete-orphan",
                          order_by="Event.timestamp")
    automaton_states = relationship("AutomatonState", back_populates="session",
                                   cascade="all, delete-orphan", order_by="AutomatonState.timestamp")
    detections = relationship("Detection", back_populates="session", cascade="all, delete-orphan")


class Event(Base):
    __tablename__ = "events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.id"), nullable=False)
    event_type = Column(String(50), nullable=False)
    timestamp = Column(Float, nullable=False)  # Unix timestamp with ms precision
    page = Column(String(255), nullable=True)
    target = Column(String(255), nullable=True)
    metadata_json = Column(JSON, nullable=True)  # coordinates, extra info
    sequence_number = Column(Integer, nullable=False)

    session = relationship("Session", back_populates="events")
    automaton_states = relationship("AutomatonState", back_populates="event")
    detections = relationship("Detection", back_populates="event")


class AutomatonState(Base):
    __tablename__ = "automaton_states"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.id"), nullable=False)
    automaton_type = Column(String(50), nullable=False)  # navigation, interaction, timing, consistency
    state = Column(String(100), nullable=False)
    previous_state = Column(String(100), nullable=True)
    input_symbol = Column(String(50), nullable=True)
    timestamp = Column(Float, nullable=False)
    event_id = Column(UUID(as_uuid=True), ForeignKey("events.id"), nullable=True)

    session = relationship("Session", back_populates="automaton_states")
    event = relationship("Event", back_populates="automaton_states")


class Detection(Base):
    __tablename__ = "detections"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.id"), nullable=False)
    reason = Column(Text, nullable=False)
    severity = Column(SAEnum(Severity), default=Severity.LOW)
    event_id = Column(UUID(as_uuid=True), ForeignKey("events.id"), nullable=True)
    automaton_type = Column(String(50), nullable=True)
    from_state = Column(String(100), nullable=True)
    to_state = Column(String(100), nullable=True)
    input_symbol = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    session = relationship("Session", back_populates="detections")
    event = relationship("Event", back_populates="detections")
