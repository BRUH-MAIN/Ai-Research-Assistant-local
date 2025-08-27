from sqlalchemy import Column, Integer, Text, TIMESTAMP, ForeignKey
from .base import Base

class Feedback(Base):
    __tablename__ = "feedback"

    session_id = Column(Integer, ForeignKey("sessions.session_id", ondelete="CASCADE"), nullable=False, primary_key=True)
    given_by = Column(Integer, ForeignKey("group_participants.group_participant_id", ondelete="CASCADE"), nullable=False, primary_key=True)
    content = Column(Text)
    created_at = Column(TIMESTAMP)
