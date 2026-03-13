import warnings
from typing import Dict, Union
from .intent_classifier import classify_intent as new_classify_intent, IntentResult


def classify_intent(text: str) -> Dict[str, float]:
    """
    Classify user intent using rule-based keyword matching.
    
    .. deprecated:: 
        Use app.services.intent_classifier.classify_intent instead.
        This function is deprecated and will be removed in a future version.

    Args:
        text (str): Raw user input text

    Returns:
        dict: {
            "intent": str,
            "confidence": float
        }
    """
    warnings.warn(
        "app.services.classifier.classify_intent is deprecated. "
        "Use app.services.intent_classifier.classify_intent instead.",
        DeprecationWarning,
        stacklevel=2
    )
    
    # Delegate to the new implementation and transform back to legacy dict format
    result = new_classify_intent(text)
    return {
        "intent": result["intent"],
        "confidence": result["confidence"]
    }
