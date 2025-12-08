import google.generativeai as genai
from google.api_core import exceptions
import config

# List of models to try in order of preference
# We start with the newest/best, and fall back to others if quotas are hit
MODELS = [
    'gemini-2.5-flash',
    'gemini-2.5-flash-lite',
    'gemini-flash-latest',
    'gemini-1.5-flash',
    'gemini-pro'
]

def configure_genai():
    if config.GEMINI_API_KEY:
        genai.configure(api_key=config.GEMINI_API_KEY)
        return True
    return False

async def generate_response(prompt):
    """
    Attempts to generate content using a list of models.
    If one fails due to quota (429) or not found (404), it tries the next.
    """
    if not configure_genai():
        return None

    last_error = None

    for model_name in MODELS:
        try:
            # print(f"Trying model: {model_name}")
            model = genai.GenerativeModel(model_name)
            response = await model.generate_content_async(prompt)
            return response.text
        except exceptions.ResourceExhausted:
            print(f"⚠️ Quota exceeded for {model_name}, switching to next model...")
            continue
        except exceptions.NotFound:
            print(f"⚠️ Model {model_name} not found, switching to next model...")
            continue
        except Exception as e:
            # Catch-all for other API errors (like 500s or 400s)
            # We try the next model just in case it's a model-specific issue
            print(f"⚠️ Error with {model_name}: {e}, switching to next model...")
            last_error = e
            continue
    
    # If we ran out of models
    if last_error:
        raise last_error
    return None
