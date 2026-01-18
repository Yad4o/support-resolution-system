"""
app/schemas/feedback.py

Purpose:
--------
Defines Pydantic schemas for Feedback-related API requests and responses.

Owner:
------
Om (Backend / API Contracts)

Responsibilities:
-----------------
- Validate feedback submitted by users
- Define clean API input/output contracts
- Protect internal analytics logic

DO NOT:
-------
- Store feedback in database here
- Analyze feedback here
- Modify AI confidence thresholds here
"""

from pydantic import BaseModel
from datetime import datetime


class FeedbackCreate(BaseModel):
    """
    Schema used when a user submits feedback for a ticket.

    Used in:
    --------
    POST /feedback/{ticket_id}

    Fields:
    -------
    - rating: Numerical rating (e.g., 1–5)
    - resolved: Whether the issue was resolved
    """

    rating: int
    resolved: bool

    # TODO (Validation Enhancements):
    # - rating range validation (1–5)


class FeedbackResponse(BaseModel):
    """
    Schema returned when feedback data is retrieved (admin use).

    Used in:
    --------
    GET /admin/feedback
    """

    id: int
    ticket_id: int
    rating: int
    resolved: bool
    created_at: datetime

    class Config:
        """
        Enables ORM compatibility.
        """
        orm_mode = True
