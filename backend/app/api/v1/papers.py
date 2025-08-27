"""
Papers endpoints router
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.postgres_manager.db import get_db
from app.db.postgres_manager.managers.papers import PaperManager
from app.db.postgres_manager.models.paper import Paper
from app.db.postgres_manager.schemas import PaperRead as PaperSchema
from typing import List

router = APIRouter()

@router.get("/", response_model=List[PaperSchema])
def get_papers(db: Session = Depends(get_db)):
    papers = db.query(Paper).all()
    return [PaperSchema.model_validate(paper) for paper in papers]

@router.get("/{paper_id}", response_model=PaperSchema)
def get_paper(paper_id: int, db: Session = Depends(get_db)):
    paper = PaperManager.get_paper_by_id(db, paper_id)
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    return PaperSchema.model_validate(paper)

@router.get("/doi/{doi}", response_model=PaperSchema)
def get_paper_by_doi(doi: str, db: Session = Depends(get_db)):
    paper = PaperManager.get_paper_by_doi(db, doi)
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    return PaperSchema.model_validate(paper)

@router.post("/", response_model=PaperSchema)
def create_paper(title: str, abstract: str = None, authors: str = None, doi: str = None, source_url: str = None, db: Session = Depends(get_db)):
    paper = PaperManager.create_paper(db, title, abstract, authors, doi, source_url)
    return PaperSchema.model_validate(paper)

@router.delete("/{paper_id}", response_model=PaperSchema)
def delete_paper(paper_id: int, db: Session = Depends(get_db)):
    paper = PaperManager.delete_paper(db, paper_id)
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    return PaperSchema.model_validate(paper)
