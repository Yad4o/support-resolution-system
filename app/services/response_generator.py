from typing import Optional
import logging


def generate_response(intent: str, original_message: str, similar_solution: Optional[str] = None) -> str:
    """
    Generate a human-readable response based on intent, original message, and similar solution.
    
    This component only returns text; it does not update database or make decisions.
    Reference: Technical Spec § 9.3 (Response Generation)
    
    Args:
        intent: The classified intent (e.g., 'login_issue', 'payment_issue')
        original_message: The original user message for context
        similar_solution: Optional solution from a similar resolved ticket to reuse.
                          NOTE: This parameter is trusted/raw user-provided content.
                          Callers are responsible for sanitization/validation before
                          calling this function. The function will pass through the
                          similar_solution verbatim without sanitization.
        
    Returns:
        str: Generated response text
    """
    
    # Priority 1: Reuse similar solution if provided
    # NOTE: similar_solution is passed through verbatim - callers must sanitize
    if similar_solution and similar_solution.strip():
        stripped_solution = similar_solution.strip()
        
        if len(stripped_solution) > 500:
            # Attempt to truncate at the last sentence boundary within the first 500 chars
            truncated_text = stripped_solution[:500]
            last_sentence_end = max(
                truncated_text.rfind('.'),
                truncated_text.rfind('!'),
                truncated_text.rfind('?')
            )
            
            if last_sentence_end != -1:
                clean_solution = truncated_text[:last_sentence_end + 1]
            else:
                clean_solution = truncated_text + "... (solution abbreviated)"
            
            # Emit warning via module logger
            logging.getLogger(__name__).warning(
                f"Solution truncated from {len(stripped_solution)} to {len(clean_solution)} characters"
            )
        else:
            clean_solution = stripped_solution
        
        return f"I understand you're experiencing an issue. Based on a similar case, here's what helped: {clean_solution}"

    # Priority 2: Intent-based static templates
    response_templates = {
        "login_issue": [
            "I understand you're having trouble logging in. Please try resetting your password or check your credentials.",
            "Login issues can often be resolved by clearing your browser cache or trying a different browser.",
            "For login problems, please verify your username and password, or use the 'forgot password' option if needed."
        ],
        "payment_issue": [
            "I understand you're experiencing a payment-related issue. Please check your billing statement or contact our payment support team.",
            "Payment issues can be resolved by reviewing your recent transactions or updating your payment method.",
            "For payment problems, please verify your card details are current and contact your bank if necessary."
        ],
        "account_issue": [
            "I understand you need help with your account. Please visit your account settings to make the necessary changes.",
            "Account issues can often be resolved by updating your profile information or verifying your email address.",
            "For account-related problems, please ensure your contact information is up to date and security settings are correct."
        ],
        "technical_issue": [
            "I understand you're experiencing a technical problem. Please try refreshing the page or clearing your browser cache.",
            "Technical issues can often be resolved by restarting your device or checking for system updates.",
            "For technical problems, please try accessing our service from a different browser or device."
        ],
        "feature_request": [
            "Thank you for your suggestion! We appreciate your feedback and will consider it for future improvements.",
            "Feature requests help us improve our service. Your suggestion has been forwarded to our development team.",
            "We value your input! Your feature request has been logged and will be reviewed by our product team."
        ],
        "general_query": [
            "I understand you have a question. Please check our help center or FAQ section for more information.",
            "For general questions, you can find answers in our knowledge base or contact our support team.",
            "I'm here to help! Please provide more details about your question so I can assist you better."
        ]
    }
    
    # Get appropriate template based on intent
    templates = response_templates.get(intent, [])
    
    if templates:
        # Select template based on original message characteristics
        if "?" in original_message or "how" in original_message.lower():
            # Use more helpful template for questions
            return templates[0]
        elif "urgent" in original_message.lower() or "emergency" in original_message.lower():
            # Use more urgent template
            return templates[1]
        else:
            # Use default template (third template)
            return templates[2]
    
    # Priority 3: Fallback response
    fallback_responses = [
        "I understand your request and will do my best to assist you.",
        "Thank you for contacting us. I'm here to help resolve your issue.",
        "I've received your message and will provide appropriate assistance."
    ]
    
    # Select fallback based on original message length (simple heuristic)
    fallback_index = len(original_message) % len(fallback_responses)
    return fallback_responses[fallback_index]
