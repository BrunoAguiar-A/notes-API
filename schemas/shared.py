from pydantic import BaseModel

class ShareNoteRequest(BaseModel):
    recipient_username: str  
    can_edit: bool = False  