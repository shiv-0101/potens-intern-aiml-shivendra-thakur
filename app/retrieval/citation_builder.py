from app.core.constants import SNIPPET_LENGTH

def build_citations(chunks: list) -> list:
    citations = []
    seen_ids = set()
    for chunk in chunks:
        meta = chunk.get("metadata", {})
        chunk_id = meta.get("chunk_id", 0)
        source = meta.get("source", "unknown")
        dedup_key = f"{source}_{chunk_id}"
        if dedup_key in seen_ids:
            continue
        seen_ids.add(dedup_key)
        citations.append({
            "source_file": source,
            "page": meta.get("page", 0),
            "chunk_id": chunk_id,
            "snippet": chunk.get("content", "")[:SNIPPET_LENGTH],
            "similarity_score": chunk.get("similarity_score", 0.0)
        })
    return citations

def build_context_string(chunks: list) -> str:
    parts = []
    for chunk in chunks:
        meta = chunk.get("metadata", {})
        source = meta.get("source", "unknown")
        page = meta.get("page", 0)
        content = chunk.get("content", "")
        parts.append(f"[Source: {source}, Page: {page}]\n{content}")
    return "\n\n---\n\n".join(parts)

def compute_confidence(chunks: list) -> float:
    if not chunks:
        return 0.0
    scores = [c.get("similarity_score", 0.0) for c in chunks]
    return round(sum(scores) / len(scores), 4)