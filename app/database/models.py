"""
SQLAlchemy models for database tables.
"""
from datetime import datetime
from typing import Dict, Any
from sqlalchemy import (
    Column, Integer, String, DateTime, Text, 
    Float, Enum, JSON, ForeignKey, BigInteger
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base

class Session(Base):
    """Database model for chat sessions."""
    __tablename__ = "sessions"

    session_id = Column(String(36), primary_key=True)
    status = Column(
        Enum('active', 'expired', 'closed', name='session_status'),
        nullable=False,
        default='active'
    )
    session_data = Column(JSON)
    create_time = Column(DateTime, nullable=False, default=func.now())
    update_time = Column(
        DateTime, 
        nullable=False, 
        default=func.now(),
        onupdate=func.now()
    )

    # Relationships
    turns = relationship("ConversationTurn", back_populates="session")
    feedback = relationship("UserFeedback", back_populates="session")

    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary."""
        return {
            "session_id": self.session_id,
            "create_time": self.create_time.isoformat(),
            "update_time": self.update_time.isoformat(),
            "status": self.status,
            "session_data": self.session_data or {}
        }


class ConversationTurn(Base):
    """Database model for conversation turns."""
    __tablename__ = "conversation_turns"

    turn_id = Column(BigInteger, primary_key=True, autoincrement=True)
    session_id = Column(String(36), ForeignKey("sessions.session_id"), nullable=False)
    user_input = Column(Text, nullable=False)
    intent = Column(String(50), nullable=False)
    confidence = Column(Float, nullable=False)
    bot_response = Column(Text, nullable=False)
    slots = Column(JSON)
    turn_number = Column(Integer, nullable=False)
    processing_time = Column(Integer)  # in milliseconds
    emotion = Column(Enum('positive', 'negative', 'neutral', name='emotion_type'), nullable=False, default='neutral')
    urgency = Column(Enum('high', 'medium', 'low', name='urgency_level'), nullable=False, default='low')
    create_time = Column(DateTime, nullable=False, default=func.now())
    update_time = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())

    # Relationships
    session = relationship("Session", back_populates="turns")
    feedback = relationship("UserFeedback", back_populates="turn")

    def to_dict(self) -> Dict[str, Any]:
        """Convert turn to dictionary."""
        return {
            "turn_id": self.turn_id,
            "session_id": self.session_id,
            "create_time": self.create_time.isoformat(),
            "user_input": self.user_input,
            "intent": self.intent,
            "confidence": self.confidence,
            "bot_response": self.bot_response,
            "slots": self.slots or {},
            "turn_number": self.turn_number,
            "processing_time": self.processing_time,
            "emotion": self.emotion,
            "urgency": self.urgency
        }


class IntentAnalytics(Base):
    """Database model for intent analytics."""
    __tablename__ = "intent_analytics"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    intent = Column(String(50), nullable=False)
    total_occurrences = Column(Integer, nullable=False, default=0)
    avg_confidence = Column(Float, nullable=False, default=0.0)
    success_rate = Column(Float, nullable=False, default=0.0)
    create_time = Column(DateTime, nullable=False, default=func.now())
    update_time = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())

    def to_dict(self) -> Dict[str, Any]:
        """Convert analytics to dictionary."""
        return {
            "intent": self.intent,
            "create_time": self.create_time.isoformat(),
            "total_occurrences": self.total_occurrences,
            "avg_confidence": self.avg_confidence,
            "success_rate": self.success_rate
        }


class SessionAnalytics(Base):
    """Database model for session analytics."""
    __tablename__ = "session_analytics"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    total_sessions = Column(Integer, nullable=False, default=0)
    avg_turns_per_session = Column(Float, nullable=False, default=0.0)
    avg_session_duration = Column(Integer, nullable=False, default=0)  # in seconds
    create_time = Column(DateTime, nullable=False, default=func.now())
    update_time = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())

    def to_dict(self) -> Dict[str, Any]:
        """Convert analytics to dictionary."""
        return {
            "create_time": self.create_time.isoformat(),
            "total_sessions": self.total_sessions,
            "avg_turns_per_session": self.avg_turns_per_session,
            "avg_session_duration": self.avg_session_duration
        }


class UserFeedback(Base):
    """Database model for user feedback."""
    __tablename__ = "user_feedback"

    feedback_id = Column(BigInteger, primary_key=True, autoincrement=True)
    session_id = Column(String(36), ForeignKey("sessions.session_id"), nullable=False)
    turn_id = Column(BigInteger, ForeignKey("conversation_turns.turn_id"))
    feedback_type = Column(
        Enum('helpful', 'not_helpful', 'incorrect', 'other', name='feedback_type'),
        nullable=False
    )
    feedback_text = Column(Text)
    create_time = Column(DateTime, nullable=False, default=func.now())
    update_time = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())

    # Relationships
    session = relationship("Session", back_populates="feedback")
    turn = relationship("ConversationTurn", back_populates="feedback")

    def to_dict(self) -> Dict[str, Any]:
        """Convert feedback to dictionary."""
        return {
            "feedback_id": self.feedback_id,
            "session_id": self.session_id,
            "turn_id": self.turn_id,
            "feedback_type": self.feedback_type,
            "feedback_text": self.feedback_text,
            "create_time": self.create_time.isoformat(),
            "update_time": self.update_time.isoformat()
        }