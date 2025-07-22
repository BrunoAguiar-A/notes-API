from pydantic import BaseModel, ConfigDict

class TagBase(BaseModel):
    name: str

class TagCreate(TagBase):
    pass

class Tag(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)