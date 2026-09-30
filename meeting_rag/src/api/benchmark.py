"""
FastAPI router for benchmark endpoints.

Routes:
  GET  /api/benchmark/configs  — available LLMs, embeddings, chunking strategies
  POST /api/benchmark/run      — run N configs and return scored results

The existing chat pipeline (main.py, agent.py, rag/) is never touched here.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from benchmark.config import (
    AVAILABLE_CHUNKING,
    AVAILABLE_EMBEDDINGS,
    AVAILABLE_LLMS,
    TOP_K_CONFIG,
    BenchmarkConfig,
)

router = APIRouter(prefix="/api/benchmark", tags=["benchmark"])


# ── Request / Response schemas ─────────────────────────────────────────────────

class BenchmarkRunConfig(BaseModel):
    """Single configuration to benchmark."""
    llm: str
    embedding_model: str
    chunking_strategy: str
    top_k: int = Field(default=4, ge=1, le=20)


class BenchmarkRequest(BaseModel):
    transcript_id: str
    question: str
    ground_truth: str | None = None          # optional — enables ContextualRecall
    configs: list[BenchmarkRunConfig] = Field(..., min_length=1)


class BenchmarkMetrics(BaseModel):
    answer_relevancy: float | None = None
    faithfulness: float | None = None
    contextual_precision: float | None = None
    contextual_recall: float | None = None   # None when no ground_truth provided
    contextual_relevancy: float | None = None
    score_global: float | None = None


class BenchmarkResult(BaseModel):
    config_id: str
    llm: str
    embedding_model: str
    chunking_strategy: str
    top_k: int
    answer: str
    retrieved_chunks: list[str]
    latency_ms: int
    metrics: BenchmarkMetrics
    error: str | None = None                 # set if this config failed


class BenchmarkResponse(BaseModel):
    run_id: str
    transcript_id: str
    question: str
    results: list[BenchmarkResult]
    best_config: str | None = None           # config_id with highest score_global
    duration_total_ms: int


# ── Endpoints ──────────────────────────────────────────────────────────────────

@router.get("/configs")
async def get_benchmark_configs():
    """Return all available options for the benchmark modal."""
    return {
        "llms": AVAILABLE_LLMS,
        "embedding_models": AVAILABLE_EMBEDDINGS,
        "chunking_strategies": AVAILABLE_CHUNKING,
        "top_k": TOP_K_CONFIG,
    }


@router.post("/run", response_model=BenchmarkResponse)
async def run_benchmark(request: BenchmarkRequest):
    """
    Run the benchmark for every requested config and return scored results.

    Each config is executed sequentially to avoid exceeding OpenRouter's
    in-flight request budget. Results are sorted by global score descending.
    The chat pipeline and its vector stores are never modified.
    """
    import time
    import uuid
    from pathlib import Path
    from benchmark.runner import run_single_config

    # ── Resolve transcript file path ───────────────────────────────────────────
    transcript_path = Path("data/uploads") / f"{request.transcript_id}.txt"
    if not transcript_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Transcript file not found for id '{request.transcript_id}'.",
        )

    run_id = f"bench_{uuid.uuid4().hex[:12]}"
    t_start = time.monotonic()

    # ── Build typed config objects ─────────────────────────────────────────────
    configs = [
        BenchmarkConfig(
            llm=c.llm,
            embedding_model=c.embedding_model,
            chunking_strategy=c.chunking_strategy,  # type: ignore[arg-type]
            top_k=c.top_k,
        )
        for c in request.configs
    ]

    # ── Run configs sequentially — avoids OpenRouter 402 in-flight budget errors ──
    raw_dicts: list[dict] = []
    for cfg in configs:
        result = await run_single_config(
            transcript_path=str(transcript_path),
            question=request.question,
            ground_truth=request.ground_truth,
            config=cfg,
        )
        raw_dicts.append(result)

    # ── Convert dicts → typed Pydantic objects ─────────────────────────────────
    raw_results: list[BenchmarkResult] = [
        BenchmarkResult(
            config_id=d["config_id"],
            llm=d["llm"],
            embedding_model=d["embedding_model"],
            chunking_strategy=d["chunking_strategy"],
            top_k=d["top_k"],
            answer=d["answer"],
            retrieved_chunks=d["retrieved_chunks"],
            latency_ms=d["latency_ms"],
            metrics=BenchmarkMetrics(**(d["metrics"] if isinstance(d["metrics"], dict) else d["metrics"].model_dump())),
            error=d.get("error"),
        )
        for d in raw_dicts
    ]

    # ── Sort by score_global descending; errors go to the bottom ───────────────
    def _sort_key(r: BenchmarkResult) -> float:
        if r.metrics.score_global is None:
            return -1.0
        return r.metrics.score_global

    sorted_results = sorted(raw_results, key=_sort_key, reverse=True)

    best_config = None
    if sorted_results and sorted_results[0].metrics.score_global is not None:
        best_config = sorted_results[0].config_id

    duration_ms = int((time.monotonic() - t_start) * 1000)

    return BenchmarkResponse(
        run_id=run_id,
        transcript_id=request.transcript_id,
        question=request.question,
        results=sorted_results,
        best_config=best_config,
        duration_total_ms=duration_ms,
    )
