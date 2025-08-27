from sqlalchemy.orm import Session
from app.db.postgres_manager.models.session_paper import SessionPaper

class SessionPaperManager:
    @staticmethod
    def create_session_paper(db: Session, session_id: int, paper_id: int):
        session_paper = SessionPaper(session_id=session_id, paper_id=paper_id)
        db.add(session_paper)
        db.commit()
        db.refresh(session_paper)
        return session_paper

    @staticmethod
    def get_papers_by_session(db: Session, session_id: int):
        return db.query(SessionPaper).filter(SessionPaper.session_id == session_id).all()

    @staticmethod
    def get_sessions_by_paper(db: Session, paper_id: int):
        return db.query(SessionPaper).filter(SessionPaper.paper_id == paper_id).all()

    @staticmethod
    def get_session_paper(db: Session, session_id: int, paper_id: int):
        return db.query(SessionPaper).filter(SessionPaper.session_id == session_id, SessionPaper.paper_id == paper_id).first()

    @staticmethod
    def delete_session_paper(db: Session, session_id: int, paper_id: int):
        session_paper = db.query(SessionPaper).filter(SessionPaper.session_id == session_id, SessionPaper.paper_id == paper_id).first()
        if session_paper:
            db.delete(session_paper)
            db.commit()
        return session_paper
