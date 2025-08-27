"""
API data models using Pydantic.
Defines request/response schemas for the chatbot API.
"""
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from enum import Enum


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    user_text: str = Field(..., min_length=1, max_length=1000, description="User input text")
    session_id: Optional[str] = Field(None, description="Optional session ID for conversation continuity")
    
    class Config:
        schema_extra = {
            "example": {
                "user_text": "Hello, how are you?",
                "session_id": "optional-session-id-123"
            }
        }


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    session_id: str = Field(..., description="Session ID for this conversation")
    reply_text: str = Field(..., description="Bot's response text")
    intent: str = Field(..., description="Classified intent from user input")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Intent classification confidence score")
    slots: Dict[str, Any] = Field(default_factory=dict, description="Extracted entities/slots from user input")
    need_human: bool = Field(default=False, description="Whether this conversation needs human intervention")
    turn_count: int = Field(default=1, description="Current turn number in the conversation")
    
    class Config:
        schema_extra = {
            "example": {
                "session_id": "session-id-123",
                "reply_text": "Hello! How can I help you today?",
                "intent": "greet",
                "confidence": 0.95,
                "slots": {},
                "need_human": False,
                "turn_count": 1
            }
        }


class FeedbackType(str, Enum):
    """Enumeration for feedback types."""
    helpful = "helpful"
    not_helpful = "not_helpful"
    incorrect = "incorrect"
    other = "other"


class FeedbackRequest(BaseModel):
    """Request model for user feedback."""
    session_id: str = Field(..., description="Session ID for the feedback")
    feedback_type: FeedbackType = Field(..., description="Type of feedback")
    feedback_text: Optional[str] = Field(None, max_length=1000, description="Optional feedback text")
    
    class Config:
        schema_extra = {
            "example": {
                "session_id": "session-id-123",
                "feedback_type": "helpful",
                "feedback_text": "The chatbot was very helpful in resolving my issue."
            }
        }


class FeedbackResponse(BaseModel):
    """Response model for feedback submission."""
    success: bool = Field(..., description="Whether feedback was successfully recorded")
    message: str = Field(..., description="Confirmation message")
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "message": "Thank you for your feedback!"
            }
        }


class SessionEndRequest(BaseModel):
    """Request model for ending a session."""
    session_id: str = Field(..., description="Session ID to end")
    end_reason: str = Field(default="user_ended", description="Reason for ending the session")
    
    class Config:
        schema_extra = {
            "example": {
                "session_id": "session-id-123",
                "end_reason": "user_ended"
            }
        }


class SessionEndResponse(BaseModel):
    """Response model for session end."""
    success: bool = Field(..., description="Whether session was successfully ended")
    message: str = Field(..., description="Confirmation message")
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "message": "Session ended successfully"
            }
        }


class TransferRequest(BaseModel):
    """Request model for human transfer."""
    session_id: str = Field(..., description="Session ID to transfer")
    reason: Optional[str] = Field(None, description="Reason for transfer")
    
    class Config:
        schema_extra = {
            "example": {
                "session_id": "session-id-123",
                "reason": "Complex technical question"
            }
        }


class TransferResponse(BaseModel):
    """Response model for human transfer."""
    success: bool = Field(..., description="Whether transfer was initiated")
    message: str = Field(..., description="Transfer status message")
    transfer_id: Optional[str] = Field(None, description="Transfer tracking ID")
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "message": "Connecting you to a human agent...",
                "transfer_id": "transfer-123"
            }
        }


class HealthResponse(BaseModel):
    """Response model for health check endpoint."""
    ok: bool = Field(True, description="Health status")
    timestamp: str = Field(..., description="Current timestamp")
    version: str = Field(..., description="Application version")
    
    class Config:
        schema_extra = {
            "example": {
                "ok": True,
                "timestamp": "2024-01-01T12:00:00Z",
                "version": "0.1.0"
            }
        }


class ErrorResponse(BaseModel):
    """Standard error response model."""
    error_code: str = Field(..., description="Error code identifier")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    
    class Config:
        schema_extra = {
            "example": {
                "error_code": "INVALID_INPUT",
                "message": "The provided input is invalid",
                "details": {"field": "user_text", "issue": "Text too long"}
            }
        }