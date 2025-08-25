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
            channel = message['channel'].decode('utf-8')
            data = message['data'].decode('utf-8')
            
            # Handle custom session update notifications
            if 'session_updated:' in channel:
                session_id = data
                await self._sync_session_to_postgres(session_id)
                return
            
            # Handle keyspace events
            if 'chat:session:' in data:
                session_id = data.replace('chat:session:', '')
                
                # Handle different event types
                if 'set' in channel or 'setex' in channel:
                    await self._sync_session_to_postgres(session_id)
                elif 'del' in channel or 'expired' in channel:
                    await self._handle_session_deletion(session_id)
                    
        except Exception as e:
            logger.error(f"Error handling Redis event: {e}")
    
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
                await self._ensure_session_exists(db, session_id, session_data)
                
                # Sync messages
                await self._sync_session_messages(db, session_id, session_data)
                
                logger.info(f"Successfully synced session {session_id} to PostgreSQL")
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error syncing session {session_id} to PostgreSQL: {e}")
    
    async def _ensure_user_exists(self, db, session_data: Dict[str, Any]):
        """Ensure user exists in PostgreSQL"""
        # Extract user info from session data
        messages = session_data.get('messages', [])
        for message in messages:
            if isinstance(message, dict) and 'sender_id' in message:
                sender_id = message['sender_id']
                
                # Check if user exists
                existing_user = UserManager.get_user_by_id(db, sender_id)
                if not existing_user:
                    # Create user with basic info
                    email = f"user_{sender_id}@temp.com"
                    UserManager.create_user(db, email=email, password_hash="temp", first_name=f"User{sender_id}")
                    logger.info(f"Created user {sender_id} in PostgreSQL")
    
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
        """Ensure session exists in PostgreSQL"""
        try:
            # Convert string session_id to int if needed
            session_id_int = int(session_id) if session_id.isdigit() else hash(session_id) % (2**31)
            
            existing_session = SessionManager.get_session_by_id(db, session_id_int)
            if not existing_session:
                # Create session
                group_id = session_data.get('group_id', 1)
                created_by = session_data.get('created_by', 1)
                topic = session_data.get('topic', 'Chat Session')
                
                # Parse timestamps if available
                started_at = None
                if 'created_at' in session_data:
                    try:
                        started_at = datetime.fromisoformat(session_data['created_at'])
                    except:
                        started_at = datetime.now()
                
                SessionManager.create_session(
                    db, 
                    group_id=group_id, 
                    created_by=created_by, 
                    topic=topic,
                    started_at=started_at
                )
                logger.info(f"Created session {session_id_int} in PostgreSQL")
        except Exception as e:
            logger.error(f"Error ensuring session exists: {e}")
    
    async def _sync_session_messages(self, db, session_id: str, session_data: Dict[str, Any]):
        """Sync messages from Redis session to PostgreSQL"""
        try:
            session_id_int = int(session_id) if session_id.isdigit() else hash(session_id) % (2**31)
            messages = session_data.get('messages', [])
            
            # Get existing messages to avoid duplicates
            existing_messages = MessageManager.get_messages_by_session(db, session_id_int)
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
                            session_id=session_id_int, 
                            sender_id=sender_id, 
                            content=content
                        )
                        existing_content.add(content)
                        logger.debug(f"Added message to session {session_id_int}")
                        
        except Exception as e:
            logger.error(f"Error syncing messages for session {session_id}: {e}")
    
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
