from sqlalchemy import Column, Integer, Text, TIMESTAMP
from .base import Base

class Paper(Base):
    __tablename__ = "papers"

    paper_id = Column(Integer, primary_key=True, index=True)
    title = Column(Text, nullable=False)
    abstract = Column(Text)
    authors = Column(Text)
    doi = Column(Text, unique=True)
    published_at = Column(TIMESTAMP)
    source_url = Column(Text)
