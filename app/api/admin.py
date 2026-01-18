"""
app/api/admin.py

Purpose:
--------
Defines admin-level API endpoints for system monitoring and metrics.

Owner:
------
Om (Backend / Admin APIs)

Responsibilities:
-----------------
- Provide system-level metrics
- Expose aggregated ticket statistics
- Support operational monitoring

DO NOT:
-------
- Implement ticket resolution here
- Modify AI behavior here
- Expose sensitive personal data
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db

# TODO (later imports):
# from app.models.ticket import Ticket
# from app.models.feedback import Feedback

router = APIRouter()


@router.get("/metrics")
def get_metrics(db: Session = Depends(get_db)):
    """
    Retrieve high-level system metrics.

    Metrics may include:
    --------------------
    - Total number of tickets
    - Auto-resolved vs escalated tickets
    - Average feedback rating
    - Resolution success rate

    TODO (Implementation Steps):
    ----------------------------
    - Count total tickets
    - Count tickets by status
    - Aggregate feedback ratings
    - Return metrics in structured format
    """

    # TODO: total_tickets = db.query(Ticket).count()
    # TODO: auto_resolved = db.query(Ticket).filter(Ticket.status == "auto_resolved").count()
    # TODO: escalated = db.query(Ticket).filter(Ticket.status == "escalated").count()
    # TODO: avg_rating = ...

    return {
        "status": "NOT_IMPLEMENTED",
        "metrics": {},
    }
