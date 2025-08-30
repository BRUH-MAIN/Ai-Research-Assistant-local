from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_
from app.db.postgres_manager.models.paper import Paper
from app.db.postgres_manager.models.paper_tag import PaperTag
from typing import List, Optional
from datetime import datetime

class PaperManager:
    @staticmethod
    def create_paper(db: Session, title: str, abstract: str = None, authors: str = None, doi: str = None, source_url: str = None, published_at: datetime = None):
        paper = Paper(
            title=title, 
            abstract=abstract, 
            authors=authors, 
            doi=doi, 
            source_url=source_url,
            published_at=published_at
        )
        db.add(paper)
        db.commit()
        db.refresh(paper)
        return paper

    @staticmethod
    def get_paper_by_id(db: Session, paper_id: int):
        return db.query(Paper).filter(Paper.paper_id == paper_id).first()

    @staticmethod
    def get_paper_by_doi(db: Session, doi: str):
        return db.query(Paper).filter(Paper.doi == doi).first()

    @staticmethod
    def get_papers_by_title(db: Session, title: str):
        return db.query(Paper).filter(Paper.title.ilike(f"%{title}%")).all()

    @staticmethod
    def search_papers_by_name_and_tags(db: Session, name: Optional[str] = None, tags: Optional[List[str]] = None) -> List[Paper]:
        """
        Search papers by name (title/authors) and tags
        
        Args:
            db: Database session
            name: Search term for title or authors
            tags: List of tags to filter by
            
        Returns:
            List of matching papers
        """
        query = db.query(Paper)
        
        conditions = []
        
        # Search in title and authors if name is provided
        if name:
            name_condition = or_(
                Paper.title.ilike(f"%{name}%"),
                Paper.authors.ilike(f"%{name}%")
            )
            conditions.append(name_condition)
        
        # Filter by tags if provided
        if tags:
            # Join with paper_tags table
            query = query.join(PaperTag, Paper.paper_id == PaperTag.paper_id)
            tag_condition = PaperTag.tag.in_(tags)
            conditions.append(tag_condition)
        
        # Apply all conditions
        if conditions:
            query = query.filter(and_(*conditions))
        
        # Remove duplicates if joining with tags
        if tags:
            query = query.distinct()
        
        return query.all()

    @staticmethod
    def get_paper_with_tags(db: Session, paper_id: int):
        """Get paper with its associated tags"""
        paper = db.query(Paper).filter(Paper.paper_id == paper_id).first()
        if paper:
            tags = db.query(PaperTag.tag).filter(PaperTag.paper_id == paper_id).all()
            return paper, [tag[0] for tag in tags]
        return None, []

    @staticmethod
    def add_tags_to_paper(db: Session, paper_id: int, tags: List[str]):
        """Add tags to a paper"""
        for tag in tags:
            # Check if tag already exists
            existing = db.query(PaperTag).filter(
                and_(PaperTag.paper_id == paper_id, PaperTag.tag == tag)
            ).first()
            
            if not existing:
                paper_tag = PaperTag(paper_id=paper_id, tag=tag)
                db.add(paper_tag)
        
        db.commit()

    @staticmethod
    def update_paper(db: Session, paper_id: int, **kwargs):
        paper = db.query(Paper).filter(Paper.paper_id == paper_id).first()
        if not paper:
            return None
        for key, value in kwargs.items():
            setattr(paper, key, value)
        db.commit()
        db.refresh(paper)
        return paper

    @staticmethod
    def delete_paper(db: Session, paper_id: int):
        paper = db.query(Paper).filter(Paper.paper_id == paper_id).first()
        if paper:
            db.delete(paper)
            db.commit()
        return paper
