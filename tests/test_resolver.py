from app.services.resolver import generate_response


def test_resolver_returns_string():
    """
    Resolver must always return a string.
    """
    response = generate_response(
        intent="login_issue",
        original_message="Cannot login"
    )
    assert isinstance(response, str)


def test_resolver_uses_similar_solution():
    """
    If similar solution exists, reuse it.
    """
    response = generate_response(
        intent="login_issue",
        original_message="Cannot login",
        similar_solution="Reset your password"
    )
    assert response == "Reset your password"


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
