from sqlalchemy import Column, Integer, Text, TIMESTAMP, ForeignKey, UniqueConstraint
from .base import Base

class GroupParticipant(Base):
    __tablename__ = "group_participants"

    group_participant_id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("groups.group_id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    role = Column(Text)
    joined_at = Column(TIMESTAMP)

    __table_args__ = (UniqueConstraint('group_id', 'user_id'),)
