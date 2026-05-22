from sentence_transformers import CrossEncoder
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

_reranker = None

def get_reranker():
    global _reranker
    if _reranker is None:
        logger.info(f"Loading reranker: {settings.reranker_model}")
        _reranker = CrossEncoder(settings.reranker_model)
    return _reranker

def rerank_chunks(query: str, chunks: list, top_k: int = 5) -> list:
    if not chunks:
        return chunks
    try:
        reranker = get_reranker()
        pairs = [(query, chunk["content"]) for chunk in chunks]
        scores = reranker.predict(pairs)
        for chunk, score in zip(chunks, scores):
            chunk["reranker_score"] = float(score)
        reranked = sorted(chunks, key=lambda x: x["reranker_score"], reverse=True)
        return reranked[:top_k]
    except Exception as e:
        logger.warning(f"Reranking failed, using original order: {e}")
        return chunks[:top_k]