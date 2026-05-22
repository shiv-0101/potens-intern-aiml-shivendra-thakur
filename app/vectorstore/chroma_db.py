import chromadb
from app.core.config import settings
from app.ingestion.embedder import embed_texts, embed_query
import logging

logger = logging.getLogger(__name__)

_client = None
_collection = None

def get_chroma_client():
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(path=settings.chroma_persist_dir)
    return _client

def get_collection():
    global _collection
    if _collection is None:
        client = get_chroma_client()
        _collection = client.get_or_create_collection(
            name=settings.collection_name,
            metadata={"hnsw:space": "cosine"}
        )
    return _collection

def add_chunks_to_db(chunks: list) -> int:
    collection = get_collection()
    if not chunks:
        return 0

    texts = [chunk.page_content for chunk in chunks]
    metadatas = []
    ids = []

    for chunk in chunks:
        meta = {
            "source": chunk.metadata.get("source", "unknown"),
            "page": int(chunk.metadata.get("page", 0)),
            "chunk_id": int(chunk.metadata.get("chunk_id", 0)),
        }
        metadatas.append(meta)
        ids.append(f"{meta['source']}_chunk_{meta['chunk_id']}")

    embeddings = embed_texts(texts)

    batch_size = 100
    for i in range(0, len(texts), batch_size):
        collection.add(
            documents=texts[i:i+batch_size],
            embeddings=embeddings[i:i+batch_size],
            metadatas=metadatas[i:i+batch_size],
            ids=ids[i:i+batch_size]
        )

    logger.info(f"Added {len(chunks)} chunks to ChromaDB")
    return len(chunks)

def similarity_search(query: str, top_k: int = 5, filter_source: str = None) -> list:
    collection = get_collection()
    query_embedding = embed_query(query)

    where_filter = {"source": {"$eq": filter_source}} if filter_source else None

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        where=where_filter,
        include=["documents", "metadatas", "distances"]
    )

    search_results = []
    if results["documents"] and results["documents"][0]:
        for doc, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0]
        ):
            similarity = 1 - dist
            search_results.append({
                "content": doc,
                "metadata": meta,
                "similarity_score": round(similarity, 4),
                "snippet": doc[:200]
            })

    return search_results

def get_collection_stats() -> dict:
    try:
        collection = get_collection()
        count = collection.count()
        if count > 0:
            all_meta = collection.get(include=["metadatas"])
            sources = list(set(m["source"] for m in all_meta["metadatas"]))
        else:
            sources = []
        return {
            "total_chunks": count,
            "documents": sources,
            "document_count": len(sources)
        }
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return {"total_chunks": 0, "documents": [], "document_count": 0}

def reset_collection():
    global _collection
    client = get_chroma_client()
    try:
        client.delete_collection(settings.collection_name)
    except Exception:
        pass
    _collection = None
    return get_collection()