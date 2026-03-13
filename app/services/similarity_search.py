"""
Ticket Similarity Search Service

This service finds previously resolved tickets that match a new ticket's message.
If a similar resolved ticket exists, its solution can be reused for better accuracy and consistency.

Reference: Technical Spec § 9.2 (Similarity Search)
"""

import re
import math
from typing import Dict, List, Optional, TypedDict, Union
from collections import Counter, defaultdict


class SimilarTicketResult(TypedDict):
    """Result of similarity search."""
    matched_text: str
    similarity_score: float


class SimilaritySearchService:
    """
    Ticket similarity search service.
    
    MVP: Simple text similarity using TF-IDF and cosine similarity
    Future: Embeddings and vector database integration
    """
    
    def __init__(self, similarity_threshold: float = 0.7):
        """
        Initialize the similarity search service.
        
        Args:
            similarity_threshold: Minimum similarity score to consider a match (0.0-1.0)
        """
        self.similarity_threshold = similarity_threshold
    
    def _preprocess_text(self, text: str) -> List[str]:
        """
        Preprocess text for similarity analysis.
        
        Args:
            text: Raw text to preprocess
            
        Returns:
            List of processed tokens
        """
        if not text or not isinstance(text, str):
            return []
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters and numbers, keep letters and spaces
        text = re.sub(r'[^a-z\s]', ' ', text)
        
        # Replace multiple spaces with single space
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Tokenize and filter out very short words
        tokens = [token for token in text.split() if len(token) > 1]
        
        return tokens
    
    def _calculate_tf_idf(self, documents: List[List[str]]) -> Dict[str, Dict[str, float]]:
        """
        Calculate TF-IDF scores for a collection of documents.
        
        Args:
            documents: List of tokenized documents
            
        Returns:
            Dictionary with TF-IDF scores for each document
        """
        # Calculate term frequency for each document
        tf_scores = []
        for doc in documents:
            if not doc:
                tf_scores.append({})
                continue
            
            term_count = Counter(doc)
            total_terms = len(doc)
            tf = {term: count / total_terms for term, count in term_count.items()}
            tf_scores.append(tf)
        
        # Calculate document frequency for each term
        df = defaultdict(int)
        for doc in documents:
            unique_terms = set(doc)
            for term in unique_terms:
                df[term] += 1
        
        # Calculate IDF for each term
        total_docs = len(documents)
        idf = {term: math.log(total_docs / count) for term, count in df.items()}
        
        # Calculate TF-IDF for each document
        tfidf_scores = []
        for tf in tf_scores:
            tfidf = {term: tf_score * idf[term] for term, tf_score in tf.items()}
            tfidf_scores.append(tfidf)
        
        return tfidf_scores
    
    def _cosine_similarity(self, vec1: Dict[str, float], vec2: Dict[str, float]) -> float:
        """
        Calculate cosine similarity between two TF-IDF vectors.
        
        Args:
            vec1: First TF-IDF vector
            vec2: Second TF-IDF vector
            
        Returns:
            Cosine similarity score (0.0-1.0)
        """
        # Get common terms
        common_terms = set(vec1.keys()) & set(vec2.keys())
        
        if not common_terms:
            return 0.0
        
        # Calculate dot product
        dot_product = sum(vec1[term] * vec2[term] for term in common_terms)
        
        # Calculate magnitudes
        mag1 = math.sqrt(sum(val ** 2 for val in vec1.values()))
        mag2 = math.sqrt(sum(val ** 2 for val in vec2.values()))
        
        if mag1 == 0 or mag2 == 0:
            return 0.0
        
        # Calculate cosine similarity
        similarity = dot_product / (mag1 * mag2)
        
        return min(similarity, 1.0)  # Ensure max 1.0
    
    def find_similar_ticket(
        self, 
        new_message: str, 
        resolved_tickets: List[Dict[str, Union[str, Dict]]]
    ) -> Optional[SimilarTicketResult]:
        """
        Find the most similar resolved ticket for a new message.
        
        Args:
            new_message: New ticket message to find matches for
            resolved_tickets: List of resolved ticket objects with 'message' and optional 'response'
            
        Returns:
            Dictionary with matched text and similarity score, or None if no match above threshold
        """
        if not new_message or not isinstance(new_message, str):
            return None
        
        if not resolved_tickets or not isinstance(resolved_tickets, list):
            return None
        
        # Filter out invalid tickets
        valid_tickets = [
            ticket for ticket in resolved_tickets 
            if isinstance(ticket, dict) and 'message' in ticket and ticket['message']
        ]
        
        if not valid_tickets:
            return None
        
        # Preprocess new message
        new_tokens = self._preprocess_text(new_message)
        if not new_tokens:
            return None
        
        # Preprocess all resolved ticket messages
        ticket_messages = [ticket['message'] for ticket in valid_tickets]
        ticket_tokens = [self._preprocess_text(msg) for msg in ticket_messages]
        
        # Calculate TF-IDF for all documents (new message + all tickets)
        all_documents = [new_tokens] + ticket_tokens
        tfidf_scores = self._calculate_tf_idf(all_documents)
        
        # Calculate similarity with each ticket
        best_match = None
        best_score = 0.0
        best_index = -1
        
        new_tfidf = tfidf_scores[0]
        
        for i, ticket_tfidf in enumerate(tfidf_scores[1:], 1):
            similarity = self._cosine_similarity(new_tfidf, ticket_tfidf)
            
            if similarity > best_score:
                best_score = similarity
                best_index = i - 1  # Adjust index back to ticket list
                best_match = valid_tickets[best_index]
        
        # Check if best match meets threshold
        if best_score >= self.similarity_threshold and best_match:
            return SimilarTicketResult(
                matched_text=best_match['message'],
                similarity_score=best_score
            )
        
        return None


# Global instance for easy access
similarity_search = SimilaritySearchService()


def find_similar_ticket(
    new_message: str, 
    resolved_tickets: List[Dict[str, Union[str, Dict]]]
) -> Optional[SimilarTicketResult]:
    """
    Convenience function for ticket similarity search.
    
    Args:
        new_message: New ticket message to find matches for
        resolved_tickets: List of resolved ticket objects with 'message' and optional 'response'
        
    Returns:
        Dictionary with matched text and similarity score, or None if no match above threshold
        
    Example:
        >>> resolved_tickets = [
        ...     {"message": "I can't login to my account", "response": "Check your password"},
        ...     {"message": "Payment was declined", "response": "Contact your bank"}
        ... ]
        >>> result = find_similar_ticket("Unable to sign in", resolved_tickets)
        >>> print(result)
        {"matched_text": "I can't login to my account", "similarity_score": 0.85}
    """
    return similarity_search.find_similar_ticket(new_message, resolved_tickets)
