from datetime import datetime, timezone

from deepeval.metrics import (
    FaithfulnessMetric,
    AnswerRelevancyMetric,
    ContextualPrecisionMetric,
)
from deepeval.test_case import LLMTestCase

from evaluation.eval_config import (
    get_judge_llm,
    JUDGE_THRESHOLD_FAITHFULNESS,
    JUDGE_THRESHOLD_RELEVANCY,
    JUDGE_THRESHOLD_PRECISION,
)


def evaluate_rag_response(
    question: str,
    answer: str,
    retrieved_chunks: list[str],
    transcript_id: str,
    expected_answer: str | None = None,
) -> dict:
    """
    Runs three RAG metrics on one (question, answer, chunks) triple:
      - FaithfulnessMetric      : claims in answer supported by chunks
      - AnswerRelevancyMetric   : answer stays on topic vs the question
      - ContextualPrecisionMetric : relevant chunks ranked first (needs expected_answer)

    retrieved_chunks: plain text content of each chunk (not IDs).
    expected_answer : required for ContextualPrecision; skipped when None.
    """
    judge = get_judge_llm()
    results = []

    base_case = LLMTestCase(
        input=question,
        actual_output=answer,
        retrieval_context=retrieved_chunks,
    )

    # ── 1. FaithfulnessMetric ──────────────────────────────────────────────────
    faithfulness = FaithfulnessMetric(
        threshold=JUDGE_THRESHOLD_FAITHFULNESS,
        model=judge,
        async_mode=False,
    )
    faithfulness.measure(base_case)
    results.append({
        "name": "faithfulness",
        "score": faithfulness.score,
        "reason": faithfulness.reason,
        "threshold": JUDGE_THRESHOLD_FAITHFULNESS,
        "passed": faithfulness.is_successful(),
    })

    # ── 2. AnswerRelevancyMetric ───────────────────────────────────────────────
    relevancy = AnswerRelevancyMetric(
        threshold=JUDGE_THRESHOLD_RELEVANCY,
        model=judge,
        async_mode=False,
    )
    relevancy.measure(base_case)
    results.append({
        "name": "answer_relevancy",
        "score": relevancy.score,
        "reason": relevancy.reason,
        "threshold": JUDGE_THRESHOLD_RELEVANCY,
        "passed": relevancy.is_successful(),
    })

    # ── 3. ContextualPrecisionMetric (only when ground truth is available) ─────
    if expected_answer:
        precision_case = LLMTestCase(
            input=question,
            actual_output=answer,
            expected_output=expected_answer,
            retrieval_context=retrieved_chunks,
        )
        precision = ContextualPrecisionMetric(
            threshold=JUDGE_THRESHOLD_PRECISION,
            model=judge,
            async_mode=False,
        )
        precision.measure(precision_case)
        results.append({
            "name": "contextual_precision",
            "score": precision.score,
            "reason": precision.reason,
            "threshold": JUDGE_THRESHOLD_PRECISION,
            "passed": precision.is_successful(),
        })

    return {
        "transcript_id": transcript_id,
        "pipeline": "rag",
        "metrics": results,
        "evaluated_at": datetime.now(timezone.utc).isoformat(),
    }
