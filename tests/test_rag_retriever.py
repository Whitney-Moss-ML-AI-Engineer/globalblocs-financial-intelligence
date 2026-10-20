from pathlib import Path

from globalblocs.rag.retriever import RepositoryRetriever


def test_retriever_finds_relevant_passage(tmp_path: Path):
    (tmp_path / "sources.md").write_text(
        "# Official Data Sources\\n\\nBIS banking statistics and WTO import export trade data "
        "support cross-country financial intelligence research.\\n",
        encoding="utf-8",
    )
    retriever = RepositoryRetriever(root=tmp_path, chunk_words=80, overlap_words=10)
    results = retriever.search("WTO import export trade data", top_k=3)
    assert results
    assert results[0]["path"] == "sources.md"
    assert "WTO" in results[0]["excerpt"]
