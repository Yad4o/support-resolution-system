"""
============================================================================
SRS (Support Request System) - Decision Engine Service
============================================================================

Purpose:
--------
Safety gate for determining whether tickets should be auto-resolved or escalated
to human agents based on confidence thresholds.

Features:
--------
- Confidence-based decision making
- Comprehensive input validation
- Safety-first approach (escalate on uncertainty)
- Configurable confidence thresholds
- Detailed logging and audit trail

Responsibilities:
-----------------
- Make auto-resolution vs escalation decisions
- Validate confidence scores
- Provide safety checks for edge cases
- Support threshold configuration for testing

Owner:
------
Backend Team

DO NOT:
-------
- Change the safety-first principle
- Modify validation logic without testing
- Remove logging for audit purposes
"""

import logging
from typing import Literal, Optional

from app.core.config import settings
from app.utils.service_helpers import MetricsHelper

# Configure logger
logger = logging.getLogger(__name__)


def _validate_confidence(confidence: float) -> Optional[str]:
    """
    Validate confidence score with comprehensive checks.
    
    Args:
        confidence: Confidence score to validate
        
    Returns:
        Error message if invalid, None if valid
    """
    # Type validation
    if not isinstance(confidence, (int, float)):
        return "Confidence must be numeric"
    
    # Boolean check (bool is subclass of int, but we don't want it)
    if isinstance(confidence, bool):
        return "Confidence must be numeric, not boolean"
    
    # NaN check
    if confidence != confidence:
        return "Confidence cannot be NaN"
    
    # Range validation
    if not (0.0 <= confidence <= 1.0):
        return "Confidence must be between 0.0 and 1.0"
    
    return None


def decide_resolution(confidence: float) -> Literal["AUTO_RESOLVE", "ESCALATE"]:
    """
    Decide whether a ticket should be auto-resolved or escalated to a human.
    
    This is the safety gate that determines if AI-generated responses are
    confident enough for automatic resolution or need human intervention.
    The function follows a safety-first approach - when in doubt, escalate.
    
    Reference: Technical Spec § 9.4 (Decision Engine)
    
    Args:
        confidence: Confidence score from intent classification (0.0-1.0)
        
    Returns:
        Decision string: "AUTO_RESOLVE" or "ESCALATE"
        
    Rules:
    - confidence >= threshold -> AUTO_RESOLVE
    - confidence < threshold -> ESCALATE
    - invalid/missing confidence -> ESCALATE (safety first)
    
    Safety Principles:
    - Always escalate on uncertainty
    - Validate all inputs thoroughly
    - Log decisions for audit purposes
    """
    try:
        # Input validation with comprehensive checks
        validation_error = _validate_confidence(confidence)
        if validation_error:
            logger.warning(f"Invalid confidence score {confidence}: {validation_error} - escalating")
            MetricsHelper.increment_counter("decision_invalid_confidence")
            return "ESCALATE"
        
        # Get threshold from settings
        threshold = settings.CONFIDENCE_THRESHOLD_AUTO_RESOLVE
        
        # Log the decision process
        logger.debug(f"Decision evaluation: confidence={confidence:.3f}, threshold={threshold:.3f}")
        
        # Make decision based on confidence threshold
        if confidence >= threshold:
            logger.info(f"Auto-resolving ticket: confidence={confidence:.3f} >= threshold={threshold:.3f}")
            MetricsHelper.increment_counter("decision_auto_resolve")
            return "AUTO_RESOLVE"
        else:
            logger.info(f"Escalating ticket: confidence={confidence:.3f} < threshold={threshold:.3f}")
            MetricsHelper.increment_counter("decision_escalate")
            return "ESCALATE"
            
    except Exception as e:
        # Safety first: escalate on any error
        logger.error(f"Error in decision engine: {e} - escalating")
        MetricsHelper.increment_counter("decision_error")
        return "ESCALATE"


def get_confidence_threshold() -> float:
    """
    Get the current confidence threshold for auto-resolution.
    
    Returns:
        Current confidence threshold value
    """
    try:
        threshold = settings.CONFIDENCE_THRESHOLD_AUTO_RESOLVE
        logger.debug(f"Current confidence threshold: {threshold}")
        return threshold
    except Exception as e:
        logger.error(f"Error getting confidence threshold: {e}")
        # Return a safe default
        return 0.7


def set_confidence_threshold(threshold: float) -> None:
    """
    Set the confidence threshold for auto-resolution.
    
    WARNING: This is for testing/configuration purposes only.
    In production, the threshold should come from settings.
    
    Args:
        threshold: New confidence threshold (0.0-1.0)
        
    Raises:
        ValueError: If threshold is invalid
    """
    try:
        # Validate threshold
        validation_error = _validate_confidence(threshold)
        if validation_error:
            raise ValueError(validation_error)
        
        # Update the settings object (for testing only)
        old_threshold = settings.CONFIDENCE_THRESHOLD_AUTO_RESOLVE
        settings.CONFIDENCE_THRESHOLD_AUTO_RESOLVE = threshold
        
        logger.info(f"Confidence threshold updated: {old_threshold} -> {threshold}")
        MetricsHelper.increment_counter("threshold_updated", tags={"old": str(old_threshold), "new": str(threshold)})
        
    except ValueError:
        raise
    except Exception as e:
        logger.error(f"Error setting confidence threshold: {e}")
        raise ValueError(f"Failed to set threshold: {e}")


def get_decision_stats() -> dict:
    """
    Get decision statistics for monitoring.
    
    Returns:
        Dictionary with decision statistics
    """
    try:
        auto_resolve_count = len(MetricsHelper.get_metrics("decision_auto_resolve"))
        escalate_count = len(MetricsHelper.get_metrics("decision_escalate"))
        invalid_count = len(MetricsHelper.get_metrics("decision_invalid_confidence"))
        error_count = len(MetricsHelper.get_metrics("decision_error"))
        
        total_decisions = auto_resolve_count + escalate_count + invalid_count + error_count
        
        return {
            "total_decisions": total_decisions,
            "auto_resolve_count": auto_resolve_count,
            "escalate_count": escalate_count,
            "invalid_confidence_count": invalid_count,
            "error_count": error_count,
            "auto_resolve_rate": auto_resolve_count / total_decisions if total_decisions > 0 else 0,
            "escalate_rate": escalate_count / total_decisions if total_decisions > 0 else 0,
            "current_threshold": get_confidence_threshold()
        }
        
    except Exception as e:
        logger.error(f"Error getting decision stats: {e}")
        return {
            "error": "Failed to retrieve statistics",
            "current_threshold": get_confidence_threshold()
        }


def reset_decision_stats() -> None:
    """
    Reset decision statistics (for testing purposes).
    
    Note: This should only be used in testing environments.
    """
    try:
        MetricsHelper._metrics.clear()
        logger.info("Decision statistics reset")
    except Exception as e:
        logger.error(f"Error resetting decision stats: {e}")
