from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from schemas.note import CreateNote, UpdatedNote, ResponseNote
from services import note_service
from database import get_db
from models.note import Notes

router = APIRouter(
    prefix="/notes",
    tags=["Notes"]
)

@router.get("/", response_model=List[ResponseNote])
def get_notes(db: Session = Depends(get_db)):
    return note_service.list_notes(db)

@router.get("/{note_id}", response_model=ResponseNote)
def get_note(note_id: int, db: Session = Depends(get_db)):
    note = note_service.search_note(db, note_id)
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    return note

@router.post("/", response_model=ResponseNote, status_code=201)
def create_note(note: CreateNote, db: Session = Depends(get_db)):
    existing_note = db.query(Notes).filter(Notes.title == note.title).first()
    if existing_note:
        raise HTTPException(status_code=409, detail="Note with this title already exists")
    if "forbidden" in note.title.lower():
        raise HTTPException(status_code=400, detail="Title contains forbidden word")
    return note_service.create_note(db, note)

@router.put("/{note_id}", response_model=ResponseNote)
def update_note(note_id: int, updated_note: UpdatedNote, db: Session = Depends(get_db)):
    updated = note_service.update_note(db, note_id, updated_note)
    if updated is None:
        raise HTTPException(status_code=404, detail="Note not found")
    return updated

@router.patch("/{note_id}", response_model=ResponseNote)
def patch_note(note_id: int, note_update: UpdatedNote, db: Session = Depends(get_db)):
    patched = note_service.patch_note(db, note_id, note_update)
    if patched is None:
        raise HTTPException(status_code=404, detail="Note not found")
    return patched

@router.delete("/{note_id}", status_code=204)
def delete_note(note_id: int, db: Session = Depends(get_db)):
    success = note_service.delete_note(db, note_id)
    if not success:
        raise HTTPException(status_code=404, detail="Note not found")
    return None
