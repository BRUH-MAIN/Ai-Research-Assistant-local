from sqlalchemy import Column, Integer, Text, TIMESTAMP, ForeignKey
from .base import Base

class Feedback(Base):
    __tablename__ = "feedback"

    feedback_id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.session_id", ondelete="CASCADE"), nullable=False)
    given_by = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    content = Column(Text)
    created_at = Column(TIMESTAMP)
