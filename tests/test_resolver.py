from app.services.response_generator import generate_response


def test_resolver_returns_string():
    """
    Response generator must always return a string.
    """
    response = generate_response(
        intent="login_issue",
        original_message="Cannot login"
    )
    assert isinstance(response, str)


def test_resolver_uses_similar_solution():
    """
    If similar solution exists, reuse it with polite wrapper.
    """
    response = generate_response(
        intent="login_issue",
        original_message="Cannot login",
        similar_solution="Reset your password"
    )
    assert "I understand you're experiencing an issue" in response
    assert "Based on a similar case" in response
    assert "Reset your password" in response


def test_resolver_fallback_response():
    """
    Unknown intent should return safe fallback.
    """
    response = generate_response(
        intent="unknown",
        original_message="Something wrong"
    )
    assert isinstance(response, str)
    assert len(response) > 0
