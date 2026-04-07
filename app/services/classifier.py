"""
 =============================================================================
 SRS (Support Request System) - Intent Classification Service
 =============================================================================

Purpose:
--------
Advanced intent classification using rule-based keyword matching with
confidence scoring and sub-intent detection.

Features:
--------
- Boundary-aware keyword matching
- Confidence scoring with bonuses and penalties
- Sub-intent detection for granular classification
- Priority-based intent resolution
- Comprehensive pattern matching

Responsibilities:
-----------------
- Classify user messages into intent categories
- Provide confidence scores for classification
- Detect sub-intents for better routing
- Handle edge cases and fallback scenarios

Owner:
------
Backend Team

DO NOT:
-------
- Use external AI services (this is rule-based)
- Break existing keyword patterns
- Change confidence calculation logic
- Modify intent priority order without testing
"""

import logging
import re
from typing import Dict, Optional, List, Tuple

# Configure logger
logger = logging.getLogger(__name__)


def _boundary_match(keyword: str, text: str) -> bool:
    """
    Check if keyword appears as a whole word/phrase in text (boundary-aware matching).
    
    This function ensures that keywords match only as complete words or phrases,
    preventing false positives from partial matches within other words.
    
    Args:
        keyword: The keyword to match (can be multi-word)
        text: The text to search in
        
    Returns:
        True if keyword matches as a whole word/phrase
    """
    try:
        # Escape special regex characters in keyword
        escaped_keyword = re.escape(keyword)
        
        # Use word boundaries to match whole words only
        # For multi-word phrases, we need to handle boundaries differently
        if ' ' in keyword:
            # Multi-word phrase - check with word boundaries around the whole phrase
            pattern = r'\b' + escaped_keyword + r'\b'
        else:
            # Single word - use standard word boundaries
            pattern = r'\b' + escaped_keyword + r'\b'
            
        return bool(re.search(pattern, text, re.IGNORECASE))
        
    except Exception as e:
        logger.warning(f"Boundary match failed for keyword '{keyword}': {e}")
        return False


def _normalize_text(message: str) -> str:
    """
    Normalize text for consistent matching.
    
    Args:
        message: Original message text
        
    Returns:
        Normalized text
    """
    if not message or not isinstance(message, str):
        return ""
    
    # Normalize message
    text = message.lower().strip()
    
    # Clean text (remove special characters but keep spaces)
    text = re.sub(r"[^a-z0-9\s]", "", text)
    
    # Collapse multiple spaces
    text = re.sub(r"\s+", " ", text)
    
    return text


def _calculate_confidence(
    base_confidence: float,
    match_count: int,
    pattern_matches: int,
    text_length: int,
    intent: str,
    text: str
) -> float:
    """
    Calculate confidence score with bonuses and adjustments.
    
    Args:
        base_confidence: Base confidence for the intent
        match_count: Number of keyword matches
        pattern_matches: Number of pattern matches
        text_length: Length of normalized text
        intent: Intent type
        text: Normalized text
        
    Returns:
        Calculated confidence score (0.0-1.0)
    """
    if match_count == 0 and pattern_matches == 0:
        return 0.0
    
    # Calculate confidence based on matches and base confidence
    # More keywords matched = higher confidence
    match_bonus = min(match_count * 0.1, 0.3)  # Max 30% bonus
    pattern_bonus = pattern_matches * 0.15  # 15% bonus per pattern match
    
    calculated_confidence = min(base_confidence + match_bonus + pattern_bonus, 1.0)
    
    # Adjust for message length (longer messages get slight boost)
    if text_length > 50:
        calculated_confidence = min(calculated_confidence * 1.05, 1.0)
    elif text_length < 10:
        calculated_confidence *= 0.9
    
    # Special handling for general queries with "explain" + billing context
    if intent == "general_query" and _boundary_match("explain", text) and _boundary_match("billing", text):
        calculated_confidence = max(calculated_confidence, 0.95)
    
    # Special handling: reduce payment_issue confidence for "explain" queries without action verbs
    if intent == "payment_issue" and _boundary_match("explain", text) and _boundary_match("billing", text):
        # Check if this is an informational query (no action verbs like charge, failed, etc.)
        action_verbs = ["charge", "charged", "failed", "declined", "debit", "refund", "transaction"]
        has_action_verb = any(_boundary_match(verb, text) for verb in action_verbs)
        if not has_action_verb:
            calculated_confidence *= 0.7  # Reduce confidence for informational queries
    
    # Special handling: if account_issue has account keywords, give it priority
    if intent == "account_issue" and any(_boundary_match(kw, text) for kw in ["account", "delete", "profile"]):
        calculated_confidence = max(calculated_confidence, 0.9)

    # Special handling: locked/blocked/suspended are login signals even when "account" is present
    if intent == "login_issue" and any(_boundary_match(kw, text) for kw in ["locked", "blocked", "suspended", "attempts", "2fa", "two factor"]):
        calculated_confidence = max(calculated_confidence, 0.92)
    
    return calculated_confidence


def _detect_sub_intent(intent: str, text: str) -> Optional[str]:
    """
    Detect sub-intent based on keyword patterns.
    
    Args:
        intent: Primary intent
        text: Normalized text
        
    Returns:
        Sub-intent if detected, None otherwise
    """
    sub_intent_patterns: Dict[str, List[Tuple[str, List[str]]]] = {
        "login_issue": [
            ("password_reset",    ["forgot", "reset", "remember", "lost", "recovery"]),
            ("account_locked",    ["locked", "lock", "blocked", "2fa", "two factor", "suspended", "attempts"]),
            ("wrong_credentials", ["credentials", "wrong", "invalid"]),
        ],
        "payment_issue": [
            ("duplicate_charge",  ["twice", "double", "duplicate", "refund", "unexpected"]),
            ("payment_declined",  ["declined", "failed", "rejected"]),
            ("billing_question",  ["invoice", "receipt", "plan", "pricing"]),
        ],
        "account_issue": [
            ("delete_account",    ["delete", "remove", "close", "cancel", "deactivate", "gdpr"]),
            ("update_info",       ["update", "change", "edit", "email", "phone", "name", "profile"]),
        ],
        "technical_issue": [
            ("crash_error",       ["crash", "error", "bug", "broken", "not working", "fails"]),
            ("performance",       ["slow", "loading", "lag", "freeze", "timeout"]),
        ],
        "feature_request": [
            ("new_feature",       ["add", "new", "build", "implement", "wish"]),
            ("improvement",       ["improve", "better", "enhance"]),
        ],
        "general_query": [
            ("how_to",            ["how", "steps", "guide", "tutorial"]),
            ("pricing_plan",      ["price", "cost", "plan", "upgrade"]),
        ],
    }

    for sub_intent_name, keywords in sub_intent_patterns.get(intent, []):
        if any(kw in text for kw in keywords):
            return sub_intent_name
    
    return None


def classify_intent(message: str) -> Dict:
    """
    Classify user intent using rule-based keyword matching.
    
    This is the first step in the AI pipeline. It analyzes the user's message
    to determine the primary intent and confidence score, with optional sub-intent
    detection for more granular routing.
    
    Reference: Technical Spec § 9.1 (Intent Classification)

    Args:
        message: Raw ticket message from user

    Returns:
        Dictionary containing:
        - intent: Primary intent category
        - confidence: Confidence score (0.0-1.0)
        - sub_intent: Optional sub-intent for granular classification
    """
    try:
        # Input validation
        if not message or not isinstance(message, str):
            logger.debug("Invalid message input for classification")
            return {
                "intent": "unknown",
                "confidence": 0.0,
                "sub_intent": None,
            }

        # Normalize message
        text = _normalize_text(message)
        
        # Handle very short messages
        if len(text) < 3:
            logger.debug("Message too short for classification")
            return {
                "intent": "unknown",
                "confidence": 0.0,
                "sub_intent": None,
            }

        # -------- Intent Classification Rules -------- #
        
        intent_patterns = {
            "login_issue": {
                "keywords": [
                    "login", "signin", "sign in", "log in", "authentication", "password",
                    "credentials", "access", "account access", "cant login", "unable to login",
                    "forgot password", "reset password", "locked out", "account locked",
                    "sign in issue", "login problem", "authentication failed",
                    "locked", "blocked", "suspended", "2fa", "two factor", "attempts"
                ],
                "confidence": 0.85
            },
            "payment_issue": {
                "keywords": [
                    "payment", "billing", "charge", "charged", "transaction", "credit card",
                    "debit card", "invoice", "receipt", "refund", "payment failed",
                    "billing issue", "payment problem", "overcharged", "double charge",
                    "payment declined", "wrong charge", "money", "cost", "price"
                ],
                "confidence": 0.9
            },
            "account_issue": {
                "keywords": [
                    "account", "profile", "settings", "personal information", "email",
                    "phone number", "address", "update account", "delete account",
                    "account settings", "profile update", "change email", "change phone",
                    "deactivate", "suspend", "close account", "personal data"
                ],
                "confidence": 0.8
            },
            "technical_issue": {
                "keywords": [
                    "error", "bug", "crash", "slow", "performance", "broken", "not working",
                    "glitch", "issue", "problem", "technical", "system", "server",
                    "down", "unavailable", "timeout", "loading", "freeze", "frozen",
                    "crashing", "fails", "failed", "malfunction"
                ],
                "confidence": 0.75
            },
            "feature_request": {
                "keywords": [
                    "feature", "request", "suggestion", "improvement", "enhancement",
                    "add", "implement", "new feature", "would like", "wish", "hope",
                    "suggest", "recommend", "feedback", "idea", "could you", "can you",
                    "would be great", "nice to have", "should have",
                    "improve", "better", "enhance", "search"
                ],
                "confidence": 0.8
            },
            "general_query": {
                "keywords": [
                    "question", "help", "how", "what", "where", "when", "why", "information",
                    "clarification", "explain", "understand", "guide", "tutorial",
                    "documentation", "support", "assistance", "contact", "info"
                ],
                "patterns": [
                    r"how (?:do|can|should|would)",
                    r"what (?:is|are|do|can)",
                    r"where (?:can|do|is)",
                    r"when (?:can|do|is)",
                    r"why (?:do|can|is)",
                    r"explain (?:please|kindly)",
                    r"help (?:me|with)",
                    r"contact (?:support|you)"
                ],
                "confidence": 0.7
            }
        }

        # -------- Matching Logic -------- #
        
        best_match = None
        highest_score = 0
        
        # Priority order: more specific intents first
        intent_priority = [
            "payment_issue",
            "login_issue", 
            "account_issue",
            "technical_issue",
            "feature_request",
            "general_query"
        ]
        
        # Reorder intents by priority
        ordered_intents = {}
        for intent in intent_priority:
            if intent in intent_patterns:
                ordered_intents[intent] = intent_patterns[intent]
        
        # Match intents and calculate confidence
        for intent, config in ordered_intents.items():
            keywords = config["keywords"]
            base_confidence = config["confidence"]
            patterns = config.get("patterns", [])
            
            # Count keyword matches
            match_count = 0
            pattern_matches = 0
            
            for keyword in keywords:
                if _boundary_match(keyword, text):
                    match_count += 1
            
            # Check pattern matches (higher weight)
            for pattern in patterns:
                if re.search(pattern, text):
                    pattern_matches += 1
            
            if match_count > 0 or pattern_matches > 0:
                # Calculate confidence with all adjustments
                calculated_confidence = _calculate_confidence(
                    base_confidence, match_count, pattern_matches, 
                    len(text), intent, text
                )
                
                if calculated_confidence > highest_score:
                    highest_score = calculated_confidence
                    best_match = intent
                elif calculated_confidence == highest_score and best_match:
                    # Tie-breaker: use priority order (earlier in intent_priority wins)
                    current_priority = intent_priority.index(intent) if intent in intent_priority else len(intent_priority)
                    best_priority = intent_priority.index(best_match) if best_match in intent_priority else len(intent_priority)
                    if current_priority < best_priority:
                        highest_score = calculated_confidence
                        best_match = intent

        # -------- Sub-intent Detection -------- #
        
        sub_intent = None
        if best_match:
            sub_intent = _detect_sub_intent(best_match, text)

        # -------- Return Result -------- #
        
        if best_match:
            result = {
                "intent": best_match,
                "confidence": round(highest_score, 3),
                "sub_intent": sub_intent,
            }
            logger.debug(f"Classification result: {result}")
            return result
        
        # -------- Fallback -------- #
        
        logger.debug("No intent matched, returning unknown")
        return {
            "intent": "unknown",
            "confidence": 0.2,
            "sub_intent": None,
        }
        
    except Exception as e:
        logger.error(f"Error during intent classification: {e}")
        return {
            "intent": "unknown",
            "confidence": 0.0,
            "sub_intent": None,
        }
