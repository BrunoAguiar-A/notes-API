from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field
from schemas.tag import Tag

class CreateNote(BaseModel):
    title: str
    content: str
    important: bool = False
    tags: Optional[List[str]] = []
    archived: bool = False
    pinned: bool = False
    favorite: bool = False

class UpdatedNote(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1)
    content: Optional[str] = Field(default=None, min_length=1)
    important: Optional[bool] = None
    tags: Optional[List[str]] = []
    archived: Optional[bool] = None
    pinned: Optional[bool] = None
    favorite: Optional[bool] = None

class ResponseNote(BaseModel):
    id: int
    title: str
    content: str
    important: bool
    tags: List[Tag] = []
    archived: bool
    owner_id: int
    pinned: bool
    favorite: bool

    model_config = ConfigDict(from_attributes=True)

class PaginatedNotes(BaseModel):
    total: int
    limit: int
    offset: int
    data: List[ResponseNote]