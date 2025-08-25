from sqlalchemy import Column, Integer, Text, TIMESTAMP, ForeignKey
from .base import Base

class Group(Base):
    __tablename__ = "groups"

    group_id = Column(Integer, primary_key=True, index=True)
    name = Column(Text, nullable=False)
    created_by = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    created_at = Column(TIMESTAMP)
