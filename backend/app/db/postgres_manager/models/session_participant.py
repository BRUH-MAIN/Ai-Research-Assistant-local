from sqlalchemy import Column, Integer, TIMESTAMP, ForeignKey, UniqueConstraint
from .base import Base

class SessionParticipant(Base):
    __tablename__ = "session_participants"

    session_id = Column(Integer, ForeignKey("sessions.session_id", ondelete="CASCADE"), nullable=False, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, primary_key=True)
    joined_at = Column(TIMESTAMP)

    __table_args__ = (UniqueConstraint('session_id', 'user_id'),)
