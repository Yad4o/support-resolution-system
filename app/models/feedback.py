"""
app/models/feedback.py

Purpose:
--------
Defines the Feedback database model.

Owner:
------
Om (Backend / Data Modeling)

Responsibilities:
-----------------
- Store user feedback for ticket resolutions
- Track whether auto-resolution was successful
- Enable future AI improvement

DO NOT:
-------
- Analyze feedback here
- Adjust AI models here
- Implement business logic here
"""

from datetime import datetime
from sqlalchemy import Column, Integer, Boolean, DateTime

from app.db.session import Base


class Feedback(Base):
    """
    Feedback ORM model.

    Feedback is submitted by users after a ticket
    has been resolved (auto or human).
    """

    __tablename__ = "feedback"

    # -------------------------------------------------
    # Columns
    # -------------------------------------------------

    id = Column(
        Integer,
        primary_key=True,
        index=True,
        doc="Primary key identifier for feedback entry",
    )

    ticket_id = Column(
        Integer,
        nullable=False,
        doc="ID of the ticket this feedback belongs to",
    )

    rating = Column(
        Integer,
        nullable=False,
        doc="User rating (e.g., 1–5)",
    )

    resolved = Column(
        Boolean,
        nullable=False,
        doc="Whether the issue was actually resolved",
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        doc="Timestamp when feedback was submitted",
    )

    # -------------------------------------------------
    # TODO (Future Enhancements)
    # -------------------------------------------------
    # - foreign key constraint to tickets
    # - sentiment score
