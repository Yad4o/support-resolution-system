"""
app/db/session.py

Purpose:
--------
Database engine and session management.

Owner:
------
Om (Backend / System)

Responsibilities:
-----------------
- Create SQLAlchemy engine
- Provide session factory
- Expose Base class for ORM models
- Provide FastAPI dependency for DB sessions

DO NOT:
-------
- Define models here
- Write queries here
- Commit transactions here
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.core.config import settings

# -------------------------------------------------
# Database Engine
# -------------------------------------------------

"""
The engine is the core interface to the database.

NOTE:
- For SQLite, `check_same_thread=False` is required
- For PostgreSQL, this option must NOT be used
"""

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False}
    if settings.DATABASE_URL.startswith("sqlite")
    else {},
    echo=settings.DEBUG,  # TODO: disable in production
)

# -------------------------------------------------
# Session Factory
# -------------------------------------------------

"""
SessionLocal creates a new database session per request.

autocommit=False → manual commit control  
autoflush=False  → explicit flush control
"""

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# -------------------------------------------------
# Declarative Base
# -------------------------------------------------

"""
All ORM models must inherit from this Base.
"""

Base = declarative_base()

# -------------------------------------------------
# FastAPI Dependency
# -------------------------------------------------


def get_db():
    """
    FastAPI dependency that provides a database session.

    Usage:
    ------
    db: Session = Depends(get_db)

    Lifecycle:
    ----------
    - Session opened at request start
    - Session closed at request end (even on error)
    """

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
