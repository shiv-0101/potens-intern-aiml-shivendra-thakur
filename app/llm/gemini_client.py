from groq import Groq
from app.core.config import settings
import logging
import time

logger = logging.getLogger(__name__)

_client = None

def get_client():
    global _client
    if _client is None:
        _client = Groq(api_key=settings.groq_api_key)
    return _client

def generate(prompt: str, max_retries: int = 3) -> str:
    """Generate response from Groq with retry logic."""
    client = get_client()
    
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1024,
                temperature=0.1
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.warning(f"Groq attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
            else:
                raise
    
    raise RuntimeError("Groq API failed after all retries")