"""
Chat API endpoints.
Handles conversation requests and integrates NLP, session management, and response generation.
"""
import logging
from datetime import datetime
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse

from app.api.models import (
    ChatRequest, ChatResponse, ErrorResponse, FeedbackRequest, FeedbackResponse,
    SessionEndRequest, SessionEndResponse, TransferRequest, TransferResponse
)
from app.nlp.intent_classifier import IntentClassifier
from app.policy.response_policy import ResponsePolicy
from app.state.session_manager import session_manager

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize components
intent_classifier = IntentClassifier()
response_policy = ResponsePolicy()

# Create router
router = APIRouter(
    tags=["chat"],
    responses={404: {"model": ErrorResponse}},  # 添加通用错误响应
    default_response_class=JSONResponse  # 设置默认响应类型
)

def clamp_confidence(confidence: float) -> float:
    """限制置信度在0.0-1.0范围内"""
    return max(0.0, min(1.0, float(confidence)))

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Main chat endpoint for processing user messages.
    
    Integrates intent classification, session management, and response generation.
    """
    try:
        # 额外检查：处理纯空白字符的情况
        if not request.user_text.strip():
            return ChatResponse(
                session_id=session_manager.create_session(request.session_id),
                reply_text="I'd be happy to help! Please let me know what you'd like to know about.",
                intent="casual",
                confidence=1.0,
                slots={"category": "empty_input"},
                need_human=False,
                turn_count=1
            )
        
        # Create or get session
        session_id = session_manager.create_session(request.session_id)
        session_state = session_manager.get_session(session_id)
        
        # 计算当前轮次
        current_turn = len(session_state.turns) + 1 if session_state else 1
        
        # Get response using response policy
        response_data = response_policy.get_response(request.user_text)
        
        # 确保置信度在合理范围内
        confidence = clamp_confidence(response_data["confidence"])
        
        # 判断是否需要人工介入
        need_human = response_data.get("need_human", False)
        
        # Update session with this conversation turn
        session_manager.update_session(
            session_id=session_id,
            user_input=request.user_text,
            intent=response_data["source"],  # 使用source作为intent
            confidence=confidence,
            bot_response=response_data["response"],
            slots=response_data.get("metadata", {})
        )
        
        # Log conversation
        logger.info(
            f"Chat - Session: {session_id[:8]}... | "
            f"Source: {response_data['source']} ({confidence:.2f}) | "
            f"Turn: {current_turn} | "
            f"User: {request.user_text[:50]}..."
        )
        
        return ChatResponse(
            session_id=session_id,
            reply_text=response_data["response"],
            intent=response_data["source"],
            confidence=confidence,
            slots=response_data.get("metadata", {}),
            need_human=need_human,
            turn_count=current_turn
        )
        
    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                error_code="PROCESSING_ERROR",
                message="I'm having trouble processing your request right now. Please try again in a moment.",
                details={"error": str(e)}
            ).dict()
        )

@router.post("/save-feedback", response_model=FeedbackResponse)
async def save_feedback(request: FeedbackRequest) -> FeedbackResponse:
    """直接保存反馈到数据库"""
    try:
        from sqlalchemy.orm import Session
        from app.database.base import get_db
        from app.database import models
        from datetime import datetime

        # 获取数据库连接
        db: Session = next(get_db())
        
        try:
            # 直接创建反馈记录
            db_feedback = models.UserFeedback(
                session_id=request.session_id,
                feedback_type=request.feedback_type,
                feedback_text=request.feedback_text
            )
            db.add(db_feedback)
            db.commit()
            db.refresh(db_feedback)
            
            logger.info(f"Feedback saved directly for session {request.session_id[:8]}... - Type: {request.feedback_type}")
            return FeedbackResponse(
                success=True,
                message="Thank you for your feedback!"
            )
            
        except Exception as e:
            db.rollback()
            logger.error(f"Database error saving feedback: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=ErrorResponse(
                    error_code="DB_ERROR",
                    message="Unable to save feedback"
                ).dict()
            )
            
    except Exception as e:
        logger.error(f"Error in save_feedback: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                error_code="FEEDBACK_ERROR",
                message="An error occurred while saving your feedback"
            ).dict()
        )

@router.post("/session/end", response_model=SessionEndResponse)
async def end_session(request: SessionEndRequest) -> SessionEndResponse:
    """
    End a chat session.
    """
    try:
        # 结束会话
        success = session_manager.end_session(
            session_id=request.session_id,
            end_reason=request.end_reason
        )
        
        if success:
            logger.info(f"Session {request.session_id[:8]}... ended - Reason: {request.end_reason}")
            return SessionEndResponse(
                success=True,
                message="Session ended successfully. Thank you for using our service!"
            )
        else:
            raise HTTPException(
                status_code=404,
                detail=ErrorResponse(
                    error_code="SESSION_NOT_FOUND",
                    message="Session not found or already ended"
                ).dict()
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error ending session: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                error_code="SESSION_END_ERROR",
                message="An error occurred while ending the session"
            ).dict()
        )

@router.post("/transfer", response_model=TransferResponse)
async def request_human_transfer(request: TransferRequest) -> TransferResponse:
    """
    Request transfer to human agent.
    """
    try:
        # 验证session存在
        session_state = session_manager.get_session(request.session_id)
        if not session_state:
            raise HTTPException(
                status_code=404,
                detail=ErrorResponse(
                    error_code="SESSION_NOT_FOUND",
                    message="Session not found"
                ).dict()
            )
        
        # 标记会话为转人工状态
        transfer_id = session_manager.request_transfer(
            session_id=request.session_id,
            reason=request.reason
        )
        
        logger.info(f"Transfer requested for session {request.session_id[:8]}... - Reason: {request.reason}")
        
        return TransferResponse(
            success=True,
            message="Connecting you to a human agent. Please wait a moment...",
            transfer_id=transfer_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error requesting transfer: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                error_code="TRANSFER_ERROR",
                message="An error occurred while requesting human assistance"
            ).dict()
        )

@router.get("/session/{session_id}/stats")
async def get_session_stats(session_id: str) -> Dict[str, Any]:
    """
    Get session statistics (useful for debugging and monitoring).
    Future: Can be extended with detailed analytics.
    """
    try:
        session_state = session_manager.get_session(session_id)
        
        if not session_state:
            raise HTTPException(
                status_code=404,
                detail=ErrorResponse(
                    error_code="SESSION_NOT_FOUND",
                    message="Session not found or expired"
                ).dict()
            )
        
        return {
            "session_id": session_id,
            "created_at": session_state.created_at.isoformat(),
            "last_activity": session_state.last_activity.isoformat(),
            "total_turns": len(session_state.turns),
            "intents_used": list(set(turn.intent for turn in session_state.turns)),
            "avg_confidence": sum(turn.confidence for turn in session_state.turns) / len(session_state.turns) if session_state.turns else 0
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session stats: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                error_code="STATS_ERROR",
                message="Unable to retrieve session statistics at this time."
            ).dict()
        )