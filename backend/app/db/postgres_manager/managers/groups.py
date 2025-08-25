from sqlalchemy.orm import Session
from chat_backend.models.group import Group

class GroupManager:
    @staticmethod
    def create_group(db: Session, name: str, created_by: int):
        group = Group(name=name, created_by=created_by)
        db.add(group)
        db.commit()
        db.refresh(group)
        return group

    @staticmethod
    def get_group_by_id(db: Session, group_id: int):
        return db.query(Group).filter(Group.group_id == group_id).first()

    @staticmethod
    def get_groups_by_user(db: Session, user_id: int):
        return db.query(Group).filter(Group.created_by == user_id).all()

    @staticmethod
    def update_group(db: Session, group_id: int, **kwargs):
        group = db.query(Group).filter(Group.group_id == group_id).first()
        if not group:
            return None
        for key, value in kwargs.items():
            setattr(group, key, value)
        db.commit()
        db.refresh(group)
        return group

    @staticmethod
    def delete_group(db: Session, group_id: int):
        group = db.query(Group).filter(Group.group_id == group_id).first()
        if group:
            db.delete(group)
            db.commit()
        return group
