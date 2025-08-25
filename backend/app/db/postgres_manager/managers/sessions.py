from sqlalchemy.orm import Session
from chat_backend.models.session import Session as SessionModel

class SessionManager:
    @staticmethod
    def create_session(db: Session, group_id: int, created_by: int, topic: str = None, started_at=None, ended_at=None):
        session = SessionModel(group_id=group_id, created_by=created_by, topic=topic, started_at=started_at, ended_at=ended_at)
        db.add(session)
        db.commit()
        db.refresh(session)
        return session

    @staticmethod
    def get_session_by_id(db: Session, session_id: int):
        return db.query(SessionModel).filter(SessionModel.session_id == session_id).first()

    @staticmethod
    def get_sessions_by_group(db: Session, group_id: int):
        return db.query(SessionModel).filter(SessionModel.group_id == group_id).all()

    @staticmethod
    def update_session(db: Session, session_id: int, **kwargs):
        session = db.query(SessionModel).filter(SessionModel.session_id == session_id).first()
        if not session:
            return None
        for key, value in kwargs.items():
            setattr(session, key, value)
        db.commit()
        db.refresh(session)
        return session

    @staticmethod
    def delete_session(db: Session, session_id: int):
        session = db.query(SessionModel).filter(SessionModel.session_id == session_id).first()
        if session:
            db.delete(session)
            db.commit()
        return session
