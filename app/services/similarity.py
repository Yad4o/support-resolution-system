"""
app/services/similarity.py

Purpose:
--------
Finds previously resolved tickets that are similar to a new incoming ticket.

Owner:
------
Prajwal (AI / NLP / Similarity Search)

Why this exists:
----------------
Many customer issues repeat.
If we can find a similar past ticket that was successfully resolved,
we can reuse its solution instead of generating a new one.

Responsibilities:
-----------------
- Convert text into vector representations
- Compare similarity between ticket texts
- Return the most similar past ticket (if any)

DO NOT:
-------
- Access database sessions directly
- Modify ticket records
- Make auto-resolution decisions
"""

from typing import Optional, Dict


def find_similar_ticket(
    new_text: str,
    resolved_tickets: list[str],
) -> Optional[Dict[str, float]]:
    """
    Find the most similar resolved ticket to a new ticket.

    Parameters:
    -----------
    new_text : str
        The text of the newly created support ticket.

    resolved_tickets : list[str]
        List of text messages from previously RESOLVED tickets.
        (These will be fetched by Om and passed into this function.)

    Returns:
    --------
    dict | None

    If similar ticket found:
    {
        "matched_text": "<text of similar ticket>",
        "similarity_score": 0.82
    }

    If no good match:
    None
    """

    # -------------------------------------------------
    # STEP 1: Preprocess text
    # -------------------------------------------------
    """
    TODO:
    - Lowercase text
    - Remove extra whitespace
    - Optional: remove stopwords
    """

    # -------------------------------------------------
    # STEP 2: Convert text to vectors
    # -------------------------------------------------
    """
    TODO (choose ONE approach):

    Option 1 (Simple, Fast MVP):
    ----------------------------
    - TF-IDF Vectorizer (sklearn)

    Option 2 (Better semantic meaning):
    -----------------------------------
    - Sentence embeddings (spaCy, sentence-transformers)

    Option 3 (Advanced):
    --------------------
    - OpenAI embeddings API
    """

    # -------------------------------------------------
    # STEP 3: Compute similarity
    # -------------------------------------------------
    """
    TODO:
    - Use cosine similarity
    - Compare new_text vector against all resolved ticket vectors
    """

    # -------------------------------------------------
    # STEP 4: Threshold decision
    # -------------------------------------------------
    """
    TODO:
    - Define similarity threshold (e.g., 0.75)
    - If highest score < threshold → return None
    """

    # -------------------------------------------------
    # STEP 5: Return best match
    # -------------------------------------------------
    """
    TODO:
    - Return matched ticket text + similarity score
    """

    return None
