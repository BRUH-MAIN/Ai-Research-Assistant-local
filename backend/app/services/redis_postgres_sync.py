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
from app.db.postgres_manager.models.session import Session as SessionModel

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
            # Enable keyspace notifications in Redis
            self.redis_client.redis_client.config_set('notify-keyspace-events', 'Ex')
            
            # Set up pub/sub for keyspace notifications and custom session updates
            self._pubsub = self.redis_client.redis_client.pubsub()
            self._pubsub.psubscribe('__keyevent@0__:*')
            self._pubsub.psubscribe('session_updated:*')
            
            logger.info("Started Redis keyspace notification listener")
            
            # Listen for events
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
            # Handle different message formats
            channel = message['channel']
            data = message['data']
            
            # Decode bytes to string if necessary
            if isinstance(channel, bytes):
                channel = channel.decode('utf-8')
            if isinstance(data, bytes):
                data = data.decode('utf-8')
            
            logger.debug(f"Redis event - Channel: {channel}, Data: {data}")
            
            # Handle custom session update notifications
            if 'session_updated:' in channel:
                # Extract session_id from channel name
                session_id = channel.split('session_updated:')[1]
                logger.info(f"Session update notification for: {session_id}")
                await self._sync_session_to_postgres(session_id)
                return
            
            # Handle keyspace events
            if 'chat:session:' in data:
                session_id = data.replace('chat:session:', '')
                logger.info(f"Keyspace event for session: {session_id}")
                
                # Handle different event types
                if 'set' in channel or 'setex' in channel:
                    await self._sync_session_to_postgres(session_id)
                elif 'del' in channel or 'expired' in channel:
                    await self._handle_session_deletion(session_id)
            else:
                logger.debug(f"Ignoring Redis event: {channel} - {data}")
                    
        except Exception as e:
            logger.error(f"Error handling Redis event: {e}")
            logger.debug(f"Event details - Channel: {message.get('channel')}, Data: {message.get('data')}")
    
    async def _sync_session_to_postgres(self, session_id: str):
        """Sync a specific session from Redis to PostgreSQL"""
        try:
            # Get session data from Redis
            session_data = self.redis_client.get_session(session_id)
            if not session_data:
                logger.warning(f"Session {session_id} not found in Redis")
                return
            
            db = SessionLocal()
            try:
                # Ensure required entities exist
                await self._ensure_user_exists(db, session_data)
                await self._ensure_group_exists(db, session_data)
                
                # Ensure session exists and get the actual PostgreSQL session ID
                actual_session_id = await self._ensure_session_exists(db, session_id, session_data)
                if actual_session_id is None:
                    logger.error(f"Failed to create/find session for {session_id}")
                    return
                
                # Sync messages using the actual session ID
                await self._sync_session_messages(db, session_id, session_data, actual_session_id)
                
                logger.info(f"Successfully synced session {session_id} to PostgreSQL session {actual_session_id}")
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error syncing session {session_id} to PostgreSQL: {e}")
    
    async def _sync_session_messages(self, db, session_id: str, session_data: Dict[str, Any], actual_session_id: int):
        """Sync messages from Redis session to PostgreSQL using the actual session ID"""
        try:
            messages = session_data.get('messages', [])
            
            # Get existing messages to avoid duplicates
            existing_messages = MessageManager.get_messages_by_session(db, actual_session_id)
            existing_content = {msg.content for msg in existing_messages}
            
            for message in messages:
                if isinstance(message, dict):
                    content = message.get('content', '')
                    sender_id = message.get('sender_id')
                    
                    # Skip if message already exists (simple content-based deduplication)
                    if content in existing_content:
                        continue
                    
                    if content and sender_id:
                        MessageManager.create_message(
                            db, 
                            session_id=actual_session_id,  # Use the actual PostgreSQL session ID
                            sender_id=sender_id, 
                            content=content
                        )
                        existing_content.add(content)
                        logger.debug(f"Added message to PostgreSQL session {actual_session_id}")
                        
        except Exception as e:
            logger.error(f"Error syncing messages for session {session_id}: {e}")
    
    async def _ensure_user_exists(self, db, session_data: Dict[str, Any]):
        """Ensure user exists in PostgreSQL"""
        # First, ensure default users exist (user=1, ai=2)
        self._ensure_default_users(db)
        
        # Extract user info from session data messages
        messages = session_data.get('messages', [])
        for message in messages:
            if isinstance(message, dict) and 'sender_id' in message:
                sender_id = message['sender_id']
                
                # Check if user exists
                existing_user = UserManager.get_user_by_id(db, sender_id)
                if not existing_user:
                    # Create user with basic info
                    if sender_id == 1:
                        email = "user@default.com"
                        first_name = "User"
                    elif sender_id == 2:
                        email = "ai@assistant.com"
                        first_name = "AI Assistant"
                    else:
                        email = f"user_{sender_id}@temp.com"
                        first_name = f"User{sender_id}"
                    
                    UserManager.create_user(db, email=email, password_hash="temp", first_name=first_name)
                    logger.info(f"Created user {sender_id} in PostgreSQL")
    
    def _ensure_default_users(self, db):
        """Ensure default users (user=1, ai=2) exist in PostgreSQL"""
        try:
            # Check if user with ID 1 exists
            user_1 = UserManager.get_user_by_id(db, 1)
            if not user_1:
                UserManager.create_user(db, email="user@default.com", password_hash="temp", first_name="Default User")
                logger.info("Created default user (ID: 1) in PostgreSQL")
            
            # Check if user with ID 2 exists
            user_2 = UserManager.get_user_by_id(db, 2)
            if not user_2:
                UserManager.create_user(db, email="ai@assistant.com", password_hash="temp", first_name="AI Assistant")
                logger.info("Created AI user (ID: 2) in PostgreSQL")
                
        except Exception as e:
            logger.error(f"Error ensuring default users: {e}")
    
    async def _ensure_group_exists(self, db, session_data: Dict[str, Any]):
        """Ensure group exists in PostgreSQL"""
        # For now, create a default group if none exists
        group_id = session_data.get('group_id', 1)
        
        existing_group = GroupManager.get_group_by_id(db, group_id)
        if not existing_group:
            # Create default group
            created_by = session_data.get('created_by', 1)
            GroupManager.create_group(db, name="Default Group", created_by=created_by)
            logger.info(f"Created group {group_id} in PostgreSQL")
    
    async def _ensure_session_exists(self, db, session_id: str, session_data: Dict[str, Any]):
        """Ensure session exists in PostgreSQL and return the actual session ID"""
        try:
            # Convert string session_id to int for lookup (but this might not be the final ID)
            session_id_hash = hash(session_id) % (2**31)  # This is just for identification
            
            # Try to find existing session by a custom identifier or create new one
            # Since we can't control the session_id, we'll store it in the topic field for identification
            topic_identifier = f"Redis:{session_id}"
            
            # Look for existing session by topic identifier
            existing_sessions = db.query(SessionModel).filter(SessionModel.topic.like(f"%Redis:{session_id}%")).all()
            
            if existing_sessions:
                actual_session_id = existing_sessions[0].session_id
                logger.info(f"Found existing session for Redis {session_id} -> PostgreSQL {actual_session_id}")
                return actual_session_id
            else:
                # Create new session
                group_id = session_data.get('group_id', 1)
                created_by = session_data.get('created_by', 1)
                topic = session_data.get('topic', 'Chat Session')
                
                # Add Redis identifier to topic for future lookups
                topic_with_id = f"{topic} (Redis:{session_id})"
                
                # Parse timestamps if available
                started_at = None
                if 'created_at' in session_data:
                    try:
                        started_at = datetime.fromisoformat(session_data['created_at'])
                    except:
                        started_at = datetime.now()
                else:
                    started_at = datetime.now()
                
                # Create session and get the actual PostgreSQL session ID
                new_session = SessionManager.create_session(
                    db, 
                    group_id=group_id, 
                    created_by=created_by, 
                    topic=topic_with_id,
                    started_at=started_at
                )
                
                actual_session_id = new_session.session_id
                logger.info(f"Created session Redis {session_id} -> PostgreSQL {actual_session_id}")
                return actual_session_id
                
        except Exception as e:
            logger.error(f"Error ensuring session exists: {e}")
            return None
    
    async def _handle_session_deletion(self, session_id: str):
        """Handle session deletion (optional - you may want to keep data in PostgreSQL)"""
        logger.info(f"Session {session_id} was deleted from Redis")
        # Optionally mark session as ended in PostgreSQL instead of deleting
        # This preserves historical data
    
    async def manual_full_sync(self):
        """Manually sync all Redis data to PostgreSQL"""
        logger.info("Starting manual full sync from Redis to PostgreSQL")
        
        try:
            session_ids = self.redis_client.get_all_sessions()
            logger.info(f"Found {len(session_ids)} sessions to sync")
            
            for session_id in session_ids:
                await self._sync_session_to_postgres(session_id)
                
            logger.info("Manual full sync completed")
            
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
