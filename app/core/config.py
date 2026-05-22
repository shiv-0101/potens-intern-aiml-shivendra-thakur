from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    gemini_api_key: str = ""          # keep for reference
    groq_api_key: str = ""            # add this
    gemini_model: str = "gemini-2.0-flash"
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