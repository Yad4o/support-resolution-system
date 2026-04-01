"""
Tests for OpenAI integration in response generator with proper fallback chain.
"""
import pytest
from unittest.mock import patch, MagicMock
from app.services.response_generator import generate_response


def test_generate_response_openai_fallback_to_template():
    """Test that when OpenAI fails, function falls back to template response."""
    
    # Mock OpenAI to raise an exception
    with patch('app.services.response_generator.settings') as mock_settings:
        mock_settings.AI_PROVIDER = "openai"
        mock_settings.OPENAI_API_KEY = "test-key"
        
        with patch('app.services.response_generator._call_openai') as mock_call_openai:
            mock_call_openai.return_value = None  # Simulate OpenAI failure
            
            # Call generate_response
            response_text, source_label = generate_response(
                intent="login_issue",
                original_message="I forgot my password",
                similar_solution=None,
                sub_intent="password_reset",
                similar_quality_score=None
            )
            
            # Should fall back to template
            assert source_label == "template"
            assert "reset your password" in response_text.lower()
            assert "Click 'Forgot Password'" in response_text


def test_generate_response_openai_success():
    """Test that when OpenAI succeeds, function returns OpenAI response."""
    
    # Mock OpenAI to return a response
    with patch('app.services.response_generator.settings') as mock_settings:
        mock_settings.AI_PROVIDER = "openai"
        mock_settings.OPENAI_API_KEY = "test-key"
        
        with patch('app.services.response_generator._call_openai') as mock_call_openai:
            mock_call_openai.return_value = "Test OpenAI response for password reset"
            
            # Call generate_response
            response_text, source_label = generate_response(
                intent="login_issue",
                original_message="I forgot my password",
                similar_solution=None,
                sub_intent="password_reset",
                similar_quality_score=None
            )
            
            # Should use OpenAI response
            assert source_label == "openai"
            assert response_text == "Test OpenAI response for password reset"


def test_generate_response_similarity_priority():
    """Test that high-quality similar solution takes priority over OpenAI."""
    
    with patch('app.services.response_generator.settings') as mock_settings:
        mock_settings.AI_PROVIDER = "openai"
        mock_settings.OPENAI_API_KEY = "test-key"
        
        with patch('app.services.response_generator._call_openai') as mock_call_openai:
            mock_call_openai.return_value = "Test OpenAI response"
            
            # Call generate_response with high-quality similar solution
            response_text, source_label = generate_response(
                intent="login_issue",
                original_message="I forgot my password",
                similar_solution="Use the forgot password link and check your email",
                sub_intent="password_reset",
                similar_quality_score=0.8  # High quality score
            )
            
            # Should use similar solution (sanitized to 500 chars)
            assert source_label == "similarity"
            assert "Use the forgot password link" in response_text
            assert len(response_text) <= 500 + len("I understand you're experiencing an issue. Based on a similar case, here's what helped: ")


def test_generate_response_similarity_low_quality():
    """Test that low-quality similar solution falls back to OpenAI."""
    
    with patch('app.services.response_generator.settings') as mock_settings:
        mock_settings.AI_PROVIDER = "openai"
        mock_settings.OPENAI_API_KEY = "test-key"
        
        with patch('app.services.response_generator._call_openai') as mock_call_openai:
            mock_call_openai.return_value = "Test OpenAI response"
            
            # Call generate_response with low-quality similar solution
            response_text, source_label = generate_response(
                intent="login_issue",
                original_message="I forgot my password",
                similar_solution="Use the forgot password link",
                sub_intent="password_reset",
                similar_quality_score=0.4  # Low quality score
            )
            
            # Should fall back to OpenAI (not similarity)
            assert source_label == "openai"
            assert response_text == "Test OpenAI response"


def test_generate_response_no_openai_config():
    """Test that when OpenAI is not configured, function falls back to template."""
    
    with patch('app.services.response_generator.settings') as mock_settings:
        mock_settings.AI_PROVIDER = "openai"
        mock_settings.OPENAI_API_KEY = None  # No API key configured
        
        with patch('app.services.response_generator._call_openai') as mock_call_openai:
            mock_call_openai.return_value = "Test OpenAI response"
            
            # Call generate_response
            response_text, source_label = generate_response(
                intent="login_issue",
                original_message="I forgot my password",
                similar_solution=None,
                sub_intent="password_reset",
                similar_quality_score=None
            )
            
            # Should fall back to template (not call OpenAI)
            assert source_label == "template"
            assert "reset your password" in response_text.lower()
            mock_call_openai.assert_not_called()  # OpenAI should not be called


def test_generate_response_fallback_chain():
    """Test complete fallback chain: similarity -> OpenAI -> template -> fallback."""
    
    with patch('app.services.response_generator.settings') as mock_settings:
        mock_settings.AI_PROVIDER = "openai"
        mock_settings.OPENAI_API_KEY = "test-key"
        
        with patch('app.services.response_generator._call_openai') as mock_call_openai:
            mock_call_openai.return_value = None  # OpenAI fails
            
            # Call with unknown intent (no template)
            response_text, source_label = generate_response(
                intent="unknown_intent",
                original_message="Random message",
                similar_solution=None,
                sub_intent=None,
                similar_quality_score=None
            )
            
            # Should fall back to template (unknown intents get template response)
            assert source_label == "template"
            assert response_text == "I've received your message and will do my best to assist you."
