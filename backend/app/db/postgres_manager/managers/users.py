from sqlalchemy.orm import Session
from app.db.postgres_manager.models.user import User

class UserManager:
    @staticmethod
    def create_user(db: Session, email: str, password_hash: str, first_name: str = None, last_name: str = None, role: str = None):
        user = User(email=email, password_hash=password_hash, first_name=first_name, last_name=last_name, role=role)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def get_user_by_email(db: Session, email: str):
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def get_user_by_id(db: Session, user_id: int):
        return db.query(User).filter(User.user_id == user_id).first()

    @staticmethod
    def update_user(db: Session, user_id: int, **kwargs):
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            return None
        for key, value in kwargs.items():
            if key == "password_hash":
                continue  # Do not update password here
            setattr(user, key, value)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def delete_user(db: Session, user_id: int):
        user = db.query(User).filter(User.user_id == user_id).first()
        if user:
            db.delete(user)
            db.commit()
        return user
