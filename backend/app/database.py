"""
Database connection and session management module.
Uses SQLite for zero-configuration, zero-cost persistent local storage.
"""
from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.engine import Engine
from backend.app.config import settings

# Create engine with support for SQLite multi-threading
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

# Enable foreign keys for SQLite
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if "sqlite" in settings.DATABASE_URL:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base model class
Base = declarative_base()


def get_db():
    """Dependency that provides a database session and ensures it closes cleanly."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables and seed initial demo data if configured."""
    from backend.app.models import Report, StatusUpdate, AdminUser
    from backend.app.seed_data import seed_initial_data
    
    Base.metadata.create_all(bind=engine)
    
    # Run seed script if enabled
    db = SessionLocal()
    try:
        seed_initial_data(db)
    finally:
        db.close()
