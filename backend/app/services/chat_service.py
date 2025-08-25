"""
Chat service for managing chat sessions and messages
"""
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.db.redis_client import redis_client
from app.services.ai_service import ai_service
from app.models.chat import ChatMessage, ChatRequest, ChatResponse


class ChatService:
    """Service for managing chat sessions and messages"""
    
    @staticmethod
    def create_session() -> str:
        """Create a new chat session"""
        session_id = str(uuid.uuid4())
        session_data = {
            "session_id": session_id,
            "messages": [],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "group_id": 1,  # Default group ID for PostgreSQL compatibility
            "created_by": 1,  # Default user ID for PostgreSQL compatibility
            "topic": "Chat Session"  # Default topic
        }
        
        success = redis_client.store_session(session_id, session_data)
        if not success:
            print(f"⚠️ Warning: Failed to store session {session_id} in Redis")
        return session_id
    
    @staticmethod
    def get_session_history(session_id: str) -> Optional[List[Dict[str, Any]]]:
        """Get chat history for a session"""
        session = redis_client.get_session(session_id)
        if session:
            return session["messages"]
        return None
    
    @staticmethod
    def get_session_info(session_id: str) -> Optional[Dict[str, Any]]:
        """Get session information"""
        return redis_client.get_session_info(session_id)
    
    @staticmethod
    def _get_sender_id(sender: str) -> int:
        """Map sender type to user ID for PostgreSQL compatibility"""
        # Map sender types to user IDs
        # 'user' -> user_id = 1 (default human user)
        # 'ai' -> user_id = 2 (AI assistant)
        if sender == "user":
            return 1
        elif sender == "ai":
            return 2
        else:
            return 1  # Default to user
    
    @staticmethod
    async def send_message(session_id: str, request: ChatRequest) -> Optional[ChatResponse]:
        """Send a message and get AI response"""
        session = redis_client.get_session(session_id)
        if not session:
            return None
        
        # Create user message
        user_message = ChatMessage(
            id=request.id,
            sender=request.sender,
            content=request.content,
            timestamp=request.timestamp
        )
        
        # Convert message to storage format with sender_id for PostgreSQL compatibility
        user_message_data = user_message.dict()
        user_message_data['sender_id'] = ChatService._get_sender_id(user_message.sender)
        
        # Store user message
        success = redis_client.add_message_to_session(session_id, user_message_data)
        if not success:
            print(f"⚠️ Warning: Failed to store user message for session {session_id}")
        
        # Generate AI response
        ai_response_content = await ai_service.generate_response(
            request.content, 
            session.get("messages", [])
        )
        
        # Create AI message
        ai_message = ChatMessage(
            id=str(uuid.uuid4()),
            sender="ai",
            content=ai_response_content,
            timestamp=datetime.now()
        )
        
        # Convert AI message to storage format with sender_id
        ai_message_data = ai_message.dict()
        ai_message_data['sender_id'] = ChatService._get_sender_id(ai_message.sender)
        
        # Store AI message
        success = redis_client.add_message_to_session(session_id, ai_message_data)
        if not success:
            print(f"⚠️ Warning: Failed to store AI message for session {session_id}")
        
        return ChatResponse(userMessage=user_message, aiMessage=ai_message)
    
    @staticmethod
    def delete_session(session_id: str) -> bool:
        """Delete a chat session"""
        return redis_client.delete_session(session_id)
    
    @staticmethod
    def get_all_sessions() -> List[str]:
        """Get all active session IDs (for debugging)"""
        return redis_client.get_all_sessions()


# Create global chat service instance
chat_service = ChatService()
