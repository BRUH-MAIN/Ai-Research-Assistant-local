"""
Feedback endpoints router
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.postgres_manager.db import get_db
from app.db.postgres_manager.managers.feedback import FeedbackManager
from app.db.postgres_manager.models.feedback import Feedback
from app.db.postgres_manager.models.feedback_schema import FeedbackSchema
from typing import List

router = APIRouter()

@router.get("/", response_model=List[FeedbackSchema])
def get_feedback(db: Session = Depends(get_db)):
    feedbacks = db.query(Feedback).all()
    return [FeedbackSchema.from_orm(feedback) for feedback in feedbacks]

@router.get("/{feedback_id}", response_model=FeedbackSchema)
def get_feedback_by_id(feedback_id: int, db: Session = Depends(get_db)):
    feedback = FeedbackManager.get_feedback_by_id(db, feedback_id)
    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")
    return FeedbackSchema.from_orm(feedback)

@router.post("/", response_model=FeedbackSchema)
def create_feedback(session_id: int, given_by: int, content: str, db: Session = Depends(get_db)):
    feedback = FeedbackManager.create_feedback(db, session_id, given_by, content)
    return FeedbackSchema.from_orm(feedback)

@router.delete("/{feedback_id}", response_model=FeedbackSchema)
def delete_feedback(feedback_id: int, db: Session = Depends(get_db)):
    feedback = FeedbackManager.delete_feedback(db, feedback_id)
    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")
    return FeedbackSchema.from_orm(feedback)
