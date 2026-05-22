from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import json
import re

from app.retrieval.retriever import retrieve_for_contradiction
from app.llm.gemini_client import generate
from app.core.prompts import CONTRADICTION_PROMPT_TEMPLATE
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

class ContradictRequest(BaseModel):
    doc1: str
    doc2: str
    topic: str

class ContradictResponse(BaseModel):
    conflict: bool
    reasoning: str
    evidence: list

@router.post("/contradict", response_model=ContradictResponse)
async def contradict(request: ContradictRequest):
    try:
        chunks_doc1, chunks_doc2 = retrieve_for_contradiction(
            request.topic, request.doc1, request.doc2, top_k=3
        )

        if not chunks_doc1 and not chunks_doc2:
            raise HTTPException(
                status_code=404,
                detail=f"No content found for: {request.doc1}, {request.doc2}"
            )

        context1 = "\n\n".join([c["content"] for c in chunks_doc1]) or "No relevant content found."
        context2 = "\n\n".join([c["content"] for c in chunks_doc2]) or "No relevant content found."

        prompt = CONTRADICTION_PROMPT_TEMPLATE.format(
            topic=request.topic,
            doc1=request.doc1,
            doc2=request.doc2,
            context1=context1,
            context2=context2
        )

        response_text = generate(prompt)

        try:
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
            else:
                raise ValueError("No JSON found")
        except (json.JSONDecodeError, ValueError):
            result = {
                "conflict": "conflict" in response_text.lower(),
                "reasoning": response_text,
                "evidence": [
                    {"source": request.doc1, "claim": chunks_doc1[0]["snippet"] if chunks_doc1 else ""},
                    {"source": request.doc2, "claim": chunks_doc2[0]["snippet"] if chunks_doc2 else ""}
                ]
            }

        return ContradictResponse(
            conflict=bool(result.get("conflict", False)),
            reasoning=result.get("reasoning", ""),
            evidence=result.get("evidence", [])
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in /contradict: {e}")
        raise HTTPException(status_code=500, detail=str(e))