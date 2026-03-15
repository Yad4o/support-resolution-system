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

Note:
-----
Canonical implementation lives in similarity_search.py.
This module re-exports it to match the name defined in the Phase 3 spec.
"""

# Canonical implementation — delegates to similarity_search.py
from app.services.similarity_search import find_similar_ticket

__all__ = ["find_similar_ticket"]
