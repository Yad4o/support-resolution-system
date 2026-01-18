"""
app/services/decision.py

Purpose:
--------
Decides whether a support ticket should be auto-resolved
or escalated to a human agent.

Owner:
------
Prajwal (AI / Decision Logic)

Why this exists:
----------------
AI predictions are probabilistic.
This layer ensures that risky or uncertain cases
are safely escalated to humans.

Responsibilities:
-----------------
- Interpret AI confidence scores
- Apply business thresholds
- Return clear resolution decisions

DO NOT:
-------
- Generate responses
- Access database
- Update ticket status
"""

from enum import Enum


class ResolutionDecision(str, Enum):
    """
    Possible resolution actions.
    """

    AUTO_RESOLVE = "auto_resolve"
    ESCALATE = "escalate"


def decide_resolution(confidence: float) -> ResolutionDecision:
    """
    Decide whether to auto-resolve or escalate a ticket.

    Parameters:
    -----------
    confidence : float
        Confidence score returned by AI (0.0 – 1.0)

    Returns:
    --------
    ResolutionDecision
        AUTO_RESOLVE or ESCALATE
    """

    # -------------------------------------------------
    # STEP 1: Validate input
    # -------------------------------------------------
    """
    TODO:
    - Ensure confidence is within 0.0–1.0
    - Handle None or invalid values safely
    """

    # -------------------------------------------------
    # STEP 2: Decision thresholds
    # -------------------------------------------------
    """
    Suggested thresholds (initial):
    -------------------------------
    - confidence >= 0.75 → auto-resolve
    - confidence < 0.75 → escalate

    These thresholds MUST be conservative.
    """

    THRESHOLD = 0.75  # TODO: move to config later

    if confidence >= THRESHOLD:
        return ResolutionDecision.AUTO_RESOLVE

    # -------------------------------------------------
    # STEP 3: Escalation fallback
    # -------------------------------------------------

    return ResolutionDecision.ESCALATE
