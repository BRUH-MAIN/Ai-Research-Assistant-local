"""
Chat service for managing chat sessions and messages
"""
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.core.config import settings
from app.services.ai_service import ai_service
from app.models.chat import ChatMessage, ChatRequest, ChatResponse

if settings.ENABLE_REDIS_SYNC:
    from app.db.redis_client import redis_client
else:
    # Use PostgreSQL directly when Redis is disabled
    from app.db.postgres_manager.db import SessionLocal
    from app.db.postgres_manager.managers.sessions import SessionManager
    from app.db.postgres_manager.managers.messages import MessageManager
    from app.db.postgres_manager.managers.users import UserManager
    from app.db.postgres_manager.managers.groups import GroupManager
    from app.db.postgres_manager.managers.group_participants import GroupParticipantManager


class ChatService:
    """Service for managing chat sessions and messages"""
    
    @staticmethod
    def create_session() -> str:
        """Create a new chat session"""
        session_id = str(uuid.uuid4())
        
        if settings.ENABLE_REDIS_SYNC:
            session_data = {
                "session_id": session_id,
                "messages": [],
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "group_id": 1,  # Default group ID for PostgreSQL compatibility
                "created_by": 1,  # Default user ID for PostgreSQL compatibility
                "topic": "Chat Session"  # Default topic
            }
            
            redis_client.store_session(session_id, session_data)
        else:
            # Store directly in PostgreSQL
            db = SessionLocal()
            try:
                # Ensure default user and group exist
                user = UserManager.get_user_by_id(db, 1)
                if not user:
                    user = UserManager.create_user(db, email="user@default.com", first_name="Default User")
                
                group = GroupManager.get_group_by_id(db, 1)
                if not group:
                    group = GroupManager.create_group(db, name="Default Group", created_by=user.user_id)
                
                # Ensure group participant exists
                participant = GroupParticipantManager.get_participant_by_group_and_user(db, group.group_id, user.user_id)
                if not participant:
                    participant = GroupParticipantManager.create_group_participant(db, group.group_id, user.user_id, "user")
                
                # Create session
                session = SessionManager.create_session(
                    db,
                    group_id=group.group_id,
                    created_by=participant.group_participant_id,
                    topic=f"Chat Session {session_id[:8]}"
                )
                
                # Use the actual PostgreSQL session ID as our session ID
                session_id = str(session.session_id)
                
            finally:
                db.close()
        
        return session_id
    
    @staticmethod
    def get_session_history(session_id: str) -> Optional[List[Dict[str, Any]]]:
        """Get chat history for a session"""
        if settings.ENABLE_REDIS_SYNC:
            session = redis_client.get_session(session_id)
            if session:
                return session["messages"]
            return None
        else:
            # Get from PostgreSQL directly
            db = SessionLocal()
            try:
                # Convert session_id to int for PostgreSQL lookup
                try:
                    pg_session_id = int(session_id)
                except ValueError:
                    return None
                
                messages = MessageManager.get_messages_by_session(db, pg_session_id)
                formatted_messages = []
                
                for msg in messages:
                    # Get sender info
                    sender_type = "ai" if msg.sender_id == 2 else "user"
                    
                    formatted_messages.append({
                        "content": msg.content,
                        "sender": sender_type,
                        "timestamp": msg.sent_at.isoformat() if msg.sent_at else datetime.now().isoformat()
                    })
                
                return formatted_messages
            finally:
                db.close()
    
    @staticmethod
    def _get_sender_id(sender: str) -> int:
        """Map sender type to user ID for PostgreSQL compatibility"""
        if sender == "user":
            return 1
        elif sender == "ai":
            return 2
        else:
            return 1  # Default to user
    
    @staticmethod
    async def send_message(session_id: str, request: ChatRequest) -> Optional[ChatResponse]:
        """Send a message and get AI response"""
        if settings.ENABLE_REDIS_SYNC:
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
            redis_client.add_message_to_session(session_id, user_message_data)
            
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
            redis_client.add_message_to_session(session_id, ai_message_data)
            
            return ChatResponse(
                response=ai_response_content,
                session_id=session_id
            )
        else:
            # Direct PostgreSQL approach
            db = SessionLocal()
            try:
                # Convert session_id to int for PostgreSQL lookup
                try:
                    pg_session_id = int(session_id)
                except ValueError:
                    return None
                
                # Check if session exists
                session = SessionManager.get_session_by_id(db, pg_session_id)
                if not session:
                    return None
                
                # Get current messages for context
                current_messages = MessageManager.get_messages_by_session(db, pg_session_id)
                message_history = []
                for msg in current_messages:
                    sender_type = "ai" if msg.sender_id == 2 else "user"
                    message_history.append({
                        "content": msg.content,
                        "sender": sender_type,
                        "timestamp": msg.sent_at.isoformat() if msg.sent_at else datetime.now().isoformat()
                    })
                
                # Get user participant ID
                user_participant = GroupParticipantManager.get_participant_by_group_and_user(db, session.group_id, 1)
                if not user_participant:
                    return None
                
                # Store user message
                MessageManager.create_message(
                    db,
                    session_id=pg_session_id,
                    sender_id=user_participant.group_participant_id,
                    content=request.content
                )
                
                # Generate AI response
                ai_response_content = await ai_service.generate_response(
                    request.content, 
                    message_history
                )
                
                # Get AI participant ID
                ai_participant = GroupParticipantManager.get_participant_by_group_and_user(db, session.group_id, 2)
                if not ai_participant:
                    # Create AI participant if it doesn't exist
                    ai_user = UserManager.get_user_by_id(db, 2)
                    if not ai_user:
                        ai_user = UserManager.create_user(db, email="ai@assistant.com", first_name="AI Assistant")
                    ai_participant = GroupParticipantManager.create_group_participant(db, session.group_id, ai_user.user_id, "ai")
                
                # Store AI message
                MessageManager.create_message(
                    db,
                    session_id=pg_session_id,
                    sender_id=ai_participant.group_participant_id,
                    content=ai_response_content
                )
                
                return ChatResponse(
                    response=ai_response_content,
                    session_id=session_id
                )
                
            finally:
                db.close()
    
    @staticmethod
    def delete_session(session_id: str) -> bool:
        """Delete a chat session"""
        if settings.ENABLE_REDIS_SYNC:
            return redis_client.delete_session(session_id)
        else:
            # Delete from PostgreSQL
            db = SessionLocal()
            try:
                try:
                    pg_session_id = int(session_id)
                except ValueError:
                    return False
                
                session = SessionManager.get_session_by_id(db, pg_session_id)
                if session:
                    SessionManager.delete_session(db, pg_session_id)
                    return True
                return False
            finally:
                db.close()
    
    @staticmethod
    def get_all_sessions() -> List[str]:
        """Get all active session IDs (for debugging)"""
        if settings.ENABLE_REDIS_SYNC:
            return redis_client.get_all_sessions()
        else:
            # Get from PostgreSQL
            db = SessionLocal()
            try:
                sessions = SessionManager.get_all_sessions(db)
                return [str(session.session_id) for session in sessions]
            finally:
                db.close()


# Create global chat service instance
chat_service = ChatService()
