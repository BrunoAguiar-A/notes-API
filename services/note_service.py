from typing import List, Optional
from schemas.note import CreateNote, UpdatedNote, ResponseNote
from models.memory import Notes, count_id

def list_notes() -> List[ResponseNote]:
    return Notes

def create_note(new: CreateNote) -> ResponseNote:
    global count_id
    note = ResponseNote(id=count_id, **new.dict())
    Notes.append(note)
    count_id += 1
    return note

def search_note(note_id: int) -> Optional[ResponseNote]:
    return next((n for n in Notes if n.id == note_id), None)

def update_note(note_id: int, updated: CreateNote) -> ResponseNote:
    for i, note in enumerate(Notes):
        if note.id == note_id:
            Notes[i] = ResponseNote(id=note_id, **updated.dict())
            return Notes[i]
    raise ValueError("Note not found")

def patch_note(note_id: int, update: UpdatedNote) -> ResponseNote:
    note = search_note(note_id)
    if note is None:
        raise ValueError("Note not found")
    
    if update.title is not None:
        note.title = update.title
    if update.conteud is not None:
        note.conteud = update.conteud
    if update.important is not None:
        note.important = update.important

    return note

def delete_note(note_id: int) -> bool:
    global Notes
    before = len(Notes)
    Notes = [n for n in Notes if n.id != note_id]
    return len(Notes) < before
