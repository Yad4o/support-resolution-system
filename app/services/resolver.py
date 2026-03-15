"""
app/services/resolver.py

Purpose:
--------
Resolver service that provides high-level ticket resolution coordination.

Owner:
------
Prajwal (AI / NLP / Response Generation)

Why this exists:
----------------
Coordinates the overall ticket resolution process by integrating
intent classification, similarity search, decision making, and response generation.

Responsibilities:
-----------------
- Coordinate ticket resolution pipeline
- Import and use specialized services
- Maintain resolver-specific plumbing

DO NOT:
-------
- Duplicate implementation of specialized services
- Access database directly
- Modify ticket status
"""

from app.services.response_generator import generate_response
from app.services.similarity_search import find_similar_ticket
from app.services.classifier import classify_intent
from app.services.decision import decide_resolution, ResolutionDecision


def resolve_ticket(new_message: str, resolved_tickets: list[dict], similarity_threshold: float = None) -> dict:
    """
    High-level ticket resolution coordination.
    
    Args:
        new_message: New ticket message to resolve
        resolved_tickets: List of resolved tickets for similarity search
        similarity_threshold: Optional threshold for similarity matching
        
    Returns:
        dict: Resolution result with intent, response, and decision
    """
    # Classify intent
    classification = classify_intent(new_message)
    intent = classification["intent"]
    confidence = classification["confidence"]
    
    # Find similar solution
    similar_result = find_similar_ticket(new_message, resolved_tickets, similarity_threshold)
    similar_solution = similar_result["ticket"]["response"] if similar_result else None
    
    # Generate response
    response = generate_response(intent, new_message, similar_solution)
    
    # Make decision
    decision = decide_resolution(confidence, similar_solution_found=similar_result is not None)
    
    return {
        "intent": intent,
        "confidence": confidence,
        "response": response,
        "decision": decision,
        "similar_ticket": similar_result
    }
