from pydantic import BaseModel

class SessionSchema(BaseModel):
    id: int
    user_id: int
    # Add other fields as needed

    class Config:
        from_attributes = True
