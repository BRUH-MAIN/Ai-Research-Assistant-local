from sqlalchemy.orm import Session
from app.db.postgres_manager.models.feedback import Feedback

class FeedbackManager:
    @staticmethod
    def create_feedback(db: Session, session_id: int, given_by: int, content: str):
        feedback = Feedback(session_id=session_id, given_by=given_by, content=content)
        db.add(feedback)
        db.commit()
        db.refresh(feedback)
        return feedback

    @staticmethod
    def get_feedback_by_session_and_user(db: Session, session_id: int, given_by: int):
        return db.query(Feedback).filter(Feedback.session_id == session_id, Feedback.given_by == given_by).first()

    @staticmethod
    def get_feedback_by_session(db: Session, session_id: int):
        return db.query(Feedback).filter(Feedback.session_id == session_id).all()

    @staticmethod
    def update_feedback(db: Session, session_id: int, given_by: int, **kwargs):
        feedback = db.query(Feedback).filter(Feedback.session_id == session_id, Feedback.given_by == given_by).first()
        if not feedback:
            return None
        for key, value in kwargs.items():
            setattr(feedback, key, value)
        db.commit()
        db.refresh(feedback)
        return feedback

    @staticmethod
    def delete_feedback(db: Session, session_id: int, given_by: int):
        feedback = db.query(Feedback).filter(Feedback.session_id == session_id, Feedback.given_by == given_by).first()
        if feedback:
            db.delete(feedback)
            db.commit()
        return feedback
