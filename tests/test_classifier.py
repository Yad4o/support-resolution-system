from app.services.classifier import classify_intent


def test_classifier_returns_dict():
    """
    Classifier must return a dictionary.
    """
    result = classify_intent("I cannot login")
    assert isinstance(result, dict)


def test_classifier_has_required_keys():
    """
    Classifier output must contain intent & confidence.
    """
    result = classify_intent("Login issue")
    assert "intent" in result
    assert "confidence" in result


def test_classifier_confidence_type():
    """
    Confidence must be float.
    """
    result = classify_intent("Payment failed")
    assert isinstance(result["confidence"], float)
