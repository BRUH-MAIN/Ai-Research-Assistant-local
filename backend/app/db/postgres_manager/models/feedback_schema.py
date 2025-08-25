from pydantic import BaseModel

class FeedbackSchema(BaseModel):
    id: int
    user_id: int
    message: str
    # Add other fields as needed

    class Config:
        from_attributes = True
