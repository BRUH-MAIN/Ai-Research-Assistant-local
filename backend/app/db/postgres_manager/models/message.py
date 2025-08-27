from sqlalchemy import Column, Integer, Text, TIMESTAMP, ForeignKey, func
from .base import Base

class Message(Base):
    __tablename__ = "messages"

    message_id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.session_id", ondelete="CASCADE"), nullable=False)
    sender_id = Column(Integer, ForeignKey("group_participants.group_participant_id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)
    sent_at = Column(TIMESTAMP, default=func.current_timestamp())
