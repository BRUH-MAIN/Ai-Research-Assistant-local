"""
User endpoints router
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.postgres_manager.db import get_db
from app.db.postgres_manager.managers.users import UserManager
from app.db.postgres_manager.models.user import User
from typing import List

router = APIRouter()

@router.get("/", response_model=List[User])
def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()

@router.get("/{user_id}", response_model=User)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = UserManager.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/", response_model=User)
def create_user(email: str, password_hash: str, first_name: str = None, last_name: str = None, role: str = None, db: Session = Depends(get_db)):
    return UserManager.create_user(db, email, password_hash, first_name, last_name, role)

@router.delete("/{user_id}", response_model=User)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = UserManager.delete_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
