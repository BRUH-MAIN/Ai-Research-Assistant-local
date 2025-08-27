from sqlalchemy.orm import Session
from app.db.postgres_manager.models.group_participant import GroupParticipant

class GroupParticipantManager:
    @staticmethod
    def create_group_participant(db: Session, group_id: int, user_id: int, role: str = None):
        participant = GroupParticipant(group_id=group_id, user_id=user_id, role=role)
        db.add(participant)
        db.commit()
        db.refresh(participant)
        return participant

    @staticmethod
    def get_group_participant_by_id(db: Session, group_participant_id: int):
        return db.query(GroupParticipant).filter(GroupParticipant.group_participant_id == group_participant_id).first()

    @staticmethod
    def get_participants_by_group(db: Session, group_id: int):
        return db.query(GroupParticipant).filter(GroupParticipant.group_id == group_id).all()

    @staticmethod
    def get_participant_by_group_and_user(db: Session, group_id: int, user_id: int):
        return db.query(GroupParticipant).filter(GroupParticipant.group_id == group_id, GroupParticipant.user_id == user_id).first()

    @staticmethod
    def update_group_participant(db: Session, group_participant_id: int, **kwargs):
        participant = db.query(GroupParticipant).filter(GroupParticipant.group_participant_id == group_participant_id).first()
        if not participant:
            return None
        for key, value in kwargs.items():
            setattr(participant, key, value)
        db.commit()
        db.refresh(participant)
        return participant

    @staticmethod
    def delete_group_participant(db: Session, group_participant_id: int):
        participant = db.query(GroupParticipant).filter(GroupParticipant.group_participant_id == group_participant_id).first()
        if participant:
            db.delete(participant)
            db.commit()
        return participant
