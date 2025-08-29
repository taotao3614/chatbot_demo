"""
Session state management with database storage.
"""
import time
import uuid
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from sqlalchemy.orm import Session as DBSession

from app.config import settings
from app.database import crud, models
from app.database.base import get_db

logger = logging.getLogger(__name__)


@dataclass
class ConversationTurn:
    """Represents a single conversation turn."""
    create_time: datetime
    user_input: str
    intent: str
    confidence: float
    bot_response: str
    slots: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SessionState:
    """Represents a user session state."""
    session_id: str
    create_time: datetime
    update_time: datetime
    turns: List[ConversationTurn] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    
    def add_turn(self, user_input: str, intent: str, confidence: float, 
                 bot_response: str, slots: Dict[str, Any] = None):
        """Add a new conversation turn."""
        turn = ConversationTurn(
            create_time=datetime.now(),
            user_input=user_input,
            intent=intent,
            confidence=confidence,
            bot_response=bot_response,
            slots=slots or {}
        )
        
        self.turns.append(turn)
        self.update_time = datetime.now()
        
        # Keep only recent turns (configurable)
        if len(self.turns) > settings.max_session_turns:
            self.turns = self.turns[-settings.max_session_turns:]
    
    def get_last_intent(self) -> Optional[str]:
        """Get the intent from the last turn."""
        return self.turns[-1].intent if self.turns else None
    
    def is_expired(self) -> bool:
        """Check if session has expired."""
        expiry_time = self.update_time + timedelta(minutes=settings.session_ttl_minutes)
        return datetime.now() > expiry_time


class SessionManager:
    """
    Manages user sessions and conversation state with database storage.
    """
    
    def __init__(self):
        self._last_cleanup = time.time()
        self._db = next(get_db())
    
    def create_session(self, session_id: Optional[str] = None) -> str:
        """Create a new session or return existing session ID."""
        if session_id:
            db_session = crud.get_session(self._db, session_id)
            if db_session and db_session.status == 'active':
                crud.update_session_activity(self._db, session_id)
                return session_id
        
        # Create new session
        new_session_id = session_id or self._generate_session_id()
        crud.create_session(self._db, new_session_id)
        
        # Periodic cleanup
        self._cleanup_expired_sessions()
        
        return new_session_id
    
    def get_session(self, session_id: str) -> Optional[SessionState]:
        """Get session by ID."""
        db_session = crud.get_session(self._db, session_id)
        if not db_session or db_session.status != 'active':
            return None
            
        # Convert database session to SessionState
        now = datetime.now()
        if (now - db_session.update_time).total_seconds() > settings.session_ttl_minutes * 60:
            db_session.status = 'expired'
            self._db.commit()
            return None
            
        # Get recent turns
        db_turns = crud.get_session_turns(self._db, session_id, limit=settings.max_session_turns)
        
        # Create SessionState from database data
        session_state = SessionState(
            session_id=db_session.session_id,
            create_time=db_session.create_time,
            update_time=db_session.update_time
        )
        
        # Add turns
        for db_turn in db_turns:
            session_state.turns.append(
                ConversationTurn(
                    create_time=db_turn.create_time,
                    user_input=db_turn.user_input,
                    intent=db_turn.intent,
                    confidence=db_turn.confidence,
                    bot_response=db_turn.bot_response,
                    slots=db_turn.slots or {}
                )
            )
        
        return session_state
    
    def update_session(self, session_id: str, user_input: str, intent: str, 
                      confidence: float, bot_response: str, slots: Dict[str, Any] = None):
        """Update session with new conversation turn."""
        start_time = time.time()
        
        # Update session activity
        crud.update_session_activity(self._db, session_id)
        
        # Create new turn
        processing_time = int((time.time() - start_time) * 1000)  # Convert to milliseconds
        crud.create_conversation_turn(
            self._db,
            session_id=session_id,
            user_input=user_input,
            intent=intent,
            confidence=confidence,
            bot_response=bot_response,
            slots=slots,
            processing_time=processing_time
        )
    
    def delete_session(self, session_id: str):
        """Close a session."""
        crud.close_session(self._db, session_id)
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get session statistics from database."""
        # Get current date analytics
        today = datetime.now().date()
        analytics = crud.get_session_analytics(
            self._db,
            start_date=today,
            end_date=today
        )
        
        if analytics:
            stats = analytics[0].to_dict()
        else:
            # Count current sessions if no analytics
            active_sessions = self._db.query(models.Session).filter(
                models.Session.status == 'active'
            ).count()
            
            stats = {
                "total_sessions": active_sessions,
                "avg_turns_per_session": 0,
                "avg_session_duration": 0
            }
        
        stats["last_cleanup"] = self._last_cleanup
        return stats
    
    def _generate_session_id(self) -> str:
        """Generate a unique session ID."""
        return str(uuid.uuid4())
    
    def _cleanup_expired_sessions(self):
        """Update expired sessions in database."""
        current_time = time.time()
        
        # Only cleanup every 5 minutes
        if current_time - self._last_cleanup < 300:
            return
            
        # Find and update expired sessions
        expiry_time = datetime.now() - timedelta(minutes=settings.session_ttl_minutes)
        expired_sessions = self._db.query(models.Session).filter(
            models.Session.status == 'active',
            models.Session.update_time < expiry_time
        ).all()
        
        for session in expired_sessions:
            session.status = 'expired'
        
        self._db.commit()
        self._last_cleanup = current_time

    def save_feedback(self, session_id: str, feedback_type: str, feedback_text: str = None) -> bool:
        """保存用户反馈"""
        try:
            from app.database import crud
            
            feedback = crud.create_user_feedback(
                db=self._db,
                session_id=session_id,
                feedback_type=feedback_type,
                feedback_text=feedback_text
            )
            return True if feedback else False
            
        except Exception as e:
            logger.error(f"Error saving feedback: {str(e)}")
            return False
    
    def end_session(self, session_id: str, end_reason: str = "user_ended") -> bool:
        """结束会话"""
        try:
            from app.database import crud
            
            # 更新session状态
            db_session = crud.get_session(self._db, session_id)
            if not db_session:
                return False
                
            db_session.status = 'closed'
            db_session.update_time = datetime.now()
            
            self._db.commit()
            logger.info(f"Session {session_id} ended with reason: {end_reason}")
            return True
            
        except Exception as e:
            logger.error(f"Error ending session: {str(e)}")
            self._db.rollback()
            return False
    
    def request_transfer(self, session_id: str, reason: str = None) -> str:
        """请求转人工"""
        try:
            from app.database import crud
            import uuid
            
            # 生成转接ID
            transfer_id = str(uuid.uuid4())[:8]
            
            # 更新session状态（如果支持transferred状态）
            db_session = crud.get_session(self._db, session_id)
            if db_session:
                # 可以在session_data中记录转接信息
                session_data = db_session.session_data or {}
                session_data['transfer_requested'] = True
                session_data['transfer_id'] = transfer_id
                session_data['transfer_reason'] = reason
                session_data['transfer_time'] = datetime.now().isoformat()
                
                # 更新数据库
                crud.update_session_data(self._db, session_id, session_data)
            
            logger.info(f"Transfer requested for session {session_id} - ID: {transfer_id}")
            return transfer_id
            
        except Exception as e:
            logger.error(f"Error requesting transfer: {str(e)}")
            return "transfer-error"


# Global session manager instance
session_manager = SessionManager()