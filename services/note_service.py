from typing import Optional
from fastapi import HTTPException
from sqlalchemy import or_
from schemas.note import CreateNote, UpdatedNote, ResponseNote, PaginatedNotes
from models.note import Notes, SharedNote
from models.user import User
from sqlalchemy.orm import Session
from models.tag import Tag

def list_notes_paginated(
    db: Session,
    q: Optional[str] = None,
    tag: Optional[str] = None,
    favorite: Optional[bool] = None,
    pinned: Optional[bool] = None,
    show_archived: bool = False,
    limit: int = 10,
    offset: int = 0,
    order_by: str = "id",
    order: str = "asc"
) -> PaginatedNotes:
    base_query = db.query(Notes)

    if not show_archived:
        base_query = base_query.filter(Notes.archived == False)
    column = getattr(Notes, order_by)
    base_query = base_query.order_by(
        Notes.pinned.desc(), 
        column.desc() if order == "desc" else column.asc())
    if tag:
        base_query = base_query.join(Notes.tags).filter(Tag.name == tag)
    if q: 
        base_query = base_query.filter(
            or_(
                Notes.title.ilike(f"%{q}%"),
                Notes.content.ilike(f"%{q}%")
            )
        )
    if favorite is not None:
        base_query = base_query.filter(Notes.favorite == favorite)

    if pinned is not None:
        base_query = base_query.filter(Notes.pinned == pinned)
    # Validate order_by field
    if not hasattr(Notes, order_by):
        order_by = "id"
    column = getattr(Notes, order_by)
    if order.lower() == "desc":
        column = column.desc()
    else:
        column = column.asc()

    base_query = base_query.order_by(column)
    total = base_query.count()
    result = base_query.offset(offset).limit(limit).all()
    valid_fields = {"id", "title", "content", "important"}
    if order_by not in valid_fields:
        raise HTTPException(status_code=422, detail="Invalid order_by field")

    return PaginatedNotes(
        total = total,
        limit = limit,
        offset = offset,
        data = result
    )

def create_note(
    db: Session, 
    note: CreateNote,
    owner_id: int
) -> ResponseNote:
    # Create a new Note instance with the provided data
    new_note = Notes(
        title=note.title,
        content=note.content,
        important=note.important,
        archived=note.archived,
        owner_id=owner_id,
        pinned=note.pinned,
        favorite=note.favorite
    )
    # Create Tags
    tag_objects = []
    for tag_name in note.tags:
        tag = db.query(Tag).filter_by(name=tag_name).first()
        if not tag:
            tag = Tag(name=tag_name)
            db.add(tag)
            db.commit()
            db.refresh(tag)
        tag_objects.append(tag)
    
    new_note.tags = tag_objects

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

def update_note(db: Session, note: Notes, updated: UpdatedNote) -> Optional[ResponseNote]:
    if updated.title is not None:
        note.title = updated.title
    if updated.content is not None:
        note.content = updated.content
    if updated.important is not None:
        note.important = updated.important
    if updated.archived is not None:
        note.archived = updated.archived
    if updated.pinned is not None:
        note.pinned = updated.pinned
    if updated.favorite is not None:
        note.favorite = updated.favorite
        
    # Update Tags, if have
    if updated.tags is not None:
        updated_tags = []
        for tag_name in updated.tags:
            tag = db.query(Tag).filter_by(name=tag_name).first()
            if not tag:
                tag = Tag(name=tag_name)
                db.add(tag)
                db.commit()
                db.refresh(tag)
            updated_tags.append(tag)
        note.tags = updated_tags

    db.commit()
    db.refresh(note)
    return ResponseNote.model_validate(note)

def patch_note(db: Session, note_id: int, updated: UpdatedNote) -> Optional[ResponseNote]:
    # Update only fields that are provided 
    note = db.query(Notes).filter(Notes.id == note_id).first()
    if not note:
        return None

    if updated.title is not None:
        note.title = updated.title
    if updated.content is not None:
        note.content = updated.content
    if updated.important is not None:
        note.important = updated.important
    if updated.pinned is not None:
        note.pinned = updated.pinned
    if updated.archived is not None:
        note.archived = updated.archived
    if updated.favorite is not None:
        note.favorite = updated.favorite

    if updated.tags is not None:
        new_tags = []
        for tag_name in updated.tags:
            tag = db.query(Tag).filter_by(name=tag_name).first()
            if not tag:
                tag = Tag(name=tag_name)
                db.add(tag)
                db.commit()
                db.refresh(tag)
            new_tags.append(tag)
        note.tags = new_tags

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

def share_note(db: Session, note_id: int, target_user_id: int, can_edit: bool) -> bool:
    # Check if note exists
    note = db.query(Notes).filter(Notes.id == note_id).first()
    if not note:
        return False

    # Check if target user exists
    user = db.query(User).filter(User.id == target_user_id).first()
    if not user:
        return False

    # Create shared note entry
    shared = SharedNote(
        note_id=note_id,
        user_id=target_user_id,
        can_edit=can_edit
    )
    db.add(shared)
    db.commit()
    return True