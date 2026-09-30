"""
Benchmark runner — creates isolated, in-memory RAG pipelines for each config.

Nothing here modifies the persistent chat pipeline:
  - No save_local() calls (FAISS stays in RAM only)
  - No singleton touching (embeddings.py / semantic_chunker.py singletons untouched)
  - Transcript files are read read-only
"""

from __future__ import annotations

import asyncio
import os
import time
from pathlib import Path
from typing import Optional

from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_experimental.text_splitter import SemanticChunker
from langchain_text_splitters import RecursiveCharacterTextSplitter, TokenTextSplitter
from langchain_core.language_models import BaseChatModel
from langchain.chat_models import init_chat_model

from benchmark.config import BenchmarkConfig, ChunkingStrategy
from benchmark.evaluator import compute_metrics

# ── Embedding cache — avoid re-downloading weights for the same model id ──────
_embedding_cache: dict[str, HuggingFaceEmbeddings] = {}
_cache_lock = asyncio.Lock()


async def _get_embeddings(model_id: str) -> HuggingFaceEmbeddings:
    async with _cache_lock:
        if model_id not in _embedding_cache:
            _embedding_cache[model_id] = HuggingFaceEmbeddings(model_name=model_id)
        return _embedding_cache[model_id]


# ── Chunking helpers ───────────────────────────────────────────────────────────

def _chunk_semantic(text: str, embeddings: HuggingFaceEmbeddings) -> list[Document]:
    splitter = SemanticChunker(
        embeddings=embeddings,
        breakpoint_threshold_type="percentile",
        breakpoint_threshold_amount=95,
    )
    return splitter.create_documents([text])


def _chunk_recursive(text: str, chunk_size: int, overlap: int) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap,
        length_function=len,
    )
    return splitter.create_documents([text])


def _chunk_token(text: str, chunk_size: int, overlap: int) -> list[Document]:
    splitter = TokenTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap,
    )
    return splitter.create_documents([text])


def _apply_chunking(
    text: str,
    strategy: ChunkingStrategy,
    embeddings: HuggingFaceEmbeddings,
) -> list[Document]:
    if strategy == "semantic_percentile":
        return _chunk_semantic(text, embeddings)

    parts = strategy.split("_")           # e.g. ["recursive", "512"]
    splitter_type = parts[0]             # "recursive" | "token"
    chunk_size = int(parts[1])
    overlap = chunk_size // 10           # ~10 % overlap

    if splitter_type == "recursive":
        return _chunk_recursive(text, chunk_size, overlap)
    elif splitter_type == "token":
        return _chunk_token(text, chunk_size, overlap)

    raise ValueError(f"Unknown chunking strategy: {strategy}")


# ── In-memory FAISS builder ───────────────────────────────────────────────────

def _build_temp_faiss(chunks: list[Document], embeddings: HuggingFaceEmbeddings) -> FAISS:
    return FAISS.from_documents(chunks, embeddings)


# ── LLM factory — matches main app pattern (OpenRouter) ──────────────────────

def _create_llm(model_id: str) -> BaseChatModel:
    return init_chat_model(
        model=model_id,
        model_provider="openai",
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENROUTER_API_KEY"),
        temperature=0.0,
        max_retries=2,
    )


# ── Single config runner ──────────────────────────────────────────────────────

async def run_single_config(
    transcript_path: str,
    question: str,
    ground_truth: Optional[str],
    config: BenchmarkConfig,
) -> dict:
    """
    Build a fresh in-memory RAG pipeline for `config`, run the question,
    score with DeepEval, and return a BenchmarkResult-compatible dict.
    """
    t0 = time.monotonic()

    try:
        # 1. Read transcript
        text = Path(transcript_path).read_text(encoding="utf-8")

        # 2. Embeddings (cached per model id)
        embeddings = await _get_embeddings(config.embedding_model)

        # 3. Chunk — SemanticChunker is CPU-bound so we run it in a thread
        loop = asyncio.get_event_loop()
        chunks: list[Document] = await loop.run_in_executor(
            None,
            lambda: _apply_chunking(text, config.chunking_strategy, embeddings),
        )

        # 4. Build in-memory FAISS (also CPU/IO-bound)
        vectorstore: FAISS = await loop.run_in_executor(
            None,
            lambda: _build_temp_faiss(chunks, embeddings),
        )

        # 5. Retrieve top-k chunks
        retriever = vectorstore.as_retriever(search_kwargs={"k": config.top_k})
        retrieved_docs = await retriever.ainvoke(question)
        retrieved_texts = [doc.page_content for doc in retrieved_docs]
        context = "\n\n".join(retrieved_texts)

        # 6. Generate answer via LLM
        llm = _create_llm(config.llm)
        prompt = (
            "You are a helpful assistant. Use ONLY the provided context to answer.\n\n"
            f"Context:\n{context}\n\n"
            f"Question: {question}\n\n"
            "Answer:"
        )
        response = await llm.ainvoke(prompt)
        answer: str = response.content if hasattr(response, "content") else str(response)

        latency_ms = int((time.monotonic() - t0) * 1000)

        # 7. Evaluate with DeepEval
        metrics = await compute_metrics(
            question=question,
            answer=answer,
            retrieved_chunks=retrieved_texts,
            ground_truth=ground_truth,
        )

        return {
            "config_id": config.config_id,
            "llm": config.llm,
            "embedding_model": config.embedding_model,
            "chunking_strategy": config.chunking_strategy,
            "top_k": config.top_k,
            "answer": answer,
            "retrieved_chunks": retrieved_texts,
            "latency_ms": latency_ms,
            "metrics": metrics,
            "error": None,
        }

    except Exception as exc:  # noqa: BLE001
        latency_ms = int((time.monotonic() - t0) * 1000)
        return {
            "config_id": config.config_id,
            "llm": config.llm,
            "embedding_model": config.embedding_model,
            "chunking_strategy": config.chunking_strategy,
            "top_k": config.top_k,
            "answer": "",
            "retrieved_chunks": [],
            "latency_ms": latency_ms,
            "metrics": {
                "answer_relevancy": None,
                "faithfulness": None,
                "contextual_precision": None,
                "contextual_recall": None,
                "contextual_relevancy": None,
                "score_global": None,
            },
            "error": str(exc),
        }
