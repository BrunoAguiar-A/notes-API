from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.note import Notes
from models.user import User
from database import get_db
from services import note_service
from schemas.shared import ShareNoteRequest
from auth.deps import get_current_user


router = APIRouter()

@router.post("/notes/{note_id}/share")
def share_note(
    note_id: int,
    request: ShareNoteRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    note = db.query(Notes).filter(Notes.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    if note.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the owner can share the note")
    recipient = db.query(User).filter(User.username == request.recipient_username).first()
    if not recipient:
        raise HTTPException(status_code=404, detail="Recipient not found")
    success = note_service.share_note(db, note_id, recipient.id, request.can_edit)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to share note")
    return {"message": "Note shared successfully"}