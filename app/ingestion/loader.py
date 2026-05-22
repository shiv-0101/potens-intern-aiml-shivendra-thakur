from langchain_community.document_loaders import PyPDFLoader
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

def load_pdf(file_path: str) -> list:
    try:
        loader = PyPDFLoader(file_path)
        documents = loader.load()
        filename = Path(file_path).name
        for doc in documents:
            doc.metadata["source"] = filename
            doc.metadata["file_path"] = file_path
        logger.info(f"Loaded {len(documents)} pages from {filename}")
        return documents
    except Exception as e:
        logger.error(f"Failed to load {file_path}: {e}")
        return []

def load_multiple_pdfs(file_paths: list) -> list:
    all_documents = []
    for path in file_paths:
        docs = load_pdf(path)
        all_documents.extend(docs)
    logger.info(f"Total pages loaded: {len(all_documents)}")
    return all_documents

def load_directory(directory_path: str) -> list:
    dir_path = Path(directory_path)
    pdf_files = list(dir_path.glob("*.pdf"))
    if not pdf_files:
        logger.warning(f"No PDF files found in {directory_path}")
        return []
    return load_multiple_pdfs([str(f) for f in pdf_files])