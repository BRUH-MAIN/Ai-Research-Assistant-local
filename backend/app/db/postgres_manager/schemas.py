from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime

class UserBase(BaseModel):
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    availability: Optional[str] = 'available'

class UserCreate(UserBase):
    pass

class UserRead(UserBase):
    user_id: int
    created_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)

class GroupBase(BaseModel):
    name: str
    created_by: int

class GroupCreate(GroupBase):
    pass

class GroupRead(GroupBase):
    group_id: int
    created_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)

class GroupParticipantBase(BaseModel):
    group_id: int
    user_id: int
    role: Optional[str] = None

class GroupParticipantCreate(GroupParticipantBase):
    pass

class GroupParticipantRead(GroupParticipantBase):
    group_participant_id: int
    joined_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)

class MessageBase(BaseModel):
    session_id: int
    sender_id: int
    content: str

class MessageCreate(MessageBase):
    pass

class MessageRead(MessageBase):
    message_id: int
    sent_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)

class SessionBase(BaseModel):
    group_id: int
    created_by: int
    topic: Optional[str] = None
    status: Optional[str] = None

class SessionCreate(SessionBase):
    pass

class SessionRead(SessionBase):
    session_id: int
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)

class SessionParticipantBase(BaseModel):
    session_id: int
    user_id: int

class SessionParticipantCreate(SessionParticipantBase):
    pass

class SessionParticipantRead(SessionParticipantBase):
    joined_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)

class FeedbackBase(BaseModel):
    session_id: int
    given_by: int
    content: str

class FeedbackCreate(FeedbackBase):
    pass

class FeedbackRead(FeedbackBase):
    created_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)

class PaperBase(BaseModel):
    title: str
    abstract: Optional[str] = None
    authors: Optional[str] = None
    doi: Optional[str] = None
    source_url: Optional[str] = None

class PaperCreate(PaperBase):
    pass

class PaperRead(PaperBase):
    paper_id: int
    published_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)

class PaperWithTags(PaperRead):
    tags: List[str] = []

class PaperSearchRequest(BaseModel):
    name: Optional[str] = None
    tags: Optional[List[str]] = None

class PaperSearchResult(BaseModel):
    found_in_db: bool
    papers: List[PaperWithTags]
    arxiv_results: Optional[List[dict]] = None

class ArxivPaperDownload(BaseModel):
    arxiv_id: str
    add_tags: Optional[List[str]] = None

class PaperTagBase(BaseModel):
    paper_id: int
    tag: str

class PaperTagCreate(PaperTagBase):
    pass

class PaperTagRead(PaperTagBase):
    model_config = ConfigDict(from_attributes=True)

class SessionPaperBase(BaseModel):
    session_id: int
    paper_id: int

class SessionPaperCreate(SessionPaperBase):
    pass

class SessionPaperRead(SessionPaperBase):
    added_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)

class AiMetadataBase(BaseModel):
    message_id: int
    paper_id: int
    page_no: Optional[int] = None

class AiMetadataCreate(AiMetadataBase):
    pass

class AiMetadataRead(AiMetadataBase):
    created_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)
