from sqlalchemy import Column, DateTime, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from sqlalchemy.sql import func
from models.note_tags import note_tags

class Notes(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    important = Column(Boolean, default=False)
    updated_at  = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    archived = Column(Boolean, default=False)
    owner_id = Column(Integer, ForeignKey("users.id"))
    pinned = Column(Boolean, default=False)
    favorite = Column(Boolean, default=False)

    owner = relationship("User", back_populates="notes")
    shared_with = relationship("SharedNote", back_populates="note", cascade="all, delete")
    tags = relationship("Tag", secondary=note_tags, back_populates="notes")

class SharedNote(Base):
    __tablename__ = "shared_notes"

    id = Column(Integer, primary_key=True, index=True)
    note_id = Column(Integer, ForeignKey("notes.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    permission = Column(String, default="read")
    can_edit = Column(Boolean, default=False)

    note = relationship("Notes", back_populates="shared_with")
    user = relationship("User", back_populates="shared_notes")