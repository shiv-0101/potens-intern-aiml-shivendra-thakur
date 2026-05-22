from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from app.retrieval.retriever import retrieve_chunks
from app.retrieval.reranker import rerank_chunks
from app.retrieval.citation_builder import build_citations, build_context_string, compute_confidence
from app.llm.gemini_client import generate
from app.llm.translator import prepare_query, translate_text
from app.llm.guardrails import validate_response
from app.core.prompts import QA_PROMPT_TEMPLATE
from app.core.constants import FALLBACK_MESSAGE
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

class AskRequest(BaseModel):
    query: str
    language: Optional[str] = "en"
    top_k: Optional[int] = 5
    use_reranker: Optional[bool] = True

class AskResponse(BaseModel):
    answer: str
    citations: list
    confidence: float
    language: str
    is_fallback: bool

@router.post("/ask", response_model=AskResponse)
async def ask(request: AskRequest):
    try:
        # 1. Translate query to English if needed
        english_query, original_language = prepare_query(
            request.query, request.language
        )

        # 2. Retrieve chunks (fetch extra for reranking)
        chunks = retrieve_chunks(english_query, top_k=request.top_k * 2)

        if not chunks:
            return AskResponse(
                answer=FALLBACK_MESSAGE,
                citations=[],
                confidence=0.0,
                language=original_language,
                is_fallback=True
            )

        # 3. Rerank
        if request.use_reranker:
            chunks = rerank_chunks(english_query, chunks, top_k=request.top_k)
        else:
            chunks = chunks[:request.top_k]

        # 4. Build context
        context = build_context_string(chunks)

        # 5. Generate answer
        prompt = QA_PROMPT_TEMPLATE.format(context=context, question=english_query)
        answer = generate(prompt)

        # 6. Translate back if needed
        if original_language != "en":
            answer = translate_text(answer, original_language)

        # 7. Build response
        citations = build_citations(chunks)
        confidence = compute_confidence(chunks)
        validation = validate_response(answer, chunks)

        return AskResponse(
            answer=answer,
            citations=citations,
            confidence=confidence,
            language=original_language,
            is_fallback=validation["is_fallback"]
        )

    except Exception as e:
        logger.error(f"Error in /ask: {e}")
        raise HTTPException(status_code=500, detail=str(e))