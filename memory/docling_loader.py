"""
Memory & Knowledge Layer — Docling Document Loader

Parses PDFs, Word, HTML, and Markdown files using IBM Docling and indexes
chunks into the same ChromaDB collections that RAGStore queries.

Feeding through RAGStore.index_*() guarantees:
  - Same collection names (fia_2026_regulations / strategy_history)
  - Same embedding function (DefaultEmbeddingFunction / all-MiniLM-L6-v2)
  - Same metadata schema, so _query() builds citations correctly

Citation flow:
  DoclingLoader._to_fia_docs() → {"section": heading_text}
  → RAGStore stores metadata["section"]
  → _query() builds "FIA_2026_Technical_Regulations — {section}"
  → RAGResult.citations[] → best_citation() → Narrative.citation
"""

from pathlib import Path

from docling.chunking import HybridChunker
from docling.document_converter import DocumentConverter

from memory.rag_store import RAGStore


class DoclingLoader:

    def __init__(self):
        self._converter = DocumentConverter()
        # max_tokens=384 keeps chunks within all-MiniLM-L6-v2's 512-token limit
        self._chunker = HybridChunker(max_tokens=384)

    def load_regulations(self, path: str | Path, rag_store: RAGStore) -> int:
        """
        Parse a regulation document and index into the FIA regulations
        collection. Returns the number of chunks indexed.
        """
        docs = self._to_fia_docs(Path(path))
        return rag_store.index_fia_regulations(docs)

    def load_strategy(
        self,
        path: str | Path,
        rag_store: RAGStore,
        race: str = "",
        year: int = 0,
        outcome: str = "",
    ) -> int:
        """
        Parse a strategy document and index into the strategy history
        collection. Returns the number of chunks indexed.
        """
        docs = self._to_strategy_docs(Path(path), race=race, year=year, outcome=outcome)
        return rag_store.index_strategy_history(docs)

    # ── Private ───────────────────────────────────────────────────────────────

    # Top-level headings that appear on every page header and TOC — not useful as chunk labels
    _NOISE_SECTIONS = frozenset({
        "SECTION C: TECHNICAL REGULATIONS",
        "SECTION B: SPORTING REGULATIONS",
        "CONTENTS:",
        "CONVENTION:",
    })

    def _to_fia_docs(self, path: Path) -> list[dict]:
        """
        Produce list[{"text", "section", "title"}] from a document file.
        Matches the schema expected by RAGStore.index_fia_regulations().
        """
        conv = self._converter.convert(str(path))
        doc = conv.document
        title = doc.name or path.stem

        result = []
        for chunk in self._chunker.chunk(doc):
            text = chunk.text.strip()
            if not text or len(text) < 60:
                continue
            headings = getattr(chunk.meta, "headings", None) or []
            section = headings[-1] if headings else "Unknown"
            # Skip TOC rows and page-header noise — they have no article heading
            # and pollute retrieval with high-scoring junk matches
            if section in self._NOISE_SECTIONS:
                continue
            result.append({"text": text, "section": section, "title": title})
        return result

    def _to_strategy_docs(
        self, path: Path, race: str, year: int, outcome: str
    ) -> list[dict]:
        """
        Produce list[{"text", "race", "year", "outcome"}] from a document file.
        Matches the schema expected by RAGStore.index_strategy_history().
        """
        conv = self._converter.convert(str(path))
        doc = conv.document

        result = []
        for chunk in self._chunker.chunk(doc):
            text = chunk.text.strip()
            if not text:
                continue
            result.append({
                "text": text,
                "race": race or path.stem,
                "year": year,
                "outcome": outcome,
            })
        return result
