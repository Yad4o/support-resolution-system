"""
app/services/classifier.py

Purpose:
--------
Classifies customer support ticket messages into predefined intents.

Owner:
------
Prajwal (AI / NLP)

Responsibilities:
-----------------
- Analyze raw text input
- Predict intent category
- Return confidence score

DO NOT:
-------
- Access database here
- Update ticket status here
- Decide auto vs escalate here
"""

from typing import Dict


def classify_intent(text: str) -> Dict[str, float | str]:
    """
    Classify the intent of a support ticket message.

    Input:
    ------
    text: str
        Raw customer message

    Output:
    -------
    dict with keys:
    - intent: predicted intent label
    - confidence: confidence score (0.0 – 1.0)

    TODO (Implementation Ideas):
    ----------------------------
    - Rule-based keywords (initial)
    - spaCy text classification
    - OpenAI prompt-based classification
    """

    # TODO: Implement actual NLP logic
    return {
        "intent": "unknown",
        "confidence": 0.0,
    }
