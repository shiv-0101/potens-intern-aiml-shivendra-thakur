from app.ingestion.loader import load_directory, load_multiple_pdfs
from app.ingestion.chunker import chunk_documents
from app.vectorstore.chroma_db import add_chunks_to_db, get_collection_stats
import logging

logger = logging.getLogger(__name__)

def run_ingestion_pipeline(file_paths: list = None, directory: str = None) -> dict:
    # Step 1: Load
    if file_paths:
        documents = load_multiple_pdfs(file_paths)
    elif directory:
        from app.ingestion.loader import load_directory as ld
        documents = ld(directory)
    else:
        documents = load_directory("./data/raw")

    if not documents:
        return {"status": "error", "message": "No documents loaded"}

    logger.info(f"Loaded {len(documents)} pages")

    # Step 2: Chunk
    chunks = chunk_documents(documents)
    logger.info(f"Created {len(chunks)} chunks")

    # Step 3: Embed + Store
    count = add_chunks_to_db(chunks)

    # Step 4: Report
    stats = get_collection_stats()

    return {
        "status": "success",
        "chunks_created": count,
        "documents_processed": len(set(c.metadata.get("source") for c in chunks)),
        "total_in_db": stats["total_chunks"],
        "documents_in_db": stats["documents"]
    }