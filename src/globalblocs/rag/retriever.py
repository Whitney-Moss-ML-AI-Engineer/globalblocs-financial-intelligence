"""Lightweight lexical retrieval starter for repository-grounded RAG.

This is a lexical baseline, not a vector database or an LLM generator. Extend it
with hybrid BM25/embedding retrieval and a configured generation provider.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Iterable

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


@dataclass(frozen=True)
class Passage:
    source_id: str
    title: str
    path: str
    text: str


class RepositoryRetriever:
    """Indexes selected repository docs/config/code and returns ranked evidence."""

    DEFAULT_ROOT = Path(__file__).resolve().parents[3]
    ALLOWED_SUFFIXES = {".md", ".yaml", ".yml", ".sql", ".py", ".toml"}

    def __init__(self, root: Path | None = None, chunk_words: int = 180, overlap_words: int = 30):
        self.root = (root or self.DEFAULT_ROOT).resolve()
        self.chunk_words = max(40, chunk_words)
        self.overlap_words = max(0, min(overlap_words, self.chunk_words // 2))
        self.passages: list[Passage] = []
        self.vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), max_features=60000)
        self.matrix = None
        self.refresh()

    def _files(self) -> Iterable[Path]:
        for path in self.root.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in self.ALLOWED_SUFFIXES:
                continue
            if any(part in {".git", ".venv", "node_modules", "__pycache__", "dist", "build"} for part in path.parts):
                continue
            if path.stat().st_size > 2_000_000:
                continue
            yield path

    def refresh(self) -> int:
        passages: list[Passage] = []
        step = self.chunk_words - self.overlap_words
        for path in sorted(self._files()):
            try:
                text = path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            words = re.findall(r"\S+", text)
            if not words:
                continue
            relative = path.relative_to(self.root).as_posix()
            title = path.stem.replace("_", " ").replace("-", " ").title()
            for index, start in enumerate(range(0, len(words), step), start=1):
                chunk = " ".join(words[start : start + self.chunk_words])
                if len(chunk.strip()) < 30:
                    continue
                passages.append(Passage(
                    source_id=f"{relative}#chunk-{index}",
                    title=title,
                    path=relative,
                    text=chunk,
                ))
        self.passages = passages
        self.matrix = self.vectorizer.fit_transform([p.text for p in passages]) if passages else None
        return len(passages)

    def search(self, query: str, top_k: int = 6) -> list[dict[str, object]]:
        if not query.strip() or self.matrix is None:
            return []
        query_vector = self.vectorizer.transform([query])
        scores = cosine_similarity(query_vector, self.matrix).ravel()
        indexes = scores.argsort()[::-1]
        results = []
        for index in indexes:
            score = float(scores[index])
            if score <= 0:
                break
            passage = self.passages[int(index)]
            results.append({
                "source_id": passage.source_id,
                "title": passage.title,
                "path": passage.path,
                "score": round(score, 4),
                "excerpt": passage.text[:1400],
            })
            if len(results) >= max(1, min(top_k, 20)):
                break
        return results
