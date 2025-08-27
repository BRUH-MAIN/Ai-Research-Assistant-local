"""
Redis to PostgreSQL synchronization service
"""
import asyncio
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from app.db.redis_client import redis_client
from app.db.postgres_manager.db import SessionLocal
from app.db.postgres_manager.managers.sessions import SessionManager
from app.db.postgres_manager.managers.messages import MessageManager
from app.db.postgres_manager.managers.users import UserManager
from app.db.postgres_manager.managers.groups import GroupManager
from app.db.postgres_manager.managers.group_participants import GroupParticipantManager
from app.db.postgres_manager.models.session import Session as SessionModel
from app.db.postgres_manager.models.user import User

logger = logging.getLogger(__name__)

class RedisPgSyncService:
    """Service for syncing Redis data to PostgreSQL"""
    
    def __init__(self):
        self.redis_client = redis_client
        self.sync_enabled = True
        self._pubsub = None
        
    async def start_sync_listener(self):
        """Start the Redis keyspace notification listener"""
        if not self.redis_client.is_connected():
            logger.error("Redis not connected, cannot start sync listener")
            return
            
        try:
            self.redis_client.redis_client.config_set('notify-keyspace-events', 'Ex')
            self._pubsub = self.redis_client.redis_client.pubsub()
            self._pubsub.psubscribe('__keyevent@0__:*', 'session_updated:*')
            logger.info("Started Redis keyspace notification listener")
            await self._listen_for_events()
        except Exception as e:
            logger.error(f"Failed to start sync listener: {e}")
    
    async def _listen_for_events(self):
        """Listen for Redis keyspace events and sync to PostgreSQL"""
        try:
            while self.sync_enabled:
                message = self._pubsub.get_message(timeout=1.0)
                if message and message['type'] == 'pmessage':
                    await self._handle_redis_event(message)
                await asyncio.sleep(0.1)  # Small delay to prevent busy waiting
        except Exception as e:
            logger.error(f"Error in event listener: {e}")
        finally:
            if self._pubsub:
                self._pubsub.close()
    
    async def _handle_redis_event(self, message: Dict[str, Any]):
        """Handle a Redis keyspace event and sync to PostgreSQL"""
        try:
            channel = message['channel'].decode('utf-8') if isinstance(message['channel'], bytes) else message['channel']
            data = message['data'].decode('utf-8') if isinstance(message['data'], bytes) else message['data']
            
            # Handle custom session update notifications
            if 'session_updated:' in channel:
                session_id = channel.split('session_updated:')[1]
                await self._sync_session_to_postgres(session_id)
            # Handle keyspace events for chat sessions
            elif 'chat:session:' in data:
                session_id = data.replace('chat:session:', '')
                if 'set' in channel or 'setex' in channel:
                    await self._sync_session_to_postgres(session_id)
                elif 'del' in channel or 'expired' in channel:
                    await self._handle_session_deletion(session_id)
        except Exception as e:
            logger.error(f"Error handling Redis event: {e}")
    
    async def _sync_session_to_postgres(self, session_id: str):
        """Sync a specific session from Redis to PostgreSQL"""
        try:
            session_data = self.redis_client.get_session(session_id)
            if not session_data:
                return
            
            db = SessionLocal()
            try:
                await self._ensure_user_exists(db, session_data)
                await self._ensure_group_exists(db, session_data)
                
                actual_session_id = await self._ensure_session_exists(db, session_id, session_data)
                if actual_session_id:
                    await self._sync_messages_to_postgres(db, session_id, session_data, actual_session_id)
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Error syncing session {session_id}: {e}")
    
    async def _sync_messages_to_postgres(self, db, session_id: str, session_data: Dict[str, Any], actual_session_id: int):
        """Sync messages from Redis to PostgreSQL"""
        try:
            messages = session_data.get('messages', [])
            existing_messages = MessageManager.get_messages_by_session(db, actual_session_id)
            existing_content = {msg.content for msg in existing_messages}
            
            # Get the group_id from session data or default
            group_id = session_data.get('group_id', 1)
            
            for message in messages:
                if isinstance(message, dict):
                    content = message.get('content', '')
                    sender_user_id = message.get('sender_id')  # This is still a user_id from Redis
                    timestamp = message.get('timestamp')  # Extract timestamp if available
                    
                    if content and sender_user_id and content not in existing_content:
                        # Convert user_id to group_participant_id
                        group_participant_id = self._ensure_group_participant_exists(db, group_id, sender_user_id)
                        
                        # Parse timestamp if it exists
                        sent_at = None
                        if timestamp:
                            try:
                                if isinstance(timestamp, str):
                                    sent_at = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                                elif isinstance(timestamp, datetime):
                                    sent_at = timestamp
                            except Exception as e:
                                logger.warning(f"Failed to parse timestamp '{timestamp}': {e}")
                        
                        MessageManager.create_message(
                            db, 
                            session_id=actual_session_id, 
                            sender_id=group_participant_id, 
                            content=content,
                            sent_at=sent_at
                        )
                        existing_content.add(content)
        except Exception as e:
            logger.error(f"Error syncing messages for session {session_id}: {e}")
    
    async def _ensure_user_exists(self, db, session_data: Dict[str, Any]):
        """Ensure user exists in PostgreSQL"""
        self._ensure_default_users(db)
        
        messages = session_data.get('messages', [])
        for message in messages:
            if isinstance(message, dict) and 'sender_id' in message:
                sender_user_id = message['sender_id']  # This is a user_id from Redis
                
                if not UserManager.get_user_by_id(db, sender_user_id):
                    user_data = {
                        1: ("user@default.com", "User"),
                        2: ("ai@assistant.com", "AI Assistant")
                    }
                    email, first_name = user_data.get(sender_user_id, (f"user_{sender_user_id}@temp.com", f"User{sender_user_id}"))
                    
                    # Check if user exists by email before creating
                    existing_user = UserManager.get_user_by_email(db, email)
                    if not existing_user:
                        UserManager.create_user(db, email=email, first_name=first_name)
    
    def _ensure_default_users(self, db):
        """Ensure default users (user=1, ai=2) exist in PostgreSQL"""
        try:
            # Check if specific default users exist by email first
            default_users = [
                ("user@default.com", "Default User"),
                ("ai@assistant.com", "AI Assistant")
            ]
            
            for email, first_name in default_users:
                existing_user = UserManager.get_user_by_email(db, email)
                if not existing_user:
                    try:
                        UserManager.create_user(db, email=email, first_name=first_name)
                        logger.info(f"Created default user: {email}")
                    except Exception as e:
                        # User might have been created by another process, check again
                        existing_user = UserManager.get_user_by_email(db, email)
                        if not existing_user:
                            logger.error(f"Failed to create user {email}: {e}")
                        else:
                            logger.info(f"User {email} exists (created by another process)")
                            
        except Exception as e:
            logger.error(f"Error ensuring default users: {e}")
    
    async def _ensure_group_exists(self, db, session_data: Dict[str, Any]):
        """Ensure group exists in PostgreSQL"""
        group_id = session_data.get('group_id', 1)
        if not GroupManager.get_group_by_id(db, group_id):
            # Get the first available user to create the group
            users = db.query(User).limit(1).all()
            if users:
                created_by = users[0].user_id
                GroupManager.create_group(db, name="Default Group", created_by=created_by)
                logger.info(f"Created default group with id {group_id}")
            else:
                logger.error("No users available to create default group")
    
    def _ensure_group_participant_exists(self, db, group_id: int, user_id: int) -> int:
        """Ensure group participant exists and return group_participant_id"""
        # First ensure the user exists
        user = UserManager.get_user_by_id(db, user_id)
        if not user:
            # Create user if it doesn't exist
            user_data = {
                1: ("user@default.com", "Default User"),
                2: ("ai@assistant.com", "AI Assistant")
            }
            email, first_name = user_data.get(user_id, (f"user_{user_id}@temp.com", f"User{user_id}"))
            
            # Check if user exists by email before creating
            existing_user = UserManager.get_user_by_email(db, email)
            if existing_user:
                user = existing_user
            else:
                user = UserManager.create_user(db, email=email, first_name=first_name)
                logger.info(f"Created user for group participant: user_id={user.user_id}, email={email}")
        
        # Now ensure group participant exists
        participant = GroupParticipantManager.get_participant_by_group_and_user(db, group_id, user.user_id)
        if not participant:
            participant = GroupParticipantManager.create_group_participant(db, group_id, user.user_id, role="member")
            logger.info(f"Created group participant: group_id={group_id}, user_id={user.user_id}, participant_id={participant.group_participant_id}")
        return participant.group_participant_id
    
    def _ensure_default_environment(self, db):
        """Ensure complete default environment: users, group, and group participants"""
        try:
            # Ensure default users exist
            self._ensure_default_users(db)
            
            # Ensure default group exists
            if not GroupManager.get_group_by_id(db, 1):
                users = db.query(User).limit(1).all()
                if users:
                    GroupManager.create_group(db, name="Default Group", created_by=users[0].user_id)
                    logger.info("Created default group")
            
            # Ensure default group participants exist for common user IDs
            group_id = 1
            all_users = db.query(User).all()
            for user in all_users:
                self._ensure_group_participant_exists(db, group_id, user.user_id)
                
        except Exception as e:
            logger.error(f"Error ensuring default environment: {e}")
    
    async def _ensure_session_exists(self, db, session_id: str, session_data: Dict[str, Any]):
        """Ensure session exists in PostgreSQL and return the actual session ID"""
        try:
            topic_identifier = f"Redis:{session_id}"
            existing_sessions = db.query(SessionModel).filter(SessionModel.topic.like(f"%{topic_identifier}%")).all()
            
            if existing_sessions:
                return existing_sessions[0].session_id
            
            # Ensure group and group participant exist
            group_id = session_data.get('group_id', 1)
            user_id = session_data.get('created_by', 1)
            group_participant_id = self._ensure_group_participant_exists(db, group_id, user_id)
            
            # Create new session
            topic = f"{session_data.get('topic', 'Chat Session')} ({topic_identifier})"
            started_at = datetime.now()
            if 'created_at' in session_data:
                try:
                    started_at = datetime.fromisoformat(session_data['created_at'])
                except:
                    pass
            
            new_session = SessionManager.create_session(
                db, 
                group_id=group_id, 
                created_by=group_participant_id,  # Now using group_participant_id
                topic=topic,
                started_at=started_at
            )
            return new_session.session_id
        except Exception as e:
            logger.error(f"Error ensuring session exists: {e}")
            return None
    
    async def _handle_session_deletion(self, session_id: str):
        """Handle session deletion"""
        logger.info(f"Session {session_id} deleted from Redis")
    
    async def manual_full_sync(self):
        """Manually sync all Redis data to PostgreSQL"""
        try:
            session_ids = self.redis_client.get_all_sessions()
            for session_id in session_ids:
                await self._sync_session_to_postgres(session_id)
            logger.info(f"Manual sync completed for {len(session_ids)} sessions")
        except Exception as e:
            logger.error(f"Error during manual full sync: {e}")
    
    def stop_sync(self):
        """Stop the sync service"""
        self.sync_enabled = False
        if self._pubsub:
            self._pubsub.close()
        logger.info("Redis-PostgreSQL sync service stopped")

# Global sync service instance
sync_service = RedisPgSyncService()
