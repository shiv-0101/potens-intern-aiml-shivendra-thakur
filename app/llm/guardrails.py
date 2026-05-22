from app.core.constants import FALLBACK_MESSAGE

def is_fallback_response(answer: str) -> bool:
    fallback_indicators = [
        "do not contain enough information",
        "cannot answer",
        "not found in the context",
        FALLBACK_MESSAGE.lower()
    ]
    return any(indicator in answer.lower() for indicator in fallback_indicators)

def validate_response(answer: str, context_chunks: list) -> dict:
    is_fallback = is_fallback_response(answer)
    return {
        "is_fallback": is_fallback,
        "answer_length": len(answer),
        "context_chunks_used": len(context_chunks),
        "has_answer": not is_fallback and len(answer) > 20
    }