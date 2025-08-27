"""
API endpoint tests for the chatbot MVP.
"""
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


class TestHealthEndpoint:
    """Test health check endpoints."""
    
    def test_health_check(self):
        """Test basic health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["ok"] is True
        assert "timestamp" in data
        assert "version" in data
    
    def test_system_status(self):
        """Test detailed system status endpoint."""
        response = client.get("/status")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert "session_statistics" in data
        assert "components" in data


class TestChatEndpoint:
    """Test chat conversation endpoints."""
    
    def test_chat_greeting(self):
        """Test greeting intent recognition."""
        response = client.post("/api/v1/chat", json={
            "user_text": "hello"
        })
        
        assert response.status_code == 200
        data = response.json()
        
        assert "session_id" in data
        assert "reply_text" in data
        assert data["intent"] == "greet"
        assert isinstance(data["confidence"], float)
        assert data["confidence"] > 0
    
    def test_chat_faq_hours(self):
        """Test FAQ hours intent recognition."""
        response = client.post("/api/v1/chat", json={
            "user_text": "what are your business hours"
        })
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["intent"] == "faq_hours"
        assert "9 AM to 6 PM" in data["reply_text"]
    
    def test_chat_faq_price(self):
        """Test FAQ price intent recognition."""
        response = client.post("/api/v1/chat", json={
            "user_text": "how much does it cost"
        })
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["intent"] == "faq_price"
        assert "pricing" in data["reply_text"].lower()
    
    def test_chat_fallback(self):
        """Test fallback intent for unrecognized input."""
        response = client.post("/api/v1/chat", json={
            "user_text": "xyz random nonsense text"
        })
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["intent"] == "fallback"
        assert "sorry" in data["reply_text"].lower() or "understand" in data["reply_text"].lower()
    
    def test_chat_session_continuity(self):
        """Test session continuity across multiple messages."""
        # First message
        response1 = client.post("/api/v1/chat", json={
            "user_text": "hello"
        })
        assert response1.status_code == 200
        session_id = response1.json()["session_id"]
        
        # Second message with same session
        response2 = client.post("/api/v1/chat", json={
            "user_text": "what are your hours",
            "session_id": session_id
        })
        assert response2.status_code == 200
        assert response2.json()["session_id"] == session_id
    
    def test_chat_invalid_input(self):
        """Test error handling for invalid input."""
        response = client.post("/api/v1/chat", json={
            "user_text": ""  # Empty text should fail validation
        })
        
        assert response.status_code == 422  # Validation error
    
    def test_session_stats(self):
        """Test session statistics endpoint."""
        # Create a session with some conversation
        chat_response = client.post("/api/v1/chat", json={
            "user_text": "hello"
        })
        session_id = chat_response.json()["session_id"]
        
        # Get session stats
        stats_response = client.get(f"/api/v1/session/{session_id}/stats")
        assert stats_response.status_code == 200
        
        data = stats_response.json()
        assert data["session_id"] == session_id
        assert data["total_turns"] == 1
        assert "greet" in data["intents_used"]
