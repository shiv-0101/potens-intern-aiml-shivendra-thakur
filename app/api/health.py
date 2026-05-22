from fastapi import APIRouter
from app.vectorstore.chroma_db import get_collection_stats

router = APIRouter()

@router.get("/health")
async def health():
    stats = get_collection_stats()
    return {
        "status": "ok",
        "documents_loaded": stats["document_count"],
        "total_chunks": stats["total_chunks"],
        "documents": stats["documents"],
        "vector_store": "connected"
    }