from sqlalchemy.orm import Session
from app.db.postgres_manager.models.paper_tag import PaperTag

class PaperTagManager:
    @staticmethod
    def create_paper_tag(db: Session, paper_id: int, tag: str):
        paper_tag = PaperTag(paper_id=paper_id, tag=tag)
        db.add(paper_tag)
        db.commit()
        db.refresh(paper_tag)
        return paper_tag

    @staticmethod
    def get_tags_by_paper(db: Session, paper_id: int):
        return db.query(PaperTag).filter(PaperTag.paper_id == paper_id).all()

    @staticmethod
    def get_papers_by_tag(db: Session, tag: str):
        return db.query(PaperTag).filter(PaperTag.tag == tag).all()

    @staticmethod
    def delete_paper_tag(db: Session, paper_id: int, tag: str):
        paper_tag = db.query(PaperTag).filter(PaperTag.paper_id == paper_id, PaperTag.tag == tag).first()
        if paper_tag:
            db.delete(paper_tag)
            db.commit()
        return paper_tag
