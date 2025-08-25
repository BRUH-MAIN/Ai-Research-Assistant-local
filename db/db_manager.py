import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2 import sql
import json
from datetime import datetime
from typing import List, Dict, Optional, Union
import uuid
from contextlib import contextmanager
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ChatDatabase:
    def __init__(self, database_url: Optional[str] = None):
        """Initialize database connection using URL from environment or parameter"""
        self.database_url = database_url or os.getenv('DATABASE_URL')
        
        if not self.database_url:
            raise ValueError("DATABASE_URL not found in environment variables or parameters")
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = None
        try:
            conn = psycopg2.connect(self.database_url)
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            if conn:
                conn.close()
    
    # SESSION MANAGEMENT
    def create_session(self) -> str:
        """Create a new chat session and return session_id"""
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO sessions (session_id) VALUES (DEFAULT) RETURNING session_id"
                )
                session_id = cursor.fetchone()[0]
                conn.commit()
                return str(session_id)
    
    def end_session(self, session_id: str) -> bool:
        """End a session by setting ended_at and is_active=False"""
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """UPDATE sessions 
                       SET ended_at = NOW(), is_active = FALSE 
                       WHERE session_id = %s AND is_active = TRUE""",
                    (session_id,)
                )
                rows_affected = cursor.rowcount
                conn.commit()
                return rows_affected > 0
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """Get session details"""
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    "SELECT * FROM sessions WHERE session_id = %s",
                    (session_id,)
                )
                result = cursor.fetchone()
                return dict(result) if result else None
    
    def get_active_sessions(self) -> List[Dict]:
        """Get all active sessions"""
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    "SELECT * FROM sessions WHERE is_active = TRUE ORDER BY started_at DESC"
                )
                return [dict(row) for row in cursor.fetchall()]
    
    # PARTICIPANT MANAGEMENT
    def add_participant(self, session_id: str, user_id: str, role: str = 'user') -> str:
        """Add a participant to a session"""
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """INSERT INTO session_participants (session_id, user_id, role) 
                       VALUES (%s, %s, %s) RETURNING participant_id""",
                    (session_id, user_id, role)
                )
                participant_id = cursor.fetchone()[0]
                conn.commit()
                return str(participant_id)
    
    def get_session_participants(self, session_id: str) -> List[Dict]:
        """Get all participants in a session"""
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    """SELECT * FROM session_participants 
                       WHERE session_id = %s ORDER BY joined_at""",
                    (session_id,)
                )
                return [dict(row) for row in cursor.fetchall()]
    
    def remove_participant(self, participant_id: str) -> bool:
        """Remove a participant from a session"""
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "DELETE FROM session_participants WHERE participant_id = %s",
                    (participant_id,)
                )
                rows_affected = cursor.rowcount
                conn.commit()
                return rows_affected > 0
    
    # MESSAGE MANAGEMENT
    def send_message(self, session_id: str, user_id: str, message_text: str, 
                    sender_role: str = 'user', metadata: Optional[Dict] = None) -> str:
        """Send a message in a session"""
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """INSERT INTO messages (session_id, user_id, sender_role, message_text, metadata) 
                       VALUES (%s, %s, %s, %s, %s) RETURNING message_id""",
                    (session_id, user_id, sender_role, message_text, 
                     json.dumps(metadata) if metadata else None)
                )
                message_id = cursor.fetchone()[0]
                conn.commit()
                return str(message_id)
    
    def get_messages(self, session_id: str, limit: Optional[int] = None, 
                    offset: int = 0) -> List[Dict]:
        """Get messages from a session with optional pagination"""
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                query = """SELECT * FROM messages 
                          WHERE session_id = %s 
                          ORDER BY created_at ASC"""
                params = [session_id]
                
                if limit:
                    query += " LIMIT %s OFFSET %s"
                    params.extend([limit, offset])
                
                cursor.execute(query, params)
                return [dict(row) for row in cursor.fetchall()]
    
    def get_message(self, message_id: str) -> Optional[Dict]:
        """Get a specific message by ID"""
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    "SELECT * FROM messages WHERE message_id = %s",
                    (message_id,)
                )
                result = cursor.fetchone()
                return dict(result) if result else None
    
    def delete_message(self, message_id: str) -> bool:
        """Delete a message"""
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "DELETE FROM messages WHERE message_id = %s",
                    (message_id,)
                )
                rows_affected = cursor.rowcount
                conn.commit()
                return rows_affected > 0
    
    def get_messages_by_user(self, user_id: str, session_id: Optional[str] = None) -> List[Dict]:
        """Get all messages from a specific user, optionally filtered by session"""
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                if session_id:
                    cursor.execute(
                        """SELECT * FROM messages 
                           WHERE user_id = %s AND session_id = %s 
                           ORDER BY created_at ASC""",
                        (user_id, session_id)
                    )
                else:
                    cursor.execute(
                        """SELECT * FROM messages 
                           WHERE user_id = %s 
                           ORDER BY created_at ASC""",
                        (user_id,)
                    )
                return [dict(row) for row in cursor.fetchall()]
    
    # CONVERSATION METADATA MANAGEMENT
    def update_conversation_summary(self, session_id: str, summary: str, 
                                   tags: Optional[List[str]] = None) -> bool:
        """Update or create conversation metadata"""
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """INSERT INTO conversation_metadata (session_id, summary, tags) 
                       VALUES (%s, %s, %s)
                       ON CONFLICT (session_id) 
                       DO UPDATE SET 
                           summary = EXCLUDED.summary,
                           tags = EXCLUDED.tags,
                           last_updated = NOW()""",
                    (session_id, summary, tags)
                )
                conn.commit()
                return True
    
    def get_conversation_metadata(self, session_id: str) -> Optional[Dict]:
        """Get conversation metadata"""
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    "SELECT * FROM conversation_metadata WHERE session_id = %s",
                    (session_id,)
                )
                result = cursor.fetchone()
                return dict(result) if result else None
    
    def search_conversations_by_tags(self, tags: List[str]) -> List[Dict]:
        """Search conversations by tags"""
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    """SELECT cm.*, s.started_at, s.ended_at, s.is_active
                       FROM conversation_metadata cm
                       JOIN sessions s ON cm.session_id = s.session_id
                       WHERE cm.tags && %s
                       ORDER BY cm.last_updated DESC""",
                    (tags,)
                )
                return [dict(row) for row in cursor.fetchall()]
    
    # UTILITY FUNCTIONS
    def get_session_stats(self, session_id: str) -> Dict:
        """Get statistics for a session"""
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    """SELECT 
                           COUNT(DISTINCT user_id) as unique_users,
                           COUNT(*) as total_messages,
                           MIN(created_at) as first_message,
                           MAX(created_at) as last_message
                       FROM messages 
                       WHERE session_id = %s""",
                    (session_id,)
                )
                return dict(cursor.fetchone())
    
    def get_user_sessions(self, user_id: str) -> List[Dict]:
        """Get all sessions a user has participated in"""
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    """SELECT DISTINCT s.*, sp.role, sp.joined_at
                       FROM sessions s
                       JOIN session_participants sp ON s.session_id = sp.session_id
                       WHERE sp.user_id = %s
                       ORDER BY s.started_at DESC""",
                    (user_id,)
                )
                return [dict(row) for row in cursor.fetchall()]

# Example usage and helper functions
