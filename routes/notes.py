from fastapi import APIRouter, HTTPException
from schemas.note import CreateNote, UpdatedNote, ResponseNote
from services.note_service import (
    list_notes, create_note, search_note,
    update_note, patch_note, delete_note
)

router = APIRouter()

@router.get("/", response_model=list[ResponseNote])
def get_notes():
    return list_notes()

@router.post("/", response_model=ResponseNote)
def post_note(note: CreateNote):
    return create_note(note)

@router.get("/{note_id}", response_model=ResponseNote)
def get_note(note_id: int):
    note = search_note(note_id)
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    return note

@router.put("/{note_id}", response_model=ResponseNote)
def put_note(note_id: int, note: CreateNote):
    try:
        return update_note(note_id, note)
    except ValueError:
        raise HTTPException(status_code=404, detail="Note not found")

@router.patch("/{note_id}", response_model=ResponseNote)
def patch_note_handler(note_id: int, update: UpdatedNote):
    try:
        return patch_note(note_id, update)
    except ValueError:
        raise HTTPException(status_code=404, detail="Note not found")

@router.delete("/{note_id}")
def delete_note_handler(note_id: int):
    if delete_note(note_id):
        return {"ok": True}
    raise HTTPException(status_code=404, detail="Note not found")
