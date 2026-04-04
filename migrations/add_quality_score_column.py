"""
Migration: Add quality_score column to tickets table

This migration adds the 'quality_score' column to the existing tickets table
to support normalized quality scores from feedback (0.0-1.0). The column is nullable
and defaults to NULL for existing tickets that don't have feedback yet.

Run this migration for existing installations that don't have the quality_score column.
"""

import logging
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine, text
from app.core.config import settings

logger = logging.getLogger(__name__)


def add_quality_score_column() -> bool:
    """
    Add quality_score column to tickets table if it doesn't exist.

    Uses the configured database URL from settings.DATABASE_URL.

    Returns:
        bool: True if migration was successful, False otherwise
    """
    try:
        engine = create_engine(settings.DATABASE_URL)

        with engine.connect() as conn:
            # Check if column already exists (SQLite-compatible introspection)
            result = conn.execute(text("PRAGMA table_info(tickets)"))
            columns = [row[1] for row in result.fetchall()]

            if "quality_score" in columns:
                logger.info("quality_score column already exists in tickets table")
                return True

            # Add quality_score column as nullable FLOAT/REAL (matching SQLAlchemy Float)
            conn.execute(text("ALTER TABLE tickets ADD COLUMN quality_score REAL"))
            conn.commit()

            logger.info("Successfully added quality_score column to tickets table")
            return True

    except Exception as e:
        logger.error("Failed to add quality_score column: %s", e)
        return False


def run_migration() -> None:
    """Run the migration and report results."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    success = add_quality_score_column()
    if success:
        print("Migration completed successfully")
    else:
        print("Migration failed")
        sys.exit(1)


if __name__ == "__main__":
    run_migration()
