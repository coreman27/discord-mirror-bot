# INTERVIEW TOPIC: Third-Party API Integration
# Importing Google's Generative AI SDK for accessing AI models
import google.generativeai as genai
from google.api_core import exceptions  # Google API exception types
import config

# INTERVIEW TOPIC: Fallback Strategy and Resilience Patterns
# List of models to try in order of preference
# This implements a fallback chain - if one fails, try the next
# Common pattern in microservices and distributed systems
MODELS = [
    'gemini-2.5-flash',      # Newest, fastest (try first)
    'gemini-2.5-flash-lite', # Lighter version
    'gemini-flash-latest',   # Latest stable release
    'gemini-1.5-flash',      # Previous version
    'gemini-pro'             # Fallback to older model
]

# INTERVIEW TOPIC: Configuration and Initialization
def configure_genai():
    """Initialize the Gemini API client with API key.
    
    INTERVIEW TOPIC: Early Validation Pattern
    Check if required configuration exists before proceeding.
    Returns boolean to indicate success/failure.
    """
    if config.GEMINI_API_KEY:
        genai.configure(api_key=config.GEMINI_API_KEY)
        return True
    return False  # Missing API key

# INTERVIEW TOPIC: Async Programming and API Calls
async def generate_response(prompt):
    """Generate AI response with automatic model fallback.
    
    INTERVIEW TOPIC: Retry Logic and Error Handling
    This function implements a robust retry mechanism:
    1. Try each model in sequence
    2. Handle specific errors (quota, not found)
    3. Fallback to next model on failure
    4. Return None if all models fail
    
    Common in production systems dealing with unreliable external APIs.
    
    Args:
        prompt (str): The input text for the AI model
        
    Returns:
        str: Generated response text, or None if all models failed
    """
    # INTERVIEW TOPIC: Guard Clauses
    # Validate configuration before attempting API calls
    if not configure_genai():
        return None

    last_error = None  # Track the last error for logging

    # INTERVIEW TOPIC: Iteration and Fallback Logic
    # Loop through models, trying each until one succeeds
    for model_name in MODELS:
        try:
            # INTERVIEW TOPIC: API Interaction Pattern
            # 1. Initialize model instance
            # 2. Make async API call with await
            # 3. Extract text from response
            model = genai.GenerativeModel(model_name)
            response = await model.generate_content_async(prompt)
            return response.text  # Success - return immediately
            
        # INTERVIEW TOPIC: Exception Handling - Specific Error Types
        # Handle specific exceptions before generic ones (most specific first)
        except exceptions.ResourceExhausted:
            # HTTP 429: Rate limit/quota exceeded
            print(f"⚠️ Quota exceeded for {model_name}, switching to next model...")
            continue  # Try next model in list
            
        except exceptions.NotFound:
            # HTTP 404: Model doesn't exist (maybe deprecated)
            print(f"⚠️ Model {model_name} not found, switching to next model...")
            continue  # Try next model in list
            
        except Exception as e:
            # INTERVIEW TOPIC: Catch-All Error Handler
            # Catch any other unexpected errors (500s, network issues, etc.)
            # Store error but continue trying other models
            print(f"⚠️ Error with {model_name}: {e}, switching to next model...")
            last_error = e
            continue
    
    # INTERVIEW TOPIC: Error Propagation
    # If all models failed and we have an error, re-raise it for caller to handle
    if last_error:
        raise last_error
    
    # INTERVIEW TOPIC: Null Return Pattern
    # Return None to indicate failure without an exception
    # Caller must check for None before using result
    return None
