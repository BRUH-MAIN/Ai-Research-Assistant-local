"""
Redis queue wrapper using provided RedisClient
"""
from typing import List, Optional, Dict, Any
from app.db.redis_client import redis_client

class RedisQueue:
    def __init__(self):
        self.client = redis_client

    def get_all_sessions(self) -> List[str]:
        return self.client.get_all_sessions()

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        return self.client.get_session(session_id)

def flush_redis_messages_to_postgres(db):
    """
    Flush all messages from Redis sessions to Postgres using MessageManager.
    """
    from chat_backend.managers.messages import MessageManager
    redis_queue = RedisQueue()
    session_ids = redis_queue.get_all_sessions()
    inserted = []
    for session_id in session_ids:
        session = redis_queue.get_session(session_id)
        if not session:
            continue
        messages = session.get('messages', [])
        for msg in messages:
            content = msg.get('content') if isinstance(msg, dict) else str(msg)
            sender_id = msg.get('sender_id') if isinstance(msg, dict) else None
            if content and sender_id:
                inserted.append(MessageManager.create_message(db, session_id=session_id, sender_id=sender_id, content=content))
    return inserted
