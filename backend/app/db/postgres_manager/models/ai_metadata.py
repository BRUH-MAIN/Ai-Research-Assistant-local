from sqlalchemy import Column, Integer, TIMESTAMP, ForeignKey
from .base import Base

class AiMetadata(Base):
    __tablename__ = "ai_metadata"

    page_no = Column(Integer)
    message_id = Column(Integer, ForeignKey("messages.message_id", ondelete="CASCADE"), nullable=False, primary_key=True)
    paper_id = Column(Integer, ForeignKey("papers.paper_id", ondelete="CASCADE"), nullable=False, primary_key=True)
    created_at = Column(TIMESTAMP)
