from langdetect import detect
from app.llm.gemini_client import generate
from app.core.prompts import TRANSLATION_PROMPT
import logging

logger = logging.getLogger(__name__)

LANGUAGE_NAMES = {
    "en": "English",
    "hi": "Hindi",
    "fr": "French",
    "de": "German",
    "es": "Spanish",
}

def detect_language(text: str) -> str:
    try:
        return detect(text)
    except Exception:
        return "en"

def translate_text(text: str, target_language: str) -> str:
    if target_language == "en":
        return text
    target_name = LANGUAGE_NAMES.get(target_language, target_language)
    prompt = TRANSLATION_PROMPT.format(target_language=target_name, text=text)
    try:
        return generate(prompt).strip()
    except Exception as e:
        logger.error(f"Translation failed: {e}")
        return text

def prepare_query(query: str, declared_language: str = None) -> tuple:
    detected_lang = detect_language(query)
    original_lang = declared_language or detected_lang
    if original_lang == "en" or detected_lang == "en":
        return query, "en"
    english_query = translate_text(query, "en")
    logger.info(f"Translated query from {original_lang} to English")
    return english_query, original_lang