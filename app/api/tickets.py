"""
app/api/tickets.py

Purpose:
--------
Defines API endpoints for managing support tickets.

Owner:
------
Om (Backend / Core API)

Responsibilities:
-----------------
- Create support tickets
- Retrieve ticket information
- Trigger automated ticket resolution workflow

DO NOT:
-------
- Implement AI classification here
- Implement resolution decision logic here
- Access external APIs directly here
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.schemas.ticket import (
    TicketCreate,
    TicketResolveRequest,
    TicketResponse,
)
from app.db.session import get_db

# TODO (later imports):
# from app.models.ticket import Ticket
# from app.services.classifier import classify_intent
# from app.services.decision import decide
# from app.services.resolver import generate_response

router = APIRouter()


@router.post("/", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
def create_ticket(
    payload: TicketCreate,
    db: Session = Depends(get_db),
):
    """
    Create a new support ticket.

    Flow:
    -----
    1. Validate input using TicketCreate schema
    2. Store ticket in database with status = 'open'
    3. Return created ticket

    TODO (Implementation Steps):
    ----------------------------
    - Create Ticket ORM object
    - Add to DB session
    - Commit transaction
    - Refresh instance
    """

    # TODO: ticket = Ticket(message=payload.message)
    # TODO: db.add(ticket)
    # TODO: db.commit()
    # TODO: db.refresh(ticket)

    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Ticket creation not implemented yet",
    )


@router.get("/{ticket_id}", response_model=TicketResponse)
def get_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
):
    """
    Fetch a ticket by its ID.

    Flow:
    -----
    1. Fetch ticket from DB
    2. If not found → return 404
    3. Return ticket data

    TODO:
    -----
    - Query Ticket by ID
    - Handle missing ticket
    """

    # TODO: ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    # TODO: if not ticket → raise 404

    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Get ticket not implemented yet",
    )


@router.post("/{ticket_id}/resolve", response_model=TicketResponse)
def resolve_ticket(
    ticket_id: int,
    _: TicketResolveRequest,
    db: Session = Depends(get_db),
):
    """
    Trigger automated resolution for a ticket.

    Flow:
    -----
    1. Fetch ticket from DB
    2. Send message to AI classifier (services layer)
    3. Receive intent + confidence
    4. Decide auto vs escalate
    5. Update ticket status and fields
    6. Return updated ticket

    IMPORTANT:
    ----------
    AI logic is delegated to services layer (Prajwal).

    TODO (Implementation Steps):
    ----------------------------
    - Fetch ticket
    - Call classify_intent(ticket.message)
    - Call decide(confidence)
    - Update ticket fields
    - Commit DB changes
    """

    # TODO: Fetch ticket
    # TODO: Call AI classifier
    # TODO: Decision logic
    # TODO: Update ticket
    # TODO: Commit and return

    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Ticket resolution not implemented yet",
    )
