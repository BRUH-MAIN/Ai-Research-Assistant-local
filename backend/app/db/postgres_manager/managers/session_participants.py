from sqlalchemy.orm import Session
from app.db.postgres_manager.models.session_participant import SessionParticipant

class SessionParticipantManager:
    @staticmethod
    def create_session_participant(db: Session, session_id: int, user_id: int):
        participant = SessionParticipant(session_id=session_id, user_id=user_id)
        db.add(participant)
        db.commit()
        db.refresh(participant)
        return participant

    @staticmethod
    def get_participants_by_session(db: Session, session_id: int):
        return db.query(SessionParticipant).filter(SessionParticipant.session_id == session_id).all()

    @staticmethod
    def get_participant_by_session_and_user(db: Session, session_id: int, user_id: int):
        return db.query(SessionParticipant).filter(SessionParticipant.session_id == session_id, SessionParticipant.user_id == user_id).first()

    @staticmethod
    def delete_session_participant(db: Session, session_id: int, user_id: int):
        participant = db.query(SessionParticipant).filter(SessionParticipant.session_id == session_id, SessionParticipant.user_id == user_id).first()
        if participant:
            db.delete(participant)
            db.commit()
        return participant
