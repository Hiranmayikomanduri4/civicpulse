"""
Database connection and session management module.
Supports SQLite locally and PostgreSQL on Vercel.
"""

from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.engine import Engine
from backend.app.config import settings

DATABASE_URL = settings.DATABASE_URL

# Support PostgreSQL URLs provided by database hosting services.
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace(
        "postgres://", "postgresql://", 1
    )

engine = create_engine(
    DATABASE_URL,
    connect_args=(
        {"check_same_thread": False}
        if DATABASE_URL.startswith("sqlite")
        else {}
    ),
    pool_pre_ping=True,
)

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if DATABASE_URL.startswith("sqlite"):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    from backend.app.models import Report, StatusUpdate, AdminUser
    from backend.app.seed_data import seed_initial_data

    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        seed_initial_data(db)
    finally:
        db.close()
