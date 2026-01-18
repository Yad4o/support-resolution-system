"""
app/api/feedback.py

Purpose:
--------
Defines API endpoints for collecting user feedback.

Owner:
------
Om (Backend / API Layer)

Responsibilities:
-----------------
- Accept feedback for resolved tickets
- Store feedback in database
- Keep feedback collection simple and reliable

DO NOT:
-------
- Analyze feedback here
- Modify AI logic here
- Change ticket resolution status here
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.schemas.feedback import FeedbackCreate
from app.db.session import get_db

# TODO (later imports):
# from app.models.feedback import Feedback
# from app.models.ticket import Ticket

router = APIRouter()


@router.post("/{ticket_id}", status_code=status.HTTP_201_CREATED)
def submit_feedback(
    ticket_id: int,
    payload: FeedbackCreate,
    db: Session = Depends(get_db),
):
    """
    Submit feedback for a resolved ticket.

    Flow:
    -----
    1. Validate feedback input
    2. Ensure ticket exists
    3. Store feedback in database
    4. Return success response

    TODO (Implementation Steps):
    ----------------------------
    - Fetch ticket by ID
    - If ticket not found → return 404
    - Create Feedback ORM object
    - Commit DB transaction
    """

    # TODO: ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    # TODO: if not ticket → raise HTTPException(404)

    # TODO: feedback = Feedback(
    #           ticket_id=ticket_id,
    #           rating=payload.rating,
    #           resolved=payload.resolved
    #       )

    # TODO: db.add(feedback)
    # TODO: db.commit()

    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Feedback submission not implemented yet",
    )
