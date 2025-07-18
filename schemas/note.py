from pydantic import BaseModel
from typing import Optional

class CreateNote(BaseModel):
    title: str
    conteud: str
    important: bool = False

class UpdatedNote(BaseModel):
    title: Optional[str] = None
    conteud: Optional[str] = None
    important: Optional[bool] = None

class ResponseNote(BaseModel):
    id: int
    title: str
    conteud: str
    important: bool

    class Config:
        orm_mode = True
