from sqlalchemy.orm import Session
from chat_backend.models.message import Message
from chat_backend.redis_queue import RedisQueue

class MessageManager:
    @staticmethod
    def create_message(db: Session, session_id: int, sender_id: int, content: str):
        message = Message(session_id=session_id, sender_id=sender_id, content=content)
        db.add(message)
        db.commit()
        db.refresh(message)
        return message

    @staticmethod
    def get_message_by_id(db: Session, message_id: int):
        return db.query(Message).filter(Message.message_id == message_id).first()

    @staticmethod
    def get_messages_by_session(db: Session, session_id: int):
        return db.query(Message).filter(Message.session_id == session_id).all()

    @staticmethod
    def update_message(db: Session, message_id: int, **kwargs):
        message = db.query(Message).filter(Message.message_id == message_id).first()
        if not message:
            return None
        for key, value in kwargs.items():
            setattr(message, key, value)
        db.commit()
        db.refresh(message)
        return message

    @staticmethod
    def delete_message(db: Session, message_id: int):
        message = db.query(Message).filter(Message.message_id == message_id).first()
        if message:
            db.delete(message)
            db.commit()
        return message

    @staticmethod
    def flush_from_redis(db: Session):
        """
        Fetch all sessions and their messages from Redis and insert into Postgres.
        Uses the provided RedisClient for connection and format.
        """
        from chat_backend.redis_queue import RedisQueue
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
