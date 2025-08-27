from sqlalchemy import Column, Integer, TIMESTAMP, ForeignKey, UniqueConstraint
from .base import Base

class SessionPaper(Base):
    __tablename__ = "session_papers"

    session_id = Column(Integer, ForeignKey("sessions.session_id", ondelete="CASCADE"), nullable=False, primary_key=True)
    paper_id = Column(Integer, ForeignKey("papers.paper_id", ondelete="CASCADE"), nullable=False, primary_key=True)
    added_at = Column(TIMESTAMP)

    __table_args__ = (UniqueConstraint('session_id', 'paper_id'),)
