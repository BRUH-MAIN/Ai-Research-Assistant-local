from pydantic import BaseModel

class MessageSchema(BaseModel):
    id: int
    content: str
    sender_id: int
    # Add other fields as needed

    class Config:
        from_attributes = True
