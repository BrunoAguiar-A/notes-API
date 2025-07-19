from typing import List, Optional
from schemas.note import CreateNote, UpdatedNote, ResponseNote
from models.note import Notes
from sqlalchemy.orm import Session

def list_notes(db: Session) -> List[ResponseNote]:
    # Retrieve all notes from the database
    notes = db.query(Notes).all()
    return [ResponseNote.model_validate(note) for note in notes]

def create_note(db: Session, note: CreateNote) -> ResponseNote:
    # Create a new Note instance with the provided data
    new_note = Notes(
        title=note.title,
        content=note.content,
        important=note.important
    )

    # Add the new note to the session and commit it to the database
    db.add(new_note)
    db.commit()
    db.refresh(new_note)

    # Return the created note as a response schema
    return ResponseNote.model_validate(new_note)


def search_note(db: Session, note_id: int) -> Optional[ResponseNote]:
    # Search for a note by its ID
    note = db.query(Notes).filter(Notes.id == note_id).first()
    if note:
        return ResponseNote.model_validate(note)
    return None

def update_note(db: Session, note_id: int, updated: UpdatedNote) -> Optional[ResponseNote]:
    # Update a note fully with new data
    note = db.query(Notes).filter(Notes.id == note_id).first()
    if not note:
        return None

    if updated.title is not None:
        note.title = updated.title
    if updated.content is not None:
        note.content = updated.content
    if updated.important is not None:
        note.important = updated.important

    db.commit()
    db.refresh(note)
    return ResponseNote.model_validate(note)

def patch_note(db: Session, note_id: int, update: UpdatedNote) -> Optional[ResponseNote]:
    # Update only fields that are provided (partial update)
    note = db.query(Notes).filter(Notes.id == note_id).first()
    if not note:
        return None

    if update.title is not None:
        note.title = update.title
    if update.content is not None:
        note.content = update.content
    if update.important is not None:
        note.important = update.important

    db.commit()
    db.refresh(note)
    return ResponseNote.model_validate(note)

def delete_note(db: Session, note_id: int) -> bool:
    # Delete a note by its ID
    note = db.query(Notes).filter(Notes.id == note_id).first()
    if not note:
        return False

    db.delete(note)
    db.commit()
    return True
