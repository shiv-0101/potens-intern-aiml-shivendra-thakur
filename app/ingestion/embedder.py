from sentence_transformers import SentenceTransformer
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

_model = None

def get_embedding_model() -> SentenceTransformer:
    global _model
    if _model is None:
        logger.info(f"Loading embedding model: {settings.embedding_model}")
        _model = SentenceTransformer(settings.embedding_model)
    return _model

def embed_texts(texts: list) -> list:
    model = get_embedding_model()
    embeddings = model.encode(texts, show_progress_bar=True, batch_size=32)
    return embeddings.tolist()

def embed_query(query: str) -> list:
    model = get_embedding_model()
    embedding = model.encode([query])
    return embedding[0].tolist()