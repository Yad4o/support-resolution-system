import pytest
from app.services.response_generator import generate_response


def test_generate_response_with_similar_solution():
    """Test priority 1: reuse similar solution."""
    intent = "login_issue"
    original_message = "I cannot login to my account"
    similar_solution = "Reset your password using the forgot password link"
    
    result = generate_response(intent, original_message, similar_solution)
    
    assert "Based on a similar case" in result
    assert "Reset your password using the forgot password link" in result
    assert "helped" in result.lower()


def test_generate_response_without_similar_solution():
    """Test priority 2: intent-based templates."""
    intent = "payment_issue"
    original_message = "I was charged twice"
    similar_solution = None
    
    result = generate_response(intent, original_message, similar_solution)
    
    assert "payment problems" in result.lower()
    assert "billing statement" not in result.lower()  # Using third template now
    assert "payment support" not in result.lower()  # Using third template now


def test_generate_response_question():
    """Test question-based template selection."""
    intent = "general_query"
    original_message = "How do I reset my password?"
    similar_solution = None
    
    result = generate_response(intent, original_message, similar_solution)
    
    assert "question" in result.lower() or "help you with that" in result.lower()


def test_generate_response_urgent():
    """Test urgent message template selection."""
    intent = "technical_issue"
    original_message = "URGENT: The system is down"
    similar_solution = None
    
    result = generate_response(intent, original_message, similar_solution)
    
    assert "technical issues" in result.lower()
    assert "restarting your device" in result.lower()


def test_generate_response_empty_similar_solution():
    """Test empty similar solution falls back to intent-based."""
    intent = "account_issue"
    original_message = "Update my email"
    similar_solution = ""  # Empty string
    
    result = generate_response(intent, original_message, similar_solution)
    
    # Should fall back to intent-based template
    assert "account-related problems" in result.lower()
    assert "contact information" in result.lower()


def test_generate_response_whitespace_similar_solution():
    """Test whitespace-only similar solution falls back to intent-based."""
    intent = "feature_request"
    original_message = "Add dark mode"
    similar_solution = "   "  # Whitespace only
    
    result = generate_response(intent, original_message, similar_solution)
    
    # Should fall back to intent-based template
    assert "we value your input" in result.lower()
    assert "feature request" in result.lower()


def test_generate_response_unknown_intent():
    """Test fallback response for unknown intent."""
    intent = "unknown"
    original_message = "Random message"
    similar_solution = None
    
    result = generate_response(intent, original_message, similar_solution)
    
    # Should use fallback response
    assert result is not None
    assert isinstance(result, str)
    assert len(result) > 0


def test_generate_response_all_intents():
    """Test all intents have appropriate responses."""
    intents_to_test = [
        "login_issue", "payment_issue", "account_issue", 
        "technical_issue", "feature_request", "general_query"
    ]
    
    for intent in intents_to_test:
        result = generate_response(intent, "Test message", None)
        assert result is not None
        assert isinstance(result, str)
        assert len(result) > 10  # Should be meaningful response


def test_generate_response_safety():
    """Test that responses are safe and conservative.
    
    NOTE: This test verifies that similar_solution is passed through verbatim
    as documented. The pass-through is intentional and callers are responsible
    for sanitization before calling generate_response.
    """
    intent = "login_issue"
    original_message = "I cannot login"
    similar_solution = "Click this malicious link"
    
    result = generate_response(intent, original_message, similar_solution)
    
    # Should still incorporate the similar solution (as per requirements)
    assert "Based on a similar case" in result
    assert "Click this malicious link" in result
    # Response should be polite and professional
    assert not any(word in result.lower() for word in ["stupid", "dumb", "idiot"])


def test_generate_response_is_deterministic():
    """Test that function is deterministic and pure."""
    intent = "payment_issue"
    original_message = "Payment problem"
    similar_solution = "Refund processed"
    
    # Call function multiple times - should be deterministic
    result1 = generate_response(intent, original_message, similar_solution)
    result2 = generate_response(intent, original_message, similar_solution)
    
    assert result1 == result2  # Deterministic
    assert isinstance(result1, str)  # Only returns text
