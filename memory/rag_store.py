"""
Memory & Knowledge Layer — RAG Vector Store

Responsibilities:
  1. Index FIA 2026 regulation documents and strategy history
  2. Retrieve the most relevant chunks for a given query
  3. Fire retrieval audit to the Overseer (Hook 2) after every query

Design decision: retrieve FIRST, reason SECOND.
This file is always called before the reasoning agents produce output.
Agents receive context from here before they generate anything.

ChromaDB chosen for MVP — drop-in replacement with Milvus or
IBM Watson Discovery for production scale.

Embeddings: sentence-transformers all-MiniLM-L6-v2 for MVP.
Swap to ibm/slate-125m-english-rtrvr via watsonx for production.
"""

import os
from pathlib import Path
from typing import Optional

import chromadb
from chromadb.utils import embedding_functions

from config import config
from models import RAGResult


class RAGStore:

    def __init__(self):
        self._client = chromadb.PersistentClient(path=config.chroma_path)
        self._embed_fn = (
            embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name="all-MiniLM-L6-v2"
            )
        )
        self._fia_collection = self._client.get_or_create_collection(
            name=config.fia_collection,
            embedding_function=self._embed_fn,
            metadata={"hnsw:space": "cosine"},
        )
        self._strategy_collection = self._client.get_or_create_collection(
            name=config.strategy_collection,
            embedding_function=self._embed_fn,
            metadata={"hnsw:space": "cosine"},
        )
        self._audit_callback = None

    def register_audit_callback(self, callback):
        """
        Overseer registers here to receive Hook 2 (retrieval audit).
        """
        self._audit_callback = callback

    # ── Indexing ─────────────────────────────────────────────────────────────

    def index_fia_regulations(self, documents: list[dict]) -> int:
        """
        Index FIA 2026 Technical Regulation documents.
        Each document: {"text": str, "section": str, "title": str}
        Returns the number of chunks indexed.
        """
        chunks, metadatas, ids = [], [], []
        for i, doc in enumerate(documents):
            # Chunk at paragraph boundaries — better retrieval than fixed size
            paragraphs = self._chunk_by_paragraph(doc["text"])
            for j, para in enumerate(paragraphs):
                chunks.append(para)
                metadatas.append({
                    "source": "FIA_2026_Technical_Regulations",
                    "section": doc.get("section", "Unknown"),
                    "title": doc.get("title", ""),
                    "chunk_index": j,
                })
                ids.append(f"fia_{i}_{j}")

        self._fia_collection.add(
            documents=chunks,
            metadatas=metadatas,
            ids=ids,
        )
        return len(chunks)

    def index_strategy_history(self, documents: list[dict]) -> int:
        """
        Index historical Ferrari strategy patterns.
        Each document: {"text": str, "race": str, "year": int, "outcome": str}
        """
        chunks, metadatas, ids = [], [], []
        for i, doc in enumerate(documents):
            paragraphs = self._chunk_by_paragraph(doc["text"])
            for j, para in enumerate(paragraphs):
                chunks.append(para)
                metadatas.append({
                    "source": f"StrategyHistory_{doc.get('year', '')}_{doc.get('race', '')}",
                    "race": doc.get("race", ""),
                    "year": str(doc.get("year", "")),
                    "outcome": doc.get("outcome", ""),
                })
                ids.append(f"strat_{i}_{j}")

        self._strategy_collection.add(
            documents=chunks,
            metadatas=metadatas,
            ids=ids,
        )
        return len(chunks)

    # ── Retrieval ─────────────────────────────────────────────────────────────

    def query_regulations(self, query: str, n_results: int = 3) -> RAGResult:
        """
        Query the FIA regulations collection.
        Called by the Regulation Agent before any reasoning begins.
        """
        return self._query(query, self._fia_collection, n_results)

    def query_strategy(self, query: str, n_results: int = 3) -> RAGResult:
        """
        Query the strategy history collection.
        Called by the Agentic Strategist before reasoning begins.
        """
        return self._query(query, self._strategy_collection, n_results)

    # ── Private ──────────────────────────────────────────────────────────────

    def _query(
        self,
        query: str,
        collection: chromadb.Collection,
        n_results: int,
    ) -> RAGResult:
        results = collection.query(
            query_texts=[query],
            n_results=n_results,
            include=["documents", "metadatas", "distances"],
        )

        docs = results["documents"][0] if results["documents"] else []
        metas = results["metadatas"][0] if results["metadatas"] else []
        # ChromaDB returns distances (lower = better); convert to similarity
        distances = results["distances"][0] if results["distances"] else []
        similarities = [1 - d for d in distances]

        citations = [
            f"{m.get('source', 'Unknown')} — {m.get('section', m.get('race', ''))}"
            for m in metas
        ]

        rag_result = RAGResult(
            chunks=docs,
            citations=citations,
            similarity_scores=similarities,
            query=query,
            collection_name=collection.name,
        )

        self._fire_audit(rag_result)
        return rag_result

    def _chunk_by_paragraph(self, text: str) -> list[str]:
        """
        Split at double newlines. Each paragraph is a meaningful unit
        for FIA regulation text — better than fixed character chunking.
        """
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        # Merge very short paragraphs with the next one
        merged, buffer = [], ""
        for p in paragraphs:
            buffer = f"{buffer} {p}".strip() if buffer else p
            if len(buffer) >= 150:
                merged.append(buffer)
                buffer = ""
        if buffer:
            merged.append(buffer)
        return merged

    def _fire_audit(self, result: RAGResult) -> None:
        """
        Governance Hook 2 — fires immediately after retrieval.
        The Overseer uses this to know what was retrieved before
        it runs the pre-delivery cross-validation check.
        """
        if self._audit_callback:
            self._audit_callback("retrieval_audit", {
                "query": result.query,
                "collection": result.collection_name,
                "num_results": len(result.chunks),
                "top_similarity": max(result.similarity_scores) if result.similarity_scores else 0.0,
                "citations": result.citations,
                "meets_threshold": result.meets_threshold(config.confidence_threshold),
                "chunks": result.chunks,   # stored for Overseer cross-validation
            })
