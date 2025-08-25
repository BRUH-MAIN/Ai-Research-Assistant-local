"""
Group endpoints router
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.postgres_manager.db import get_db
from app.db.postgres_manager.managers.groups import GroupManager
from app.db.postgres_manager.models.group import Group
from typing import List

router = APIRouter()

@router.get("/", response_model=List[Group])
def get_groups(db: Session = Depends(get_db)):
    return db.query(Group).all()

@router.get("/{group_id}", response_model=Group)
def get_group(group_id: int, db: Session = Depends(get_db)):
    group = GroupManager.get_group_by_id(db, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    return group

@router.post("/", response_model=Group)
def create_group(name: str, created_by: int, db: Session = Depends(get_db)):
    return GroupManager.create_group(db, name, created_by)

@router.delete("/{group_id}", response_model=Group)
def delete_group(group_id: int, db: Session = Depends(get_db)):
    group = GroupManager.delete_group(db, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    return group
