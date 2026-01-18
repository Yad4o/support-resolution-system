"""
app/services/resolver.py

Purpose:
--------
Generates a human-readable resolution message for a support ticket.

Owner:
------
Prajwal (AI / NLP / Response Generation)

Why this exists:
----------------
Once we understand WHAT the problem is (intent),
we must generate a clear, helpful response for the user.

Responsibilities:
-----------------
- Generate solution text based on intent
- Reuse known solutions when possible
- Ensure responses are polite and clear

DO NOT:
-------
- Decide auto vs escalate
- Access database
- Modify ticket status
"""

from typing import Optional


def generate_response(
    intent: str,
    original_message: str,
    similar_solution: Optional[str] = None,
) -> str:
    """
    Generate a response for a support ticket.

    Parameters:
    -----------
    intent : str
        Predicted intent category (e.g., 'login_issue', 'payment')

    original_message : str
        Original customer message (used for context)

    similar_solution : Optional[str]
        Previously used solution for a similar ticket (if found)

    Returns:
    --------
    str
        Final response message to be shown to the user
    """

    # -------------------------------------------------
    # STEP 1: Reuse known solution (highest priority)
    # -------------------------------------------------
    """
    If a similar ticket was found earlier and its solution
    worked well, reuse that solution directly.
    """

    if similar_solution:
        # TODO:
        # - Slightly rephrase (optional)
        # - Ensure tone is polite
        return similar_solution

    # -------------------------------------------------
    # STEP 2: Intent-based static responses (MVP)
    # -------------------------------------------------
    """
    Initial version should use predefined responses.

    Example:
    - login_issue → password reset steps
    - payment → billing FAQ
    """

    if intent == "login_issue":
        return (
            "It looks like you're having trouble logging in. "
            "Please try resetting your password using the "
            "'Forgot Password' option on the login page."
        )

    if intent == "payment_issue":
        return (
            "We noticed a payment-related issue. "
            "Please check your billing details and ensure "
            "your payment method is valid."
        )

    # -------------------------------------------------
    # STEP 3: AI-generated response (future)
    # -------------------------------------------------
    """
    TODO (Advanced):
    - Use OpenAI / LLM to generate contextual response
    - Include safety checks
    - Keep responses concise
    """

    # -------------------------------------------------
    # STEP 4: Fallback response
    # -------------------------------------------------
    """
    Used when intent is unknown or confidence is low.
    """

    return (
        "Thanks for reaching out. "
        "We are reviewing your issue and will get back to you shortly."
    )
