from pydantic import BaseModel
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

class CreateNote(BaseModel):
    title: str
    content: str
    important: bool = False

class UpdatedNote(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1)
    content: Optional[str] = Field(default=None, min_length=1)
    important: Optional[bool] = None

class ResponseNote(BaseModel):
    id: int
    title: str
    content: str
    important: bool

    model_config = ConfigDict(from_attributes=True)
