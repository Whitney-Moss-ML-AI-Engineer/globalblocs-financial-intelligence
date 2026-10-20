"""Repository RAG endpoints; retrieval is lexical until an LLM/vector provider is configured."""
from __future__ import annotations

from functools import lru_cache
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from globalblocs.rag.retriever import RepositoryRetriever

router = APIRouter(prefix="/api/v1/rag", tags=["retrieval-augmented-generation"])


class RAGQuery(BaseModel):
    query: str = Field(min_length=3, max_length=2000)
    top_k: int = Field(default=6, ge=1, le=20)


@lru_cache(maxsize=1)
def _retriever() -> RepositoryRetriever:
    return RepositoryRetriever()


@router.get("/health")
def rag_health() -> dict[str, Any]:
    retriever = _retriever()
    return {
        "status": "ok",
        "retrieval_mode": "repository_tfidf",
        "generation_mode": "not_configured",
        "indexed_passages": len(retriever.passages),
        "note": "Lexical evidence retrieval is active. A language-model generator and vector index are not yet configured.",
    }


@router.post("/query")
def rag_query(request: RAGQuery) -> dict[str, Any]:
    try:
        evidence = _retriever().search(request.query, request.top_k)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Repository retrieval failed: {type(exc).__name__}")
    if not evidence:
        return {
            "query": request.query,
            "answer": "I could not find relevant indexed repository evidence. Try a more specific question or verify that the relevant source is in the repository.",
            "answer_mode": "retrieval_only",
            "citations": [],
            "limitations": ["No relevant passage was retrieved.", "No LLM generation is configured."],
        }
    return {
        "query": request.query,
        "answer": (
            "Repository evidence was retrieved for this question. This starter returns cited evidence "
            "rather than synthesizing a final answer with an LLM. Review the cited passages before "
            "using them in research or investment analysis."
        ),
        "answer_mode": "retrieval_only",
        "citations": evidence,
        "limitations": [
            "TF-IDF lexical ranking is a starter retriever, not semantic vector search.",
            "An LLM generator, hybrid reranker, and structured-data retrieval are not configured yet.",
            "Repository documentation does not substitute for current validated market observations.",
        ],
    }


@router.post("/refresh")
def refresh_index() -> dict[str, Any]:
    """Rebuild the in-memory index. Protect this endpoint with admin auth before deployment."""
    retriever = _retriever()
    count = retriever.refresh()
    return {"status": "refreshed", "indexed_passages": count, "mode": "repository_tfidf"}
