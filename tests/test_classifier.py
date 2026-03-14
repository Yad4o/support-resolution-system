import pytest
import warnings
<<<<<<< HEAD
=======
from app.services.classifier import classify_intent
from app.services.intent_classifier import classify_intent as new_classify_intent


def test_legacy_classifier_delegates_to_new_implementation():
    """Test that legacy classifier delegates to new implementation with deprecation warning."""
    message = "I cannot login to my account"
    
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")  # Capture all warnings
        
        # Call legacy function
        legacy_result = classify_intent(message)
        
        # Call new function directly
        new_result = new_classify_intent(message)
        
        # Should have raised a deprecation warning
        assert len(w) == 1
        assert issubclass(w[0].category, DeprecationWarning)
        assert "deprecated" in str(w[0].message).lower()
        assert "intent_classifier" in str(w[0].message)
        
        # Results should be identical
        assert legacy_result == new_result


import warnings
>>>>>>> feat/task3.2-similarity-search
from app.services.classifier import classify_intent
from app.services.intent_classifier import classify_intent as new_classify_intent


<<<<<<< HEAD
def test_legacy_classifier_delegates_to_new_implementation():
    """Test that legacy classifier delegates to new implementation with deprecation warning."""
    message = "I cannot login to my account"
    
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")  # Capture all warnings
        
        # Call legacy function
        legacy_result = classify_intent(message)
        
        # Call new function directly
        new_result = new_classify_intent(message)
        
        # Should have raised a deprecation warning
        assert len(w) == 1
        assert issubclass(w[0].category, DeprecationWarning)
        assert "deprecated" in str(w[0].message).lower()
        assert "intent_classifier" in str(w[0].message)
        
        # Results should be identical
        assert legacy_result == new_result


def test_legacy_classifier_login_issue():
    result = classify_intent("I cannot login to my account")
=======
def test_legacy_classifier_login_issue():
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        result = classify_intent("I cannot login to my account")
>>>>>>> feat/task3.2-similarity-search
    assert result["intent"] == "login_issue"
    assert result["confidence"] > 0.0


def test_legacy_classifier_payment_issue():
<<<<<<< HEAD
    result = classify_intent("My payment was debited twice")
=======
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        result = classify_intent("My payment was debited twice")
>>>>>>> feat/task3.2-similarity-search
    assert result["intent"] == "payment_issue"
    assert result["confidence"] > 0.0


def test_legacy_classifier_account_issue():
<<<<<<< HEAD
    result = classify_intent("Please delete my account")
=======
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        result = classify_intent("Please delete my account")
>>>>>>> feat/task3.2-similarity-search
    assert result["intent"] == "account_issue"
    assert result["confidence"] > 0.0


def test_legacy_classifier_technical_issue():
<<<<<<< HEAD
    result = classify_intent("The app is crashing with an error")
=======
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        result = classify_intent("The app is crashing with an error")
>>>>>>> feat/task3.2-similarity-search
    assert result["intent"] == "technical_issue"
    assert result["confidence"] > 0.0


def test_legacy_classifier_feature_request():
<<<<<<< HEAD
    result = classify_intent("Please add a dark mode feature")
=======
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        result = classify_intent("Please add a dark mode feature")
>>>>>>> feat/task3.2-similarity-search
    assert result["intent"] == "feature_request"
    assert result["confidence"] > 0.0


def test_legacy_classifier_general_query():
<<<<<<< HEAD
    result = classify_intent("How can I use this app?")
=======
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        result = classify_intent("How can I use this app?")
>>>>>>> feat/task3.2-similarity-search
    assert result["intent"] == "general_query"
    assert result["confidence"] > 0.0


def test_legacy_classifier_unknown_intent():
<<<<<<< HEAD
    result = classify_intent("blabla xyz random text")
=======
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        result = classify_intent("blabla xyz random text")
>>>>>>> feat/task3.2-similarity-search
    assert result["intent"] == "unknown"
    assert result["confidence"] >= 0.0


def test_legacy_classifier_empty_string():
<<<<<<< HEAD
    result = classify_intent("")
=======
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        result = classify_intent("")
>>>>>>> feat/task3.2-similarity-search
    assert result["intent"] == "unknown"
    assert result["confidence"] == 0.0


def test_legacy_classifier_none_input():
<<<<<<< HEAD
    result = classify_intent(None)
=======
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        result = classify_intent(None)
>>>>>>> feat/task3.2-similarity-search
    assert result["intent"] == "unknown"
    assert result["confidence"] == 0.0


def test_legacy_classifier_special_characters_cleanup():
<<<<<<< HEAD
    result = classify_intent("!!! LOGIN??? ###")
=======
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        result = classify_intent("!!! LOGIN??? ###")
>>>>>>> feat/task3.2-similarity-search
    assert result["intent"] == "login_issue"
    assert result["confidence"] > 0.0
