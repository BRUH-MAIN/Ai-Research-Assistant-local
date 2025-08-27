from sqlalchemy.orm import Session
from app.db.postgres_manager.models.ai_metadata import AiMetadata

class AiMetadataManager:
    @staticmethod
    def create_ai_metadata(db: Session, message_id: int, paper_id: int, page_no: int = None):
        ai_metadata = AiMetadata(message_id=message_id, paper_id=paper_id, page_no=page_no)
        db.add(ai_metadata)
        db.commit()
        db.refresh(ai_metadata)
        return ai_metadata

    @staticmethod
    def get_metadata_by_message(db: Session, message_id: int):
        return db.query(AiMetadata).filter(AiMetadata.message_id == message_id).all()

    @staticmethod
    def get_metadata_by_paper(db: Session, paper_id: int):
        return db.query(AiMetadata).filter(AiMetadata.paper_id == paper_id).all()

    @staticmethod
    def get_metadata_by_message_and_paper(db: Session, message_id: int, paper_id: int):
        return db.query(AiMetadata).filter(AiMetadata.message_id == message_id, AiMetadata.paper_id == paper_id).first()

    @staticmethod
    def update_ai_metadata(db: Session, message_id: int, paper_id: int, **kwargs):
        ai_metadata = db.query(AiMetadata).filter(AiMetadata.message_id == message_id, AiMetadata.paper_id == paper_id).first()
        if not ai_metadata:
            return None
        for key, value in kwargs.items():
            setattr(ai_metadata, key, value)
        db.commit()
        db.refresh(ai_metadata)
        return ai_metadata

    @staticmethod
    def delete_ai_metadata(db: Session, message_id: int, paper_id: int):
        ai_metadata = db.query(AiMetadata).filter(AiMetadata.message_id == message_id, AiMetadata.paper_id == paper_id).first()
        if ai_metadata:
            db.delete(ai_metadata)
            db.commit()
        return ai_metadata
