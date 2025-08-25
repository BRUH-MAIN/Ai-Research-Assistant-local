from sqlalchemy import Column, Integer, Text, TIMESTAMP, ForeignKey
from .base import Base

class Session(Base):
    __tablename__ = "sessions"

    session_id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("groups.group_id", ondelete="CASCADE"), nullable=False)
    created_by = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    topic = Column(Text)
    started_at = Column(TIMESTAMP)
    ended_at = Column(TIMESTAMP)
