"""
Message endpoints router
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.postgres_manager.db import get_db
from app.db.postgres_manager.managers.messages import MessageManager
from app.db.postgres_manager.models.message import Message
from typing import List

router = APIRouter()

@router.get("/", response_model=List[Message])
def get_messages(db: Session = Depends(get_db)):
    return db.query(Message).all()

@router.get("/{message_id}", response_model=Message)
def get_message(message_id: int, db: Session = Depends(get_db)):
    message = MessageManager.get_message_by_id(db, message_id)
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    return message

@router.post("/", response_model=Message)
def create_message(session_id: int, sender_id: int, content: str, db: Session = Depends(get_db)):
    return MessageManager.create_message(db, session_id, sender_id, content)

@router.delete("/{message_id}", response_model=Message)
def delete_message(message_id: int, db: Session = Depends(get_db)):
    message = MessageManager.delete_message(db, message_id)
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    return message
