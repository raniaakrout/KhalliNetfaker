"""
DeepEval metrics computation for benchmark results.

Metrics:
  - AnswerRelevancy        — is the answer relevant to the question?
  - Faithfulness           — is the answer grounded in retrieved context?
  - ContextualPrecision    — are irrelevant chunks ranked lower?
  - ContextualRecall       — does context cover the ground truth?
  - ContextualRelevancy    — is retrieved context relevant to the question?

Global score = average of all non-None metrics.
"""

from __future__ import annotations

import asyncio
import os
from typing import Optional

from deepeval import evaluate
from deepeval.metrics import (
    AnswerRelevancyMetric,
    FaithfulnessMetric,
    ContextualPrecisionMetric,
    ContextualRecallMetric,
    ContextualRelevancyMetric,
)
from deepeval.test_case import LLMTestCase
from evaluation.eval_config import get_judge_llm


async def compute_metrics(
    question: str,
    answer: str,
    retrieved_chunks: list[str],
    ground_truth: Optional[str],
) -> dict:
    """
    Run DeepEval metrics on a single RAG result.

    Returns a dict with individual metric scores and a global average.
    ContextualRecall is None when ground_truth is not provided.
    """
    # OpenRouter judge LLM configured via JUDGE_MODEL in .env (e.g. openai/gpt-oss-120b)
    judge = get_judge_llm()

    # Build test case
    test_case = LLMTestCase(
        input=question,
        actual_output=answer,
        retrieval_context=retrieved_chunks,
        expected_output=ground_truth,
    )

    # Initialize metrics (threshold=0.0 to always get a score, even if poor)
    metrics = [
        AnswerRelevancyMetric(threshold=0.0, model=judge),
        FaithfulnessMetric(threshold=0.0, model=judge),
        ContextualPrecisionMetric(threshold=0.0, model=judge),
        ContextualRelevancyMetric(threshold=0.0, model=judge),
    ]

    if ground_truth:
        metrics.append(ContextualRecallMetric(threshold=0.0, model=judge))

    # Run evaluation — wrap blocking evaluate() in a thread to avoid blocking the event loop
    try:
        loop = asyncio.get_event_loop()
        evaluation_result = await loop.run_in_executor(
            None,
            lambda: evaluate([test_case], metrics),
        )

        # Extract scores from EvaluationResult.test_results[0].metrics_data
        scores = {}
        if evaluation_result.test_results:
            for meta in evaluation_result.test_results[0].metrics_data:
                scores[meta.name] = meta.score
        # Build response dict
        answer_relevancy = scores.get("Answer Relevancy")
        faithfulness = scores.get("Faithfulness")
        contextual_precision = scores.get("Contextual Precision")
        contextual_recall = scores.get("Contextual Recall")
        contextual_relevancy = scores.get("Contextual Relevancy")

        # Global score = average of non-None metrics
        non_none = [
            s for s in [
                answer_relevancy,
                faithfulness,
                contextual_precision,
                contextual_recall,
                contextual_relevancy,
            ] if s is not None
        ]
        score_global = sum(non_none) / len(non_none) if non_none else None

        return {
            "answer_relevancy": answer_relevancy,
            "faithfulness": faithfulness,
            "contextual_precision": contextual_precision,
            "contextual_recall": contextual_recall,
            "contextual_relevancy": contextual_relevancy,
            "score_global": score_global,
        }

    except Exception as e:  # noqa: BLE001
        import traceback
        traceback.print_exc()   # ← affiche l'erreur réelle dans les logs
        # If DeepEval fails, return None scores
        return {
            "answer_relevancy": None,
            "faithfulness": None,
            "contextual_precision": None,
            "contextual_recall": None,
            "contextual_relevancy": None,
            "score_global": None,
        }
