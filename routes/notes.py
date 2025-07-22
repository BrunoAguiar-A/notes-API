from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import  Optional
from models.user import User
from schemas.note import CreateNote, UpdatedNote, ResponseNote, PaginatedNotes
from services import note_service
from database import get_db
from models.note import Notes, SharedNote
from auth.deps import get_current_user


VALID_ORDER_FIELDS = {"id", "title", "content", "important"}

# Define the router with a prefix for all /notes endpoints
router = APIRouter(
    prefix="/notes",
    tags=["Notes"],
    dependencies=[Depends(get_current_user)] 
)


# Get a single note by its ID
@router.get("/{note_id}", response_model=ResponseNote)
def get_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    note = note_service.search_note(db, note_id)
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")

    # Owner access
    if note.owner_id == current_user.id:
        return note

    # Shared access
    shared = db.query(SharedNote).filter_by(
        note_id=note_id,
        user_id=current_user.id
    ).first()

    if shared:
        return note

    # Access denied
    raise HTTPException(status_code=403, detail="You don't have access to this note")


# Create a new note
@router.post("/", response_model=ResponseNote, status_code=201)
def create_note(
    note: CreateNote,
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    # Check if a note with the same title already exists
    existing_note = db.query(Notes).filter(Notes.title == note.title).first()
    if existing_note:
        raise HTTPException(status_code=409, detail="Note with this title already exists")

    # Example of validation logic: block certain words in title
    if "forbidden" in note.title.lower():
        raise HTTPException(status_code=400, detail="Title contains forbidden word")

    return note_service.create_note(db, note, owner_id=current_user.id)

# Update an entire note by ID
@router.put("/{note_id}", response_model=ResponseNote)
def update_note(
    note_id: int,
    note_data: UpdatedNote,
    db: Session = Depends(get_db), 
    current_user: str = Depends(get_current_user)
):
    # Search note first
    note = db.query(Notes).filter(Notes.id == note_id).first()

    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    # If owner, can edit
    if note.owner_id == current_user.id:
        return note_service.update_note(db, note, note_data)
    # Otherwise, check if the note was shared with editing permission.
    shared = db.query(SharedNote).filter_by(
        note_id=note_id,
        user_id=current_user.id,
        can_edit=True
    ).first()

    if shared:
        return note_service.update_note(db, note, note_data)

    raise HTTPException(status_code=403, detail="You dont have permission to edit this note")

# Patch specific fields of a note
@router.patch("/{note_id}", response_model=ResponseNote)
def patch_note(
    note_id: int,
    note_update: UpdatedNote,
    db: Session = Depends(get_db), current_user: str = Depends(get_current_user)
):
    patched = note_service.patch_note(db, note_id, note_update)
    if patched is None:
        raise HTTPException(status_code=404, detail="Note not found")
    return patched

# Delete a note by ID
@router.delete("/{note_id}", status_code=204)
def delete_note(
    note_id: int,
    db: Session = Depends(get_db), current_user: str = Depends(get_current_user)
):
    success = note_service.delete_note(db, note_id)
    if not success:
        raise HTTPException(status_code=404, detail="Note not found")
    return None
    
@router.get("/", response_model=PaginatedNotes)
def list_notes(
    q: Optional[str] = Query(None, description="Search in title or content"),
    tag: Optional[str] = Query(None, description="Filter by tag name"),
    favorite: Optional[bool] = Query(None, description="Filter by favorite"),
    pinned: Optional[bool] = Query(None, description="Filter by pinned"),
    archived: Optional[bool] = Query(False, description="Include archived notes"),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    order_by: str = Query("id", description="Column to sort by"),
    order: str = Query("asc", pattern="^(asc|desc)$", description="Sort order"),
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    if order_by not in VALID_ORDER_FIELDS:
        raise HTTPException(status_code=422, detail=f"Invalid order_by field: {order_by}")

    return note_service.list_notes_paginated(
        db=db,
        q=q,
        tag=tag,
        favorite=favorite,
        pinned=pinned,
        show_archived=archived,
        limit=limit,
        offset=offset,
        order_by=order_by,
        order=order
    )
@router.patch("/{note_id}/pin", response_model=ResponseNote)
def pin_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    note = db.query(Notes).filter(Notes.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    if note.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="You do not own this note")

    note.pinned = True
    db.commit()
    db.refresh(note)
    return ResponseNote.model_validate(note)


@router.patch("/{note_id}/unpin", response_model=ResponseNote)
def unpin_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    note = db.query(Notes).filter(Notes.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    if note.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="You do not own this note")

    note.pinned = False
    db.commit()
    db.refresh(note)
    return ResponseNote.model_validate(note)

@router.get("/pinned", response_model=PaginatedNotes)
def list_pinned_notes(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    from models.note import Notes

    query = db.query(Notes).filter(
        Notes.owner_id == current_user.id,
        Notes.pinned == True,
        Notes.archived == False
    )

    total = query.count()
    notes = query.order_by(Notes.id.desc()).offset(offset).limit(limit).all()

    return PaginatedNotes(
        total=total,
        limit=limit,
        offset=offset,
        data=notes
    )

@router.patch("/{note_id}/favorite", response_model=ResponseNote)
def favorite_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    note = db.query(Notes).filter(Notes.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    if note.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="You do not own this note")

    note.favorite = True
    db.commit()
    db.refresh(note)
    return ResponseNote.model_validate(note)


@router.patch("/{note_id}/unfavorite", response_model=ResponseNote)
def unfavorite_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    note = db.query(Notes).filter(Notes.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    if note.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="You do not own this note")

    note.favorite = False
    db.commit()
    db.refresh(note)
    return ResponseNote.model_validate(note)

@router.get("/favorites", response_model=PaginatedNotes)
def list_favorite_notes(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    from models.note import Notes

    query = db.query(Notes).filter(
        Notes.owner_id == current_user.id,
        Notes.favorite == True,
        Notes.archived == False
    )

    total = query.count()
    notes = query.order_by(Notes.id.desc()).offset(offset).limit(limit).all()

    return PaginatedNotes(
        total=total,
        limit=limit,
        offset=offset,
        data=notes
    )

@router.get("/shared", response_model=PaginatedNotes)
def list_shared_notes(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    from models.note import Notes, SharedNote

    # Buscar IDs das notas compartilhadas comigo
    shared_ids = db.query(SharedNote.note_id).filter(
        SharedNote.user_id == current_user.id
    )

    query = db.query(Notes).filter(
        Notes.id.in_(shared_ids),
        Notes.archived == False  # Não mostra arquivadas
    )

    total = query.count()
    notes = query.order_by(Notes.pinned.desc(), Notes.id.desc()).offset(offset).limit(limit).all()

    return PaginatedNotes(
        total=total,
        limit=limit,
        offset=offset,
        data=notes
    )

@router.get("/mine", response_model=PaginatedNotes)
def list_my_notes(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    from models.note import Notes

    query = db.query(Notes).filter(
        Notes.owner_id == current_user.id,
        Notes.archived == False
    )

    total = query.count()
    notes = query.order_by(Notes.pinned.desc(), Notes.id.desc()).offset(offset).limit(limit).all()

    return PaginatedNotes(
        total=total,
        limit=limit,
        offset=offset,
        data=notes
    )
