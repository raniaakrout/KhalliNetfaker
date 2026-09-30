"""
Benchmark configuration dataclasses.

LLMs are accessed via OpenRouter (same base_url as the main app).
Temperature is fixed at 0.0 for deterministic, reproducible results.
"""

from dataclasses import dataclass, field
from typing import Literal

# ── Types ─────────────────────────────────────────────────────────────────────

ChunkingStrategy = Literal[
    # Semantic (LangChain SemanticChunker)
    "semantic_percentile",
    # Recursive character splitter
    "recursive_512",
    "recursive_1024",
    "recursive_2048",
    "recursive_4096",
    # Token splitter
    "token_512",
    "token_1024",
    "token_2048",
    "token_4096",
]

# ── Available options (returned by GET /api/benchmark/configs) ─────────────────

AVAILABLE_LLMS = [
    {
        "id": "meta-llama/llama-3.1-8b-instruct",
        "label": "LLaMA 3.1 8B",
        "provider": "openrouter",
    },
    {
        "id": "meta-llama/llama-3.3-70b-instruct",
        "label": "LLaMA 3.3 70B",
        "provider": "openrouter",
    },
    {
        "id": "google/gemma-2-9b-it",
        "label": "Gemma 2 9B",
        "provider": "openrouter",
    },
    {
        "id": "openai/gpt-oss-120b",
        "label": "GPT-OSS 120B",
        "provider": "openrouter",
    },
]

AVAILABLE_EMBEDDINGS = [
    {
        "id": "BAAI/bge-small-en-v1.5",
        "label": "BGE Small EN v1.5",
    },
    {
        "id": "sentence-transformers/all-MiniLM-L6-v2",
        "label": "MiniLM L6 v2",
    },
]

AVAILABLE_CHUNKING = [
    # ── Semantic ──────────────────────────────────────────────────────────────
    {
        "id": "semantic_percentile",
        "label": "Semantic — Percentile 95",
        "group": "Semantic",
    },
    # ── Recursive ─────────────────────────────────────────────────────────────
    {
        "id": "recursive_512",
        "label": "Recursive 512 (overlap 50)",
        "group": "Recursive",
        "chunk_size": 512,
        "overlap": 50,
    },
    {
        "id": "recursive_1024",
        "label": "Recursive 1024 (overlap 100)",
        "group": "Recursive",
        "chunk_size": 1024,
        "overlap": 100,
    },
    {
        "id": "recursive_2048",
        "label": "Recursive 2048 (overlap 200)",
        "group": "Recursive",
        "chunk_size": 2048,
        "overlap": 200,
    },
    {
        "id": "recursive_4096",
        "label": "Recursive 4096 (overlap 400)",
        "group": "Recursive",
        "chunk_size": 4096,
        "overlap": 400,
    },
    # ── Token ─────────────────────────────────────────────────────────────────
    {
        "id": "token_512",
        "label": "Token 512 (overlap 50)",
        "group": "Token",
        "chunk_size": 512,
        "overlap": 50,
    },
    {
        "id": "token_1024",
        "label": "Token 1024 (overlap 100)",
        "group": "Token",
        "chunk_size": 1024,
        "overlap": 100,
    },
    {
        "id": "token_2048",
        "label": "Token 2048 (overlap 200)",
        "group": "Token",
        "chunk_size": 2048,
        "overlap": 200,
    },
    {
        "id": "token_4096",
        "label": "Token 4096 (overlap 400)",
        "group": "Token",
        "chunk_size": 4096,
        "overlap": 400,
    },
]

TOP_K_CONFIG = {"min": 1, "max": 20, "default": 4}

# ── Dataclass ──────────────────────────────────────────────────────────────────

@dataclass
class BenchmarkConfig:
    """
    One benchmark run configuration.
    Temperature is intentionally absent — always 0.0 for determinism.
    """
    llm: str                   # OpenRouter model id, e.g. "meta-llama/llama-3.1-8b-instruct"
    embedding_model: str       # HuggingFace model id, e.g. "BAAI/bge-small-en-v1.5"
    chunking_strategy: ChunkingStrategy
    top_k: int = 4

    @property
    def config_id(self) -> str:
        """Short human-readable identifier for this config."""
        llm_short = self.llm.split("/")[-1]          # "llama-3.1-8b-instruct"
        emb_short = "bge" if "bge" in self.embedding_model.lower() else "minilm"
        return f"{llm_short}__{self.chunking_strategy}__{emb_short}__k{self.top_k}"
