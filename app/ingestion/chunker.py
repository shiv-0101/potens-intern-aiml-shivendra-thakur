from langchain.text_splitter import RecursiveCharacterTextSplitter
from app.core.config import settings
import logging
import re

logger = logging.getLogger(__name__)

def clean_text(text: str) -> str:
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    return text

def chunk_documents(documents: list) -> list:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    chunks = splitter.split_documents(documents)
    for i, chunk in enumerate(chunks):
        chunk.metadata["chunk_id"] = i
        chunk.page_content = clean_text(chunk.page_content)
    chunks = [c for c in chunks if len(c.page_content.strip()) > 50]
    logger.info(f"Created {len(chunks)} chunks from {len(documents)} pages")
    return chunks