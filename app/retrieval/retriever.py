from app.vectorstore.chroma_db import similarity_search
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

def retrieve_chunks(query: str, top_k: int = None, filter_source: str = None) -> list:
    k = top_k or settings.top_k
    results = similarity_search(query, top_k=k, filter_source=filter_source)
    logger.info(f"Retrieved {len(results)} chunks")
    return results

def retrieve_for_contradiction(query: str, doc1: str, doc2: str, top_k: int = 3) -> tuple:
    chunks_doc1 = similarity_search(query, top_k=top_k, filter_source=doc1)
    chunks_doc2 = similarity_search(query, top_k=top_k, filter_source=doc2)
    return chunks_doc1, chunks_doc2