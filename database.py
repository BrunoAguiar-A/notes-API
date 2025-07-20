from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, declarative_base

# SQLite file
DATABASE_URL = "sqlite:///./notas.db"

# Create connection engine
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base for the ORM models
Base = declarative_base()

# Function to initialize tables
def init_db():
    from models import note  # Delayed import to avoid circular dependency
    Base.metadata.create_all(bind=engine)

# Dependency to inject database session
def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()