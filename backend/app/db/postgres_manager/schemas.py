from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: Optional[str] = None

class UserCreate(UserBase):
    password_hash: str

class UserRead(UserBase):
    user_id: int
    created_at: Optional[datetime] = None
    class Config:
        orm_mode = True

class GroupBase(BaseModel):
    name: str
    created_by: int

class GroupCreate(GroupBase):
    pass

class GroupRead(GroupBase):
    group_id: int
    created_at: Optional[datetime] = None
    class Config:
        orm_mode = True

class MessageBase(BaseModel):
    session_id: int
    sender_id: int
    content: str

class MessageCreate(MessageBase):
    pass

class MessageRead(MessageBase):
    message_id: int
    sent_at: Optional[datetime] = None
    class Config:
        orm_mode = True

class SessionBase(BaseModel):
    group_id: int
    created_by: int
    topic: Optional[str] = None

class SessionCreate(SessionBase):
    pass

class SessionRead(SessionBase):
    session_id: int
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    class Config:
        orm_mode = True

class FeedbackBase(BaseModel):
    session_id: int
    given_by: int
    content: str

class FeedbackCreate(FeedbackBase):
    pass

class FeedbackRead(FeedbackBase):
    feedback_id: int
    created_at: Optional[datetime] = None
    class Config:
        orm_mode = True
