# AI / ML

**What we are testing:** how you wire LLM components end-to-end, your honesty about model limits, and whether your prompts and traces look like a person who thought about it rather than someone who copied a tutorial.

---

## What This Repo Implements

### Q1. Document Q&A with Citations
RAG over research papers with ingestion, chunking, embeddings, Chroma vector storage, optional reranking, and citations.

### Q2. Triage Agent with Real Tool Calling
Not implemented in this repo.

---

## How To Run

### 1) Setup
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

### 2) Configure
Create a `.env` file in the project root:
```
GROQ_API_KEY=your_key_here
```

### 3) Run API
```powershell
python run.py api
```

### 4) Run UI
```powershell
python run.py ui
```

### 5) Ingest Documents
Put PDFs in `data/raw/` and run:
```powershell
python run.py 
```
Or use the UI upload tab to send files to `/ingest`.

---

## Design Decisions

- **Chunking strategy:** RecursiveCharacterTextSplitter with chunk size 700 and overlap 120, using paragraph -> sentence -> word fallbacks. Chunks shorter than 50 characters are dropped to reduce noise.
- **Embeddings:** sentence-transformers/all-MiniLM-L6-v2 for fast, local embeddings.
- **Vector store:** Chroma persistent client with cosine similarity and on-disk persistence at ./data/embeddings.
- **Reranking:** Optional CrossEncoder ms-marco-MiniLM-L-6-v2 reranks top-k results; failure falls back to original ranking.
- **Language handling:** Language detected with langdetect. Non-English queries are translated to English for retrieval, then answers are returned in the original language.
- **LLM generation:** Groq llama-3.3-70b-versatile for response generation with low temperature and retries.
- **No silent hallucinations:** When retrieval is empty or weak, the API returns a fallback message instead of an invented answer.
- **Citations:** Each cited chunk includes source, page, chunk id, and snippet (first 200 characters).

---


## AI USE LOG

- GitHub Copilot: ~20 messages. Used for README edits and code assistance in this repo.
- Gemini: ~20-30 messages. Used for drafting prompts and checking output quality.
- ChatGPT: ~10-15 messages. Used for quick sanity checks and alternative phrasing.
- Arena AI: 8-10 messages with Claude Sonnet 4.6 and 2-3 message comparisons with GPT-5.2. Used for PRD comparison and prompt evaluation.
- Groq (llama-3.3-70b-versatile): Used as the runtime LLM for generation. Logs stored in [LLM logs/](LLM%20logs/).
