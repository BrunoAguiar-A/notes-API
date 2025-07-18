from pydantic import BaseModel
from typing import Optional

class CreateNote(BaseModel):
    title: str
    content: str
    important: bool = False

class UpdatedNote(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    important: Optional[bool] = None

class ResponseNote(BaseModel):
    id: int
    title: str
    content: str
    important: bool

    class Config:
        from_attributes = True  # Habilita o uso de from_orm()
        orm_mode = True
