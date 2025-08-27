from sqlalchemy import Column, Integer, VARCHAR, ForeignKey
from .base import Base

class PaperTag(Base):
    __tablename__ = "paper_tags"

    paper_id = Column(Integer, ForeignKey("papers.paper_id", ondelete="CASCADE"), nullable=False, primary_key=True)
    tag = Column(VARCHAR(100), nullable=False, primary_key=True)
