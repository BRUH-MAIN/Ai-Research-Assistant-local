from pydantic import BaseModel

class GroupSchema(BaseModel):
    id: int
    name: str
    # Add other fields as needed

    class Config:
        from_attributes = True
