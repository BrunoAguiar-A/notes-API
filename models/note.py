from sqlalchemy import Column, Integer, String, Boolean
from database import Base

class Notes(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    important = Column(Boolean, default=True)
