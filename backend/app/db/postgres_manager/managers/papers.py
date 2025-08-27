from sqlalchemy.orm import Session
from app.db.postgres_manager.models.paper import Paper

class PaperManager:
    @staticmethod
    def create_paper(db: Session, title: str, abstract: str = None, authors: str = None, doi: str = None, source_url: str = None):
        paper = Paper(title=title, abstract=abstract, authors=authors, doi=doi, source_url=source_url)
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
