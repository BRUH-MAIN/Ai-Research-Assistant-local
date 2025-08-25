from sqlalchemy import Column, Integer, Text, TIMESTAMP
from .base import Base

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    email = Column(Text, unique=True, nullable=False)
    password_hash = Column(Text, nullable=False)
    first_name = Column(Text)
    last_name = Column(Text)
    role = Column(Text)
    created_at = Column(TIMESTAMP)
