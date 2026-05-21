# Research Paper RAG Assistant — PRD & PLAN.md

---

# PRD.md — Product Requirements Document

---

## 1. Product Overview

**Product Name:** Research Paper RAG Assistant
**Type:** Production-ready AI system (Internship Assignment)
**Timeline:** 10 hours
**Domain:** AI/ML Research Papers

### 1.1 Problem Statement

Researchers and students struggle to extract precise, cited information from multiple dense academic papers. They need a system that can answer natural language questions, show exactly where the answer came from, detect contradictions between papers, and work across languages.

### 1.2 Product Vision

A clean, modular, production-grade Retrieval-Augmented Generation (RAG) system that ingests research PDFs, answers questions with source citations, prevents hallucinations, detects cross-document contradictions, and supports multilingual queries — all exposed through a FastAPI backend and Streamlit frontend.

### 1.3 Success Criteria

| Criterion | Target |
|---|---|
| Accurate cited answers | Citations included in every response |
| Hallucination prevention | Explicit fallback when context is insufficient |
| Contradiction detection | Working `/contradict` endpoint |
| Multilingual support | At least Hindi ↔ English |
| API health | All endpoints return structured JSON |
| UI functional | Upload, query, citations, contradiction pages work |
| Reproducible setup | Single command to run everything |

---

## 2. Target Users

| User | Need |
|---|---|
| Internship Evaluator | See clean architecture, modular code, working demo |
| Researcher | Ask questions across multiple papers |
| Student | Understand paper contents without reading fully |
| Non-English Speaker | Query in native language |

---

## 3. Functional Requirements

### 3.1 Document Ingestion Module

**FR-01:** System shall accept PDF files (5–10 papers)
**FR-02:** System shall extract raw text with metadata (filename, page number)
**FR-03:** System shall clean extracted text (remove excessive whitespace, artifacts)
**FR-04:** System shall split documents using `RecursiveCharacterTextSplitter` with:
- `chunk_size = 700`
- `chunk_overlap = 120`

**FR-05:** Each chunk shall carry metadata:
```json
{
  "source": "attention_is_all_you_need.pdf",
  "page": 4,
  "chunk_id": 14
}
```

**FR-06:** System shall generate embeddings using `sentence-transformers/all-MiniLM-L6-v2`
**FR-07:** System shall store embeddings in persistent ChromaDB collection

---

### 3.2 Query & Retrieval Module

**FR-08:** System shall accept a natural language query
**FR-09:** System shall optionally detect and translate non-English queries to English before retrieval
**FR-10:** System shall embed the query using the same embedding model
**FR-11:** System shall perform similarity search returning top-K chunks (K=5 default)
**FR-12:** System shall optionally rerank results using `cross-encoder/ms-marco-MiniLM-L-6-v2`
**FR-13:** System shall compute a confidence score based on average retrieval similarity

---

### 3.3 LLM Generation Module

**FR-14:** System shall use Gemini 1.5 Flash as the LLM
**FR-15:** System shall construct a grounded prompt:

```
You are a research assistant. Answer ONLY from the provided context below.
If the answer is not found in the context, respond exactly with:
"The provided documents do not contain enough information to answer this question."

Context:
{context}

Question:
{question}

Answer:
```

**FR-16:** System shall never generate answers outside provided context
**FR-17:** System shall return answer in the query language (translate back if needed)

---

### 3.4 Citation System

**FR-18:** Every answer response shall include citations:
```json
{
  "answer": "Transformers use self-attention...",
  "citations": [
    {
      "source_file": "attention_is_all_you_need.pdf",
      "page": 4,
      "chunk_id": 14,
      "snippet": "Transformers outperform RNNs in..."
    }
  ],
  "confidence": 0.87
}
```

**FR-19:** Snippets shall be the first 200 characters of the retrieved chunk
**FR-20:** Citations shall be deduplicated by chunk_id

---

### 3.5 Contradiction Detection Module

**FR-21:** System shall accept two document names and a topic
**FR-22:** System shall retrieve top-3 chunks from each document filtered by topic
**FR-23:** System shall send both chunk sets to Gemini with a contradiction analysis prompt
**FR-24:** System shall return structured contradiction result:
```json
{
  "conflict": true,
  "reasoning": "Paper A claims 85% accuracy while Paper B reports 92%...",
  "evidence": [
    {"source": "paperA.pdf", "snippet": "..."},
    {"source": "paperB.pdf", "snippet": "..."}
  ]
}
```

---

### 3.6 Multilingual Support

**FR-25:** System shall detect input language
**FR-26:** System shall translate non-English queries to English using Gemini
**FR-27:** System shall translate the final answer back to the original language
**FR-28:** Minimum supported languages: English, Hindi

---

### 3.7 API Endpoints

**FR-29:** `GET /health` — returns system status
**FR-30:** `POST /ask` — main Q&A endpoint
**FR-31:** `POST /contradict` — contradiction detection endpoint
**FR-32:** `POST /ingest` — trigger document ingestion pipeline

---

### 3.8 Streamlit UI

**FR-33:** Page 1: Document uploader — upload PDFs and trigger ingestion
**FR-34:** Page 2: Q&A interface — text input, language selector, answer display with citations
**FR-35:** Page 3: Contradiction checker — select two docs, enter topic, view result
**FR-36:** Page 4: System health / loaded documents display

---

## 4. Non-Functional Requirements

| ID | Requirement |
|---|---|
| NFR-01 | API response time < 10 seconds for /ask |
| NFR-02 | System runs locally with Python venv |
| NFR-03 | All secrets in `.env` file, never hardcoded |
| NFR-04 | ChromaDB data persisted to disk |
| NFR-05 | Code modular — each file has single responsibility |
| NFR-06 | All endpoints return structured JSON |
| NFR-07 | Graceful error handling with meaningful messages |
| NFR-08 | README must explain chunking strategy, architecture, setup |

---

## 5. Out of Scope

- User authentication / multi-user sessions
- Real-time streaming responses
- Cloud deployment (focus on local)
- Complex agent loops
- Non-PDF document formats (Phase 1)

---

## 6. API Contract

### `GET /health`
```json
{
  "status": "ok",
  "documents_loaded": 7,
  "vector_store": "connected"
}
```

### `POST /ask`

**Request:**
```json
{
  "query": "What is the transformer architecture?",
  "language": "en",
  "top_k": 5
}
```

**Response:**
```json
{
  "answer": "The Transformer is a model architecture...",
  "citations": [
    {
      "source_file": "attention_is_all_you_need.pdf",
      "page": 4,
      "chunk_id": 14,
      "snippet": "The Transformer follows an encoder-decoder structure..."
    }
  ],
  "confidence": 0.87,
  "language": "en"
}
```

### `POST /contradict`

**Request:**
```json
{
  "doc1": "paper_a.pdf",
  "doc2": "paper_b.pdf",
  "topic": "training efficiency"
}
```

**Response:**
```json
{
  "conflict": true,
  "reasoning": "Paper A claims training takes 12 hours while Paper B reports 3 hours on similar hardware.",
  "evidence": [
    {
      "source": "paper_a.pdf",
      "page": 6,
      "snippet": "Training required approximately 12 hours on 8 GPUs..."
    },
    {
      "source": "paper_b.pdf",
      "page": 3,
      "snippet": "Our model trains in under 3 hours on equivalent hardware..."
    }
  ]
}
```

### `POST /ingest`

**Request:**
```json
{
  "file_paths": ["data/raw/paper1.pdf", "data/raw/paper2.pdf"]
}
```

**Response:**
```json
{
  "status": "success",
  "chunks_created": 342,
  "documents_processed": 2
}
```

---

## 7. Data Requirements

### Sample Papers to Use (Download from arXiv)

| Paper | arXiv ID | Why |
|---|---|---|
| Attention Is All You Need | 1706.03762 | Foundational, well-known |
| BERT | 1810.04805 | Good for contradiction with GPT |
| GPT-3 | 2005.14165 | Contradicts BERT on some claims |
| RAG (Lewis et al.) | 2005.11401 | Meta — about RAG itself |
| LoRA | 2106.09685 | Fine-tuning efficiency |

Minimum 3 papers required for demo. 5+ preferred.

---

## 8. Risk Assessment

| Risk | Mitigation |
|---|---|
| Gemini API rate limits | Implement retry with backoff, cache responses |
| PDF parsing failures | Try/except with skip + log |
| ChromaDB corruption | Delete and re-ingest option |
| Translation errors | Fallback to English-only mode |
| Time overrun | Phases clearly defined; Phase 4 is optional |

---

---

# PLAN.md — Execution Plan

---

## Total Budget: 10 Hours

```
Hour 0-1   → Phase 0: Project Setup & Foundation
Hour 1-3   → Phase 1: Ingestion Pipeline
Hour 3-5   → Phase 2: Core RAG + /ask Endpoint
Hour 5-6.5 → Phase 3: Contradiction + Multilingual + Streamlit UI
Hour 6.5-8 → Phase 4: Stretch Features + Polish
Hour 8-9   → Phase 5: Testing + README
Hour 9-10  → Phase 6: Final Review + Submission Prep
```

---

## PHASE 0 — Project Setup & Foundation (Hour 0–1)

**Goal:** Runnable skeleton. Nothing broken.

### Tasks

#### 0.1 Create Project Structure
```bash
mkdir rag-document-qa && cd rag-document-qa

mkdir -p app/api app/core app/ingestion app/retrieval \
          app/llm app/vectorstore app/ui \
          data/raw data/processed data/embeddings \
          docs/sample_papers docs/screenshots \
          tests examples
```

#### 0.2 Create All Empty Files
```bash
touch app/__init__.py
touch app/api/__init__.py app/api/ask.py app/api/contradict.py app/api/health.py
touch app/core/__init__.py app/core/config.py app/core/prompts.py app/core/constants.py
touch app/ingestion/__init__.py app/ingestion/loader.py app/ingestion/chunker.py \
      app/ingestion/embedder.py app/ingestion/pipeline.py
touch app/retrieval/__init__.py app/retrieval/retriever.py app/retrieval/reranker.py \
      app/retrieval/citation_builder.py
touch app/llm/__init__.py app/llm/gemini_client.py app/llm/translator.py app/llm/guardrails.py
touch app/vectorstore/__init__.py app/vectorstore/chroma_db.py app/vectorstore/schema.py
touch app/ui/streamlit_app.py
touch app/main.py
touch run.py
touch requirements.txt .env .gitignore README.md
touch tests/test_ask.py tests/test_contradict.py tests/eval_dataset.json
touch examples/sample_queries.json examples/sample_outputs.json
```

#### 0.3 Create `.env`
```bash
GEMINI_API_KEY=your_key_here
CHROMA_PERSIST_DIR=./data/embeddings
COLLECTION_NAME=research_papers
TOP_K=5
CHUNK_SIZE=700
CHUNK_OVERLAP=120
```

#### 0.4 Create `requirements.txt`
```
fastapi==0.111.0
uvicorn==0.30.0
streamlit==1.35.0
langchain==0.2.0
langchain-community==0.2.0
langchain-google-genai==1.0.6
chromadb==0.5.0
sentence-transformers==3.0.0
pypdf==4.2.0
python-dotenv==1.0.1
pydantic==2.7.1
google-generativeai==0.7.0
deep-translator==1.11.4
langdetect==1.0.9
httpx==0.27.0
pytest==8.2.0
```

#### 0.5 Setup Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

#### 0.6 Create `.gitignore`
```
venv/
.env
__pycache__/
*.pyc
data/embeddings/
*.db
.DS_Store
```

#### 0.7 Download Sample Papers

Download these 5 PDFs into `data/raw/`:
1. `attention_is_all_you_need.pdf` — arXiv 1706.03762
2. `bert.pdf` — arXiv 1810.04805
3. `gpt3.pdf` — arXiv 2005.14165
4. `rag_lewis.pdf` — arXiv 2005.11401
5. `lora.pdf` — arXiv 2106.09685

**Checkpoint:** Project structure exists, venv active, packages install without errors.

---

## PHASE 1 — Ingestion Pipeline (Hour 1–3)

**Goal:** PDFs → ChromaDB. Text stored with metadata and embeddings.

### Task 1.1 — `app/core/config.py`

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    gemini_api_key: str
    chroma_persist_dir: str = "./data/embeddings"
    collection_name: str = "research_papers"
    top_k: int = 5
    chunk_size: int = 700
    chunk_overlap: int = 120
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    reranker_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"

    class Config:
        env_file = ".env"

settings = Settings()
```

---

### Task 1.2 — `app/core/constants.py`

```python
SUPPORTED_LANGUAGES = ["en", "hi", "fr", "de", "es"]
DEFAULT_LANGUAGE = "en"
MAX_CHUNK_SIZE = 700
FALLBACK_MESSAGE = "The provided documents do not contain enough information to answer this question."
TOP_K_DEFAULT = 5
SNIPPET_LENGTH = 200
```

---

### Task 1.3 — `app/core/prompts.py`

```python
QA_PROMPT_TEMPLATE = """
You are a precise research assistant. Answer ONLY using the context below.
If the answer is not found in the context, respond exactly with:
"The provided documents do not contain enough information to answer this question."

Do not make up information. Do not use prior knowledge.

Context:
{context}

Question:
{question}

Answer:
"""

CONTRADICTION_PROMPT_TEMPLATE = """
You are an expert at analyzing research papers for contradictions.

Below are excerpts from two research papers on the topic: "{topic}"

Paper 1 ({doc1}):
{context1}

Paper 2 ({doc2}):
{context2}

Analyze these excerpts carefully. Determine if they contain contradictory claims.

Respond in this exact JSON format:
{{
  "conflict": true or false,
  "reasoning": "Detailed explanation of the contradiction or agreement",
  "evidence": [
    {{"source": "{doc1}", "claim": "specific claim from paper 1"}},
    {{"source": "{doc2}", "claim": "specific claim from paper 2"}}
  ]
}}
"""

TRANSLATION_PROMPT = """
Translate the following text to {target_language}.
Return ONLY the translated text, nothing else.

Text: {text}
"""
```

---

### Task 1.4 — `app/ingestion/loader.py`

```python
from langchain_community.document_loaders import PyPDFLoader
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

def load_pdf(file_path: str) -> list:
    """Load a single PDF and return list of Document objects with metadata."""
    try:
        loader = PyPDFLoader(file_path)
        documents = loader.load()
        
        # Attach source filename to metadata
        filename = Path(file_path).name
        for doc in documents:
            doc.metadata["source"] = filename
            doc.metadata["file_path"] = file_path
        
        logger.info(f"Loaded {len(documents)} pages from {filename}")
        return documents
    except Exception as e:
        logger.error(f"Failed to load {file_path}: {e}")
        return []

def load_multiple_pdfs(file_paths: list[str]) -> list:
    """Load multiple PDFs and return combined document list."""
    all_documents = []
    for path in file_paths:
        docs = load_pdf(path)
        all_documents.extend(docs)
    
    logger.info(f"Total pages loaded: {len(all_documents)}")
    return all_documents

def load_directory(directory_path: str) -> list:
    """Load all PDFs from a directory."""
    dir_path = Path(directory_path)
    pdf_files = list(dir_path.glob("*.pdf"))
    
    if not pdf_files:
        logger.warning(f"No PDF files found in {directory_path}")
        return []
    
    file_paths = [str(f) for f in pdf_files]
    return load_multiple_pdfs(file_paths)
```

---

### Task 1.5 — `app/ingestion/chunker.py`

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

def chunk_documents(documents: list) -> list:
    """
    Split documents into chunks using RecursiveCharacterTextSplitter.
    
    Strategy:
    - chunk_size=700: Stays within embedding model context limits
    - chunk_overlap=120: Preserves semantic continuity at chunk boundaries
    - Recursive splitting: Tries to split on paragraphs, sentences, words in order
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    
    chunks = splitter.split_documents(documents)
    
    # Assign chunk IDs
    for i, chunk in enumerate(chunks):
        chunk.metadata["chunk_id"] = i
        # Clean up text
        chunk.page_content = clean_text(chunk.page_content)
    
    # Filter empty chunks
    chunks = [c for c in chunks if len(c.page_content.strip()) > 50]
    
    logger.info(f"Created {len(chunks)} chunks from {len(documents)} pages")
    return chunks

def clean_text(text: str) -> str:
    """Remove excessive whitespace and artifacts."""
    import re
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)  # Remove non-ASCII artifacts
    return text.strip()
```

---

### Task 1.6 — `app/ingestion/embedder.py`

```python
from sentence_transformers import SentenceTransformer
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# Load model once at module level (not per request)
_model = None

def get_embedding_model() -> SentenceTransformer:
    global _model
    if _model is None:
        logger.info(f"Loading embedding model: {settings.embedding_model}")
        _model = SentenceTransformer(settings.embedding_model)
    return _model

def embed_texts(texts: list[str]) -> list[list[float]]:
    """Generate embeddings for a list of texts."""
    model = get_embedding_model()
    embeddings = model.encode(texts, show_progress_bar=True, batch_size=32)
    return embeddings.tolist()

def embed_query(query: str) -> list[float]:
    """Generate embedding for a single query."""
    model = get_embedding_model()
    embedding = model.encode([query])
    return embedding[0].tolist()
```

---

### Task 1.7 — `app/vectorstore/schema.py`

```python
from pydantic import BaseModel
from typing import Optional

class ChunkMetadata(BaseModel):
    source: str
    page: int
    chunk_id: int
    file_path: Optional[str] = None

class SearchResult(BaseModel):
    content: str
    metadata: ChunkMetadata
    similarity_score: float
    snippet: str
```

---

### Task 1.8 — `app/vectorstore/chroma_db.py`

```python
import chromadb
from chromadb.config import Settings as ChromaSettings
from app.core.config import settings
from app.ingestion.embedder import embed_texts, embed_query
import logging

logger = logging.getLogger(__name__)

_client = None
_collection = None

def get_chroma_client():
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(
            path=settings.chroma_persist_dir,
        )
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
    """Add document chunks to ChromaDB."""
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
    
    # Generate embeddings
    embeddings = embed_texts(texts)
    
    # Add to ChromaDB in batches
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
    """Search for similar chunks."""
    collection = get_collection()
    query_embedding = embed_query(query)
    
    where_filter = None
    if filter_source:
        where_filter = {"source": {"$eq": filter_source}}
    
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
            # ChromaDB cosine distance: convert to similarity
            similarity = 1 - dist
            search_results.append({
                "content": doc,
                "metadata": meta,
                "similarity_score": round(similarity, 4),
                "snippet": doc[:200]
            })
    
    return search_results

def get_collection_stats() -> dict:
    """Get stats about the current collection."""
    try:
        collection = get_collection()
        count = collection.count()
        
        # Get unique sources
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
    """Delete and recreate the collection."""
    global _collection
    client = get_chroma_client()
    try:
        client.delete_collection(settings.collection_name)
    except Exception:
        pass
    _collection = None
    return get_collection()
```

---

### Task 1.9 — `app/ingestion/pipeline.py`

```python
from app.ingestion.loader import load_directory, load_multiple_pdfs
from app.ingestion.chunker import chunk_documents
from app.vectorstore.chroma_db import add_chunks_to_db, get_collection_stats
import logging
import os

logger = logging.getLogger(__name__)

def run_ingestion_pipeline(file_paths: list[str] = None, directory: str = None) -> dict:
    """
    Full ingestion pipeline:
    Load PDFs → Chunk → Embed → Store in ChromaDB
    """
    # Step 1: Load documents
    if file_paths:
        documents = load_multiple_pdfs(file_paths)
    elif directory:
        documents = load_directory(directory)
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
```

**Checkpoint:** Run `python -c "from app.ingestion.pipeline import run_ingestion_pipeline; print(run_ingestion_pipeline())"` — ChromaDB populated.

---

## PHASE 2 — Core RAG + /ask Endpoint (Hour 3–5)

**Goal:** Working Q&A with citations and hallucination prevention.

### Task 2.1 — `app/llm/gemini_client.py`

```python
import google.generativeai as genai
from app.core.config import settings
import logging
import time

logger = logging.getLogger(__name__)

genai.configure(api_key=settings.gemini_api_key)
_model = None

def get_gemini_model():
    global _model
    if _model is None:
        _model = genai.GenerativeModel("gemini-1.5-flash")
    return _model

def generate(prompt: str, max_retries: int = 3) -> str:
    """Generate response from Gemini with retry logic."""
    model = get_gemini_model()
    
    for attempt in range(max_retries):
        try:
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.warning(f"Gemini attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                raise
    
    raise RuntimeError("Gemini API failed after all retries")
```

---

### Task 2.2 — `app/llm/translator.py`

```python
from langdetect import detect
from app.llm.gemini_client import generate
from app.core.prompts import TRANSLATION_PROMPT
import logging

logger = logging.getLogger(__name__)

LANGUAGE_NAMES = {
    "en": "English",
    "hi": "Hindi",
    "fr": "French",
    "de": "German",
    "es": "Spanish",
    "zh": "Chinese",
    "ar": "Arabic"
}

def detect_language(text: str) -> str:
    """Detect language of input text."""
    try:
        lang = detect(text)
        return lang
    except Exception:
        return "en"

def translate_text(text: str, target_language: str) -> str:
    """Translate text to target language using Gemini."""
    if target_language == "en":
        return text
    
    target_name = LANGUAGE_NAMES.get(target_language, target_language)
    prompt = TRANSLATION_PROMPT.format(
        target_language=target_name,
        text=text
    )
    
    try:
        translated = generate(prompt)
        return translated.strip()
    except Exception as e:
        logger.error(f"Translation failed: {e}")
        return text  # Fallback to original

def prepare_query(query: str, declared_language: str = None) -> tuple[str, str]:
    """
    Detect language, translate to English for retrieval.
    Returns (english_query, original_language)
    """
    detected_lang = detect_language(query)
    original_lang = declared_language or detected_lang
    
    if original_lang == "en" or detected_lang == "en":
        return query, "en"
    
    english_query = translate_text(query, "en")
    logger.info(f"Translated query from {original_lang} to English")
    return english_query, original_lang
```

---

### Task 2.3 — `app/llm/guardrails.py`

```python
from app.core.constants import FALLBACK_MESSAGE

def is_fallback_response(answer: str) -> bool:
    """Check if the LLM fell back to the safety message."""
    fallback_indicators = [
        "do not contain enough information",
        "cannot answer",
        "not found in the context",
        FALLBACK_MESSAGE.lower()
    ]
    return any(indicator in answer.lower() for indicator in fallback_indicators)

def validate_response(answer: str, context_chunks: list) -> dict:
    """Basic validation of LLM response quality."""
    is_fallback = is_fallback_response(answer)
    
    return {
        "is_fallback": is_fallback,
        "answer_length": len(answer),
        "context_chunks_used": len(context_chunks),
        "has_answer": not is_fallback and len(answer) > 20
    }
```

---

### Task 2.4 — `app/retrieval/retriever.py`

```python
from app.vectorstore.chroma_db import similarity_search
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

def retrieve_chunks(query: str, top_k: int = None, filter_source: str = None) -> list:
    """Retrieve top-K relevant chunks for a query."""
    k = top_k or settings.top_k
    
    results = similarity_search(query, top_k=k, filter_source=filter_source)
    
    logger.info(f"Retrieved {len(results)} chunks for query: {query[:50]}...")
    return results

def retrieve_for_contradiction(query: str, doc1: str, doc2: str, top_k: int = 3) -> tuple:
    """Retrieve chunks from two specific documents."""
    chunks_doc1 = similarity_search(query, top_k=top_k, filter_source=doc1)
    chunks_doc2 = similarity_search(query, top_k=top_k, filter_source=doc2)
    
    return chunks_doc1, chunks_doc2
```

---

### Task 2.5 — `app/retrieval/reranker.py`

```python
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
    """
    Rerank retrieved chunks using cross-encoder.
    More accurate than vector similarity alone.
    """
    if not chunks:
        return chunks
    
    try:
        reranker = get_reranker()
        
        pairs = [(query, chunk["content"]) for chunk in chunks]
        scores = reranker.predict(pairs)
        
        # Attach reranker scores
        for chunk, score in zip(chunks, scores):
            chunk["reranker_score"] = float(score)
        
        # Sort by reranker score
        reranked = sorted(chunks, key=lambda x: x["reranker_score"], reverse=True)
        return reranked[:top_k]
    
    except Exception as e:
        logger.warning(f"Reranking failed, using original order: {e}")
        return chunks[:top_k]
```

---

### Task 2.6 — `app/retrieval/citation_builder.py`

```python
from app.core.constants import SNIPPET_LENGTH

def build_citations(chunks: list) -> list:
    """Build citation objects from retrieved chunks."""
    citations = []
    seen_ids = set()
    
    for chunk in chunks:
        meta = chunk.get("metadata", {})
        chunk_id = meta.get("chunk_id", 0)
        source = meta.get("source", "unknown")
        
        # Deduplicate by chunk_id + source
        dedup_key = f"{source}_{chunk_id}"
        if dedup_key in seen_ids:
            continue
        seen_ids.add(dedup_key)
        
        citation = {
            "source_file": source,
            "page": meta.get("page", 0),
            "chunk_id": chunk_id,
            "snippet": chunk.get("content", "")[:SNIPPET_LENGTH],
            "similarity_score": chunk.get("similarity_score", 0.0)
        }
        citations.append(citation)
    
    return citations

def build_context_string(chunks: list) -> str:
    """Build context string from chunks for LLM prompt."""
    context_parts = []
    for i, chunk in enumerate(chunks):
        meta = chunk.get("metadata", {})
        source = meta.get("source", "unknown")
        page = meta.get("page", 0)
        content = chunk.get("content", "")
        
        context_parts.append(
            f"[Source: {source}, Page: {page}]\n{content}"
        )
    
    return "\n\n---\n\n".join(context_parts)

def compute_confidence(chunks: list) -> float:
    """Compute confidence score from similarity scores."""
    if not chunks:
        return 0.0
    
    scores = [c.get("similarity_score", 0.0) for c in chunks]
    avg_score = sum(scores) / len(scores)
    return round(avg_score, 4)
```

---

### Task 2.7 — `app/api/ask.py`

```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from app.retrieval.retriever import retrieve_chunks
from app.retrieval.reranker import rerank_chunks
from app.retrieval.citation_builder import build_citations, build_context_string, compute_confidence
from app.llm.gemini_client import generate
from app.llm.translator import prepare_query, translate_text
from app.llm.guardrails import validate_response
from app.core.prompts import QA_PROMPT_TEMPLATE
from app.core.constants import FALLBACK_MESSAGE
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

class AskRequest(BaseModel):
    query: str
    language: Optional[str] = "en"
    top_k: Optional[int] = 5
    use_reranker: Optional[bool] = True

class AskResponse(BaseModel):
    answer: str
    citations: list
    confidence: float
    language: str
    is_fallback: bool

@router.post("/ask", response_model=AskResponse)
async def ask(request: AskRequest):
    try:
        # Step 1: Translate query to English if needed
        english_query, original_language = prepare_query(
            request.query, 
            request.language
        )
        
        # Step 2: Retrieve chunks
        chunks = retrieve_chunks(english_query, top_k=request.top_k * 2)  # Retrieve extra for reranking
        
        if not chunks:
            return AskResponse(
                answer=FALLBACK_MESSAGE,
                citations=[],
                confidence=0.0,
                language=original_language,
                is_fallback=True
            )
        
        # Step 3: Rerank
        if request.use_reranker:
            chunks = rerank_chunks(english_query, chunks, top_k=request.top_k)
        else:
            chunks = chunks[:request.top_k]
        
        # Step 4: Build context
        context = build_context_string(chunks)
        
        # Step 5: Generate answer
        prompt = QA_PROMPT_TEMPLATE.format(
            context=context,
            question=english_query
        )
        answer = generate(prompt)
        
        # Step 6: Translate answer back if needed
        if original_language != "en":
            answer = translate_text(answer, original_language)
        
        # Step 7: Build citations and confidence
        citations = build_citations(chunks)
        confidence = compute_confidence(chunks)
        
        # Step 8: Validate
        validation = validate_response(answer, chunks)
        
        return AskResponse(
            answer=answer,
            citations=citations,
            confidence=confidence,
            language=original_language,
            is_fallback=validation["is_fallback"]
        )
    
    except Exception as e:
        logger.error(f"Error in /ask: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

---

### Task 2.8 — `app/api/health.py`

```python
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
```

---

### Task 2.9 — `app/main.py`

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import ask, health, contradict
from app.ingestion.pipeline import run_ingestion_pipeline
from pydantic import BaseModel
from typing import Optional, List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Research Paper RAG Assistant",
    description="RAG system for querying research papers with citations",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ask.router, tags=["QA"])
app.include_router(health.router, tags=["Health"])
app.include_router(contradict.router, tags=["Contradiction"])

class IngestRequest(BaseModel):
    file_paths: Optional[List[str]] = None
    directory: Optional[str] = None

@app.post("/ingest", tags=["Ingestion"])
async def ingest(request: IngestRequest = None):
    result = run_ingestion_pipeline(
        file_paths=request.file_paths if request else None,
        directory=request.directory if request else None
    )
    return result

@app.get("/", tags=["Root"])
async def root():
    return {"message": "Research Paper RAG Assistant API", "docs": "/docs"}
```

---

### Task 2.10 — `run.py`

```python
import uvicorn
import subprocess
import sys
import os

def run_api():
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

def run_ui():
    subprocess.run([
        sys.executable, "-m", "streamlit", "run", 
        "app/ui/streamlit_app.py",
        "--server.port", "8501"
    ])

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "api"
    
    if mode == "api":
        run_api()
    elif mode == "ui":
        run_ui()
    elif mode == "ingest":
        from app.ingestion.pipeline import run_ingestion_pipeline
        result = run_ingestion_pipeline()
        print(result)
    else:
        print("Usage: python run.py [api|ui|ingest]")
```

**Checkpoint:** `python run.py api` starts server. `GET /health` returns 200. `POST /ask` returns answer with citations.

---

## PHASE 3 — Contradiction + Streamlit UI (Hour 5–6.5)

### Task 3.1 — `app/api/contradict.py`

```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import json

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
        # Retrieve relevant chunks from each doc
        chunks_doc1, chunks_doc2 = retrieve_for_contradiction(
            request.topic, request.doc1, request.doc2, top_k=3
        )
        
        if not chunks_doc1 and not chunks_doc2:
            raise HTTPException(
                status_code=404,
                detail=f"No content found for documents: {request.doc1}, {request.doc2}"
            )
        
        # Build context strings
        context1 = "\n\n".join([c["content"] for c in chunks_doc1]) or "No relevant content found."
        context2 = "\n\n".join([c["content"] for c in chunks_doc2]) or "No relevant content found."
        
        # Build prompt
        prompt = CONTRADICTION_PROMPT_TEMPLATE.format(
            topic=request.topic,
            doc1=request.doc1,
            doc2=request.doc2,
            context1=context1,
            context2=context2
        )
        
        # Generate analysis
        response_text = generate(prompt)
        
        # Parse JSON response
        try:
            # Extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
            else:
                raise ValueError("No JSON found")
        except (json.JSONDecodeError, ValueError):
            # Fallback if JSON parsing fails
            result = {
                "conflict": "conflict" in response_text.lower() or "contradict" in response_text.lower(),
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
```

---

### Task 3.2 — `app/ui/streamlit_app.py`

```python
import streamlit as st
import requests
import json
from pathlib import Path
import os

API_BASE = "http://localhost:8000"

st.set_page_config(
    page_title="Research Paper RAG Assistant",
    page_icon="📚",
    layout="wide"
)

# ─── Sidebar Navigation ────────────────────────────────────────────────────────

st.sidebar.title("📚 RAG Assistant")
st.sidebar.markdown("---")
page = st.sidebar.radio(
    "Navigate",
    ["🏠 Home", "📄 Upload Documents", "❓ Ask Questions", "⚡ Contradiction Checker"]
)

# ─── Health Check ──────────────────────────────────────────────────────────────

def check_health():
    try:
        r = requests.get(f"{API_BASE}/health", timeout=5)
        return r.json()
    except Exception:
        return None

# ─── Page: Home ────────────────────────────────────────────────────────────────

if page == "🏠 Home":
    st.title("📚 Research Paper RAG Assistant")
    st.markdown("""
    ### AI-Powered Research Paper Question Answering
    
    This system allows you to:
    - 📄 **Upload** research papers (PDF)
    - ❓ **Ask** natural language questions
    - 📎 **Get** cited answers with source references
    - ⚡ **Detect** contradictions between papers
    - 🌍 **Query** in multiple languages
    """)
    
    st.markdown("---")
    
    # System Status
    st.subheader("System Status")
    health = check_health()
    
    if health:
        col1, col2, col3 = st.columns(3)
        col1.metric("Status", "✅ Online")
        col2.metric("Documents", health.get("documents_loaded", 0))
        col3.metric("Chunks", health.get("total_chunks", 0))
        
        if health.get("documents"):
            st.subheader("Loaded Documents")
            for doc in health["documents"]:
                st.markdown(f"- 📄 `{doc}`")
    else:
        st.error("❌ API not reachable. Make sure `python run.py api` is running.")

# ─── Page: Upload Documents ────────────────────────────────────────────────────

elif page == "📄 Upload Documents":
    st.title("📄 Upload Documents")
    
    tab1, tab2 = st.tabs(["Upload PDFs", "Ingest from Directory"])
    
    with tab1:
        uploaded_files = st.file_uploader(
            "Upload PDF files",
            type=["pdf"],
            accept_multiple_files=True
        )
        
        if uploaded_files and st.button("📥 Ingest Documents", type="primary"):
            # Save uploaded files to data/raw
            saved_paths = []
            for uploaded_file in uploaded_files:
                save_path = f"./data/raw/{uploaded_file.name}"
                with open(save_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                saved_paths.append(save_path)
            
            with st.spinner("Ingesting documents... This may take a few minutes."):
                try:
                    r = requests.post(
                        f"{API_BASE}/ingest",
                        json={"file_paths": saved_paths},
                        timeout=300
                    )
                    result = r.json()
                    
                    if result.get("status") == "success":
                        st.success(f"✅ Successfully ingested {result['documents_processed']} documents!")
                        st.json(result)
                    else:
                        st.error(f"❌ Ingestion failed: {result.get('message', 'Unknown error')}")
                except Exception as e:
                    st.error(f"Error: {e}")
    
    with tab2:
        st.info("Auto-ingest all PDFs from `data/raw/` directory")
        if st.button("🔄 Ingest from data/raw/", type="primary"):
            with st.spinner("Ingesting..."):
                try:
                    r = requests.post(f"{API_BASE}/ingest", json={}, timeout=300)
                    result = r.json()
                    st.json(result)
                except Exception as e:
                    st.error(f"Error: {e}")

# ─── Page: Ask Questions ───────────────────────────────────────────────────────

elif page == "❓ Ask Questions":
    st.title("❓ Ask Research Questions")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        query = st.text_area(
            "Your Question",
            placeholder="What is the transformer architecture? How does attention work?",
            height=100
        )
    
    with col2:
        language = st.selectbox(
            "Language",
            options=["en", "hi", "fr", "de", "es"],
            format_func=lambda x: {
                "en": "🇬🇧 English",
                "hi": "🇮🇳 Hindi",
                "fr": "🇫🇷 French",
                "de": "🇩🇪 German",
                "es": "🇪🇸 Spanish"
            }[x]
        )
        top_k = st.slider("Results", 1, 10, 5)
        use_reranker = st.checkbox("Use Reranker", value=True)
    
    if st.button("🔍 Ask", type="primary") and query:
        with st.spinner("Searching and generating answer..."):
            try:
                r = requests.post(
                    f"{API_BASE}/ask",
                    json={
                        "query": query,
                        "language": language,
                        "top_k": top_k,
                        "use_reranker": use_reranker
                    },
                    timeout=60
                )
                result = r.json()
                
                # Display answer
                st.markdown("---")
                
                if result.get("is_fallback"):
                    st.warning("⚠️ " + result["answer"])
                else:
                    st.subheader("📝 Answer")
                    st.markdown(result["answer"])
                
                # Confidence
                confidence = result.get("confidence", 0)
                st.metric("Confidence Score", f"{confidence:.2%}")
                
                # Citations
                citations = result.get("citations", [])
                if citations:
                    st.subheader(f"📎 Citations ({len(citations)})")
                    
                    for i, cite in enumerate(citations):
                        with st.expander(
                            f"📄 {cite['source_file']} — Page {cite['page']} "
                            f"(Score: {cite.get('similarity_score', 0):.3f})"
                        ):
                            st.markdown(f"**Chunk ID:** {cite['chunk_id']}")
                            st.markdown(f"**Snippet:**")
                            st.markdown(f"> {cite['snippet']}")
                
            except Exception as e:
                st.error(f"Error: {e}")

# ─── Page: Contradiction Checker ───────────────────────────────────────────────

elif page == "⚡ Contradiction Checker":
    st.title("⚡ Contradiction Checker")
    st.markdown("Detect conflicting claims between two research papers.")
    
    # Get available documents
    health = check_health()
    available_docs = health.get("documents", []) if health else []
    
    if not available_docs:
        st.warning("No documents loaded. Please upload documents first.")
    else:
        col1, col2 = st.columns(2)
        
        with col1:
            doc1 = st.selectbox("Paper 1", options=available_docs)
        
        with col2:
            doc2 = st.selectbox("Paper 2", options=available_docs)
        
        topic = st.text_input(
            "Topic to Compare",
            placeholder="training efficiency, model accuracy, architecture..."
        )
        
        if st.button("⚡ Check for Contradictions", type="primary") and topic and doc1 != doc2:
            with st.spinner("Analyzing papers for contradictions..."):
                try:
                    r = requests.post(
                        f"{API_BASE}/contradict",
                        json={"doc1": doc1, "doc2": doc2, "topic": topic},
                        timeout=60
                    )
                    result = r.json()
                    
                    st.markdown("---")
                    
                    if result.get("conflict"):
                        st.error("⚡ Contradiction Detected!")
                    else:
                        st.success("✅ No significant contradiction found")
                    
                    st.subheader("Reasoning")
                    st.markdown(result.get("reasoning", ""))
                    
                    evidence = result.get("evidence", [])
                    if evidence:
                        st.subheader("Evidence")
                        for ev in evidence:
                            with st.expander(f"📄 {ev.get('source', 'Unknown')}"):
                                st.markdown(ev.get("claim", ev.get("snippet", "")))
                
                except Exception as e:
                    st.error(f"Error: {e}")
        
        elif doc1 == doc2:
            st.warning("Please select two different documents.")
```

**Checkpoint:** Both API and UI run. All 4 pages work.

---

## PHASE 4 — Polish, Tests, Examples (Hour 6.5–8)

### Task 4.1 — `tests/eval_dataset.json`

```json
{
  "questions": [
    {
      "id": 1,
      "query": "What is the transformer architecture?",
      "expected_source": "attention_is_all_you_need.pdf",
      "expected_keywords": ["encoder", "decoder", "attention", "self-attention"]
    },
    {
      "id": 2,
      "query": "What does BERT stand for and what is its pretraining objective?",
      "expected_source": "bert.pdf",
      "expected_keywords": ["Bidirectional", "masked language model", "next sentence"]
    },
    {
      "id": 3,
      "query": "How does LoRA reduce the number of trainable parameters?",
      "expected_source": "lora.pdf",
      "expected_keywords": ["low-rank", "decomposition", "freeze", "adapter"]
    }
  ]
}
```

---

### Task 4.2 — `tests/test_ask.py`

```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "documents_loaded" in data

def test_ask_basic():
    response = client.post("/ask", json={
        "query": "What is attention mechanism?",
        "language": "en",
        "top_k": 3
    })
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "citations" in data
    assert "confidence" in data
    assert isinstance(data["citations"], list)
    assert 0.0 <= data["confidence"] <= 1.0

def test_ask_empty_query():
    response = client.post("/ask", json={
        "query": "zzxyzxyzxyz totally random gibberish",
        "language": "en",
        "top_k": 5
    })
    assert response.status_code == 200
    data = response.json()
    # Should return fallback or low confidence
    assert "answer" in data

def test_ask_returns_citations():
    response = client.post("/ask", json={
        "query": "What is transformer architecture?",
        "language": "en"
    })
    data = response.json()
    if not data.get("is_fallback"):
        assert len(data["citations"]) > 0
        citation = data["citations"][0]
        assert "source_file" in citation
        assert "page" in citation
        assert "snippet" in citation
```

---

### Task 4.3 — `tests/test_contradict.py`

```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_contradict_endpoint_exists():
    response = client.post("/contradict", json={
        "doc1": "attention_is_all_you_need.pdf",
        "doc2": "bert.pdf",
        "topic": "model architecture"
    })
    # Either 200 or 404 (if docs not loaded) — not 500
    assert response.status_code in [200, 404]

def test_contradict_response_structure():
    response = client.post("/contradict", json={
        "doc1": "bert.pdf",
        "doc2": "gpt3.pdf",
        "topic": "training approach"
    })
    if response.status_code == 200:
        data = response.json()
        assert "conflict" in data
        assert "reasoning" in data
        assert "evidence" in data
        assert isinstance(data["conflict"], bool)
```

---

### Task 4.4 — `examples/sample_queries.json`

```json
{
  "queries": [
    {
      "id": 1,
      "query": "What is the transformer architecture?",
      "language": "en",
      "expected_topic": "transformer, attention mechanism"
    },
    {
      "id": 2,
      "query": "ट्रांसफार्मर आर्किटेक्चर क्या है?",
      "language": "hi",
      "expected_topic": "transformer in Hindi"
    },
    {
      "id": 3,
      "query": "How does BERT differ from GPT in pretraining?",
      "language": "en",
      "expected_topic": "BERT vs GPT comparison"
    },
    {
      "id": 4,
      "query": "What are the benefits of LoRA for fine-tuning?",
      "language": "en",
      "expected_topic": "LoRA, parameter efficient fine-tuning"
    },
    {
      "id": 5,
      "query": "What is retrieval augmented generation?",
      "language": "en",
      "expected_topic": "RAG overview"
    }
  ],
  "contradiction_queries": [
    {
      "doc1": "bert.pdf",
      "doc2": "gpt3.pdf",
      "topic": "pretraining strategy"
    },
    {
      "doc1": "attention_is_all_you_need.pdf",
      "doc2": "bert.pdf",
      "topic": "architecture design"
    }
  ]
}
```

---

## PHASE 5 — README + Documentation (Hour 8–9)

### Task 5.1 — Write README.md

```markdown
# 📚 Research Paper RAG Assistant

> A production-ready Retrieval-Augmented Generation (RAG) system for querying 
> AI/ML research papers with citations, contradiction detection, and multilingual support.

---

## 🏗️ Architecture

```
Documents (PDFs)
      ↓
  [Loader] — PyPDFLoader
      ↓
  [Chunker] — RecursiveCharacterTextSplitter
      ↓
  [Embedder] — all-MiniLM-L6-v2
      ↓
  [ChromaDB] — Persistent Vector Store
      ↓
  [Retriever] — Similarity Search
      ↓
  [Reranker] — Cross-Encoder ms-marco
      ↓
  [Gemini 1.5 Flash] — LLM
      ↓
  Answer + Citations + Confidence
```

---

## 🛠️ Tech Stack

| Component | Technology |
|---|---|
| Backend API | FastAPI |
| Frontend UI | Streamlit |
| Vector Database | ChromaDB |
| Embeddings | sentence-transformers/all-MiniLM-L6-v2 |
| LLM | Gemini 1.5 Flash |
| PDF Parsing | PyPDFLoader (LangChain) |
| Reranker | cross-encoder/ms-marco-MiniLM-L-6-v2 |
| Translation | Gemini (via prompt) |
| Language Detection | langdetect |

---

## 📦 Chunking Strategy

We use `RecursiveCharacterTextSplitter` with:
- **chunk_size = 700** — fits within embedding model context limits
- **chunk_overlap = 120** — preserves semantic continuity at boundaries

The splitter tries to split on paragraph breaks (`\n\n`), then line breaks (`\n`),
then sentences, then words — ensuring chunks are semantically meaningful.

Overlap is critical because answers often span chunk boundaries. Without overlap,
we would lose context at every split point.

---

## 🔍 Retrieval Pipeline

1. User submits query (any language)
2. Language detection + translation to English
3. Query embedded with same model as documents
4. Cosine similarity search in ChromaDB (top 10)
5. Cross-encoder reranking (top 5)
6. Context assembled with source metadata
7. Grounded prompt sent to Gemini
8. Answer translated back to user's language
9. Citations + confidence returned

---

## 🛡️ Hallucination Prevention

All prompts use grounded generation:

```
Answer ONLY from the provided context.
If not found, say: "The provided documents do not contain enough information."
```

The system never uses the LLM's prior knowledge — only retrieved context.

---

## 🚀 Setup

```bash
git clone <repo>
cd rag-document-qa

python -m venv venv
source venv/bin/activate

pip install -r requirements.txt

cp .env.example .env
# Add your GEMINI_API_KEY to .env

# Add PDFs to data/raw/
python run.py ingest

# Start API
python run.py api

# Start UI (separate terminal)
python run.py ui
```

---

## 📡 API Endpoints

### GET /health
Returns system status and loaded documents.

### POST /ask
```json
{
  "query": "What is transformer architecture?",
  "language": "en",
  "top_k": 5
}
```

### POST /contradict
```json
{
  "doc1": "bert.pdf",
  "doc2": "gpt3.pdf",
  "topic": "pretraining strategy"
}
```

### POST /ingest
```json
{
  "file_paths": ["data/raw/paper1.pdf"]
}
```

Full docs at `http://localhost:8000/docs`

---

## 📊 Citation Format

Every answer includes:
```json
{
  "source_file": "attention_is_all_you_need.pdf",
  "page": 4,
  "chunk_id": 14,
  "snippet": "The Transformer follows an encoder-decoder structure...",
  "similarity_score": 0.89
}
```

---

## 🌍 Multilingual Support

Supported: English, Hindi, French, German, Spanish

Flow: User query → detect language → translate to English → retrieve → 
generate → translate answer back → return

---

## 🔮 Future Improvements

- [ ] Streaming responses
- [ ] User authentication
- [ ] PDF annotation/highlighting
- [ ] Evaluation metrics (RAGAS)
- [ ] Cloud deployment (GCP/AWS)
- [ ] Support for more file types (DOCX, HTML)
```

---

## PHASE 6 — Final Review & Submission (Hour 9–10)

### Task 6.1 — Final Checklist

```
□ All 5 PDFs in data/raw/
□ python run.py ingest → succeeds
□ python run.py api → /health returns 200
□ POST /ask → returns answer + citations
□ POST /contradict → returns conflict analysis
□ python run.py ui → all 4 pages work
□ pytest tests/ → all pass
□ README complete with architecture diagram
□ .env not committed (in .gitignore)
□ requirements.txt complete
□ No hardcoded API keys
```

### Task 6.2 — Demo Script

Prepare these 5 demo queries:
1. "What is the transformer architecture?" (English)
2. "ट्रांसफार्मर क्या है?" (Hindi — shows multilingual)
3. "How does LoRA reduce parameters?" (shows specific citation)
4. Contradiction: bert.pdf vs gpt3.pdf, topic: "pretraining"
5. "What is quantum computing?" (shows graceful fallback)

### Task 6.3 — Interview Prep Answers

| Question | Answer |
|---|---|
| Why chunk_size=700? | Fits all-MiniLM-L6-v2's 256-token limit with buffer; balances context and precision |
| Why overlap=120? | ~17% overlap preserves cross-boundary semantic context |
| Why ChromaDB? | Zero-config persistent vector store; perfect for local demo |
| Why cosine similarity? | Scale-invariant; better for semantic similarity than Euclidean |
| How do citations work? | Each chunk carries metadata; top retrieved chunks become citations |
| Hallucination prevention? | Grounded prompt + explicit fallback instruction; no external knowledge allowed |
| Why reranker? | Vector search retrieves by embedding similarity; cross-encoder reranks by actual query-document relevance — more accurate |
| Vector vs keyword search? | Vector captures semantic meaning; keyword matches exact terms. Vector finds "car" when you ask "automobile" |

---

## Summary Timeline

```
00:00-01:00  Phase 0  ─ Project setup, structure, env, download papers
01:00-03:00  Phase 1  ─ loader → chunker → embedder → ChromaDB
03:00-05:00  Phase 2  ─ Gemini client → retriever → citations → /ask endpoint
05:00-06:30  Phase 3  ─ /contradict endpoint → Streamlit UI (all 4 pages)
06:30-08:00  Phase 4  ─ Tests → examples → polish → error handling
08:00-09:00  Phase 5  ─ README → documentation → screenshots
09:00-10:00  Phase 6  ─ Final review → demo prep → submission
```

**Critical path:** Phase 1 → Phase 2 → /ask working = minimum viable submission.
Everything after is polish that makes you stand out.