"""
CRUD operations for database models.
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from . import models

def create_session(db: Session, session_id: str) -> models.Session:
    """Create a new chat session."""
    db_session = models.Session(
        session_id=session_id,
        created_at=datetime.now(),
        last_activity=datetime.now(),
        status='active'
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session

def get_session(db: Session, session_id: str) -> Optional[models.Session]:
    """Get session by ID."""
    return db.query(models.Session).filter(models.Session.session_id == session_id).first()

def update_session_activity(db: Session, session_id: str) -> Optional[models.Session]:
    """Update session last activity time."""
    db_session = get_session(db, session_id)
    if db_session:
        db_session.last_activity = datetime.now()
        db.commit()
        db.refresh(db_session)
    return db_session

def create_conversation_turn(
    db: Session,
    session_id: str,
    user_input: str,
    intent: str,
    confidence: float,
    bot_response: str,
    slots: Dict[str, Any] = None,
    processing_time: Optional[int] = None
) -> models.ConversationTurn:
    """Create a new conversation turn."""
    # Get the current turn number for this session
    turn_number = db.query(models.ConversationTurn).filter(
        models.ConversationTurn.session_id == session_id
    ).count() + 1

    db_turn = models.ConversationTurn(
        session_id=session_id,
        timestamp=datetime.now(),
        user_input=user_input,
        intent=intent,
        confidence=confidence,
        bot_response=bot_response,
        slots=slots or {},
        turn_number=turn_number,
        processing_time=processing_time
    )
    db.add(db_turn)
    db.commit()
    db.refresh(db_turn)
    return db_turn

def get_session_turns(
    db: Session, 
    session_id: str,
    limit: Optional[int] = None
) -> List[models.ConversationTurn]:
    """Get conversation turns for a session."""
    query = db.query(models.ConversationTurn).filter(
        models.ConversationTurn.session_id == session_id
    ).order_by(models.ConversationTurn.turn_number.desc())
    
    if limit:
        query = query.limit(limit)
    
    return query.all()

def create_user_feedback(
    db: Session,
    session_id: str,
    feedback_type: str,
    feedback_text: Optional[str] = None,
    turn_id: Optional[int] = None
) -> models.UserFeedback:
    """Create user feedback."""
    db_feedback = models.UserFeedback(
        session_id=session_id,
        turn_id=turn_id,
        feedback_type=feedback_type,
        feedback_text=feedback_text,
        created_at=datetime.now()
    )
    db.add(db_feedback)
    db.commit()
    db.refresh(db_feedback)
    return db_feedback

def update_session_data(db: Session, session_id: str, session_data: dict) -> bool:
    """Update session data."""
    try:
        db_session = get_session(db, session_id)
        if db_session:
            db_session.session_data = session_data
            db.commit()
            return True
        return False
    except Exception as e:
        db.rollback()
        return False

def get_session_analytics(
    db: Session,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> List[models.SessionAnalytics]:
    """Get session analytics within date range."""
    query = db.query(models.SessionAnalytics)
    
    if start_date:
        query = query.filter(models.SessionAnalytics.date >= start_date)
    if end_date:
        query = query.filter(models.SessionAnalytics.date <= end_date)
    
    return query.all()

def get_intent_analytics(
    db: Session,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    intent: Optional[str] = None
) -> List[models.IntentAnalytics]:
    """Get intent analytics within date range."""
    query = db.query(models.IntentAnalytics)
    
    if start_date:
        query = query.filter(models.IntentAnalytics.date >= start_date)
    if end_date:
        query = query.filter(models.IntentAnalytics.date <= end_date)
    if intent:
        query = query.filter(models.IntentAnalytics.intent == intent)
    
    return query.all()

def close_session(db: Session, session_id: str) -> Optional[models.Session]:
    """Close a chat session."""
    db_session = get_session(db, session_id)
    if db_session:
        db_session.status = 'closed'
        db_session.last_activity = datetime.now()
        db.commit()
        db.refresh(db_session)
    return db_session
