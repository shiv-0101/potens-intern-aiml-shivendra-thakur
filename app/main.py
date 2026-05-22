from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import ask, health, contradict
from app.ingestion.pipeline import run_ingestion_pipeline
from pydantic import BaseModel
from typing import Optional, List
import logging

logging.basicConfig(level=logging.INFO)

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
    return run_ingestion_pipeline(
        file_paths=request.file_paths if request else None,
        directory=request.directory if request else None
    )

@app.get("/", tags=["Root"])
async def root():
    return {"message": "Research Paper RAG Assistant API", "docs": "/docs"}