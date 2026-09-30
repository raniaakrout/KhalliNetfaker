from pathlib import Path
from datetime import datetime, timezone

from deepeval.metrics import GEval, HallucinationMetric
from deepeval.test_case import LLMTestCase, LLMTestCaseParams

from schemas import MeetingMinutes
from evaluation.eval_config import (
    get_judge_llm,
    JUDGE_THRESHOLD_SUMMARY,
    JUDGE_THRESHOLD_HALLUCINATION,
)
from rag.retriever import retrieve_documents

UPLOAD_DIR = Path("data/uploads")
VECTORSTORE_DIR = Path("vectorstore")


def _load_transcript(transcript_id: str) -> str:
    path = UPLOAD_DIR / f"{transcript_id}.txt"
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def _get_supporting_chunks(
    query: str,
    transcript_id: str,
    transcript_text: str,
    k: int = 3,
) -> list[str]:
    """
    Retrieve top-k relevant chunks from FAISS vectorstore for a given query.
    Falls back gracefully to transcript slices if index is missing.
    """
    index_dir = VECTORSTORE_DIR / transcript_id
    if index_dir.exists():
        try:
            docs = retrieve_documents(query, str(index_dir), k=k)
            chunks = [d.page_content.strip() for d in docs if d.page_content and d.page_content.strip()]
            if chunks:
                return chunks
        except Exception:
            pass

    # Fallback: slice transcript text if vectorstore is not available
    if transcript_text:
        return [transcript_text[:3000]]
    return ["No context available."]


def _action_items_to_text(minutes: MeetingMinutes) -> str:
    lines = []
    for item in minutes.action_items:
        parts = [f"Task: {item.task}"]
        if item.owner:
            parts.append(f"Owner: {item.owner}")
        if item.deadline:
            parts.append(f"Deadline: {item.deadline}")
        lines.append(" | ".join(parts))
    return "\n".join(lines) if lines else "No action items."


def evaluate_summary_from_text(
    transcript_text: str,
    minutes: MeetingMinutes,
    transcript_id: str = "test",
    reference_summary: str | None = None,
) -> dict:
    """
    Evaluates summary quality against reference summary (or intrinsic quality if omitted),
    and evaluates hallucination for decisions and action items grounded on retrieved chunks.
    """
    judge = get_judge_llm()
    results = []

    # ── 1. Summary Evaluation (Reference-grounded or Intrinsic Quality) ────────
    if reference_summary and reference_summary.strip():
        summary_metric = GEval(
            name="Summary Alignment",
            criteria=(
                "Evaluate whether the actual summary accurately and faithfully reflects the key topics, "
                "decisions, and outcomes described in the reference summary without omitting essential points "
                "or fabricating false information."
            ),
            evaluation_params=[LLMTestCaseParams.ACTUAL_OUTPUT, LLMTestCaseParams.EXPECTED_OUTPUT],
            model=judge,
            threshold=JUDGE_THRESHOLD_SUMMARY,
            async_mode=False,
        )
        summary_case = LLMTestCase(
            input="Summarize the meeting key discussions and outcomes.",
            actual_output=minutes.summary,
            expected_output=reference_summary.strip(),
        )
    else:
        summary_metric = GEval(
            name="Summary Quality",
            criteria=(
                "Evaluate whether the meeting summary is well-structured, clear, concise, professional, "
                "and effectively captures high-level executive discussion points and conclusions."
            ),
            evaluation_params=[LLMTestCaseParams.ACTUAL_OUTPUT],
            model=judge,
            threshold=JUDGE_THRESHOLD_SUMMARY,
            async_mode=False,
        )
        summary_case = LLMTestCase(
            input="Summarize the meeting key discussions and outcomes.",
            actual_output=minutes.summary,
        )

    summary_metric.measure(summary_case)
    results.append({
        "name": "summarization",
        "score": summary_metric.score,
        "reason": summary_metric.reason,
        "threshold": JUDGE_THRESHOLD_SUMMARY,
        "passed": summary_metric.is_successful(),
    })

    # ── 2. HallucinationMetric on key_decisions using vectorstore retrieval ────
    if minutes.key_decisions:
        decisions_text = "\n".join(f"- {d}" for d in minutes.key_decisions)
        
        # Retrieve supporting chunks for each decision
        retrieved_contexts: list[str] = []
        for decision in minutes.key_decisions:
            chunks = _get_supporting_chunks(decision, transcript_id, transcript_text, k=2)
            retrieved_contexts.extend(chunks)

        unique_contexts = list(dict.fromkeys(retrieved_contexts)) or [transcript_text[:3000] if transcript_text else "No context"]

        hallucination_decisions = HallucinationMetric(
            threshold=JUDGE_THRESHOLD_HALLUCINATION,
            model=judge,
            async_mode=False,
        )
        decisions_case = LLMTestCase(
            input="What key decisions were agreed upon during the meeting?",
            actual_output=decisions_text,
            context=unique_contexts,
        )
        hallucination_decisions.measure(decisions_case)
        results.append({
            "name": "hallucination_key_decisions",
            "score": hallucination_decisions.score,
            "reason": hallucination_decisions.reason,
            "threshold": JUDGE_THRESHOLD_HALLUCINATION,
            "passed": hallucination_decisions.is_successful(),
        })

    # ── 3. HallucinationMetric on action_items using vectorstore retrieval ─────
    if minutes.action_items:
        action_text = _action_items_to_text(minutes)
        
        # Retrieve supporting chunks for each action item
        retrieved_contexts = []
        for item in minutes.action_items:
            query = f"Task: {item.task} Assignee: {item.owner or ''}"
            chunks = _get_supporting_chunks(query, transcript_id, transcript_text, k=2)
            retrieved_contexts.extend(chunks)

        unique_contexts = list(dict.fromkeys(retrieved_contexts)) or [transcript_text[:3000] if transcript_text else "No context"]

        hallucination_actions = HallucinationMetric(
            threshold=JUDGE_THRESHOLD_HALLUCINATION,
            model=judge,
            async_mode=False,
        )
        actions_case = LLMTestCase(
            input="What action items, assignees, and tasks were assigned in the meeting?",
            actual_output=action_text,
            context=unique_contexts,
        )
        hallucination_actions.measure(actions_case)
        results.append({
            "name": "hallucination_action_items",
            "score": hallucination_actions.score,
            "reason": hallucination_actions.reason,
            "threshold": JUDGE_THRESHOLD_HALLUCINATION,
            "passed": hallucination_actions.is_successful(),
        })

    return {
        "transcript_id": transcript_id,
        "pipeline": "summarization",
        "metrics": results,
        "evaluated_at": datetime.now(timezone.utc).isoformat(),
    }


def evaluate_summary(
    transcript_id: str,
    minutes: MeetingMinutes,
    reference_summary: str | None = None,
) -> dict:
    """
    Loads transcript if available and evaluates summary, decisions, and action items.
    """
    transcript_text = _load_transcript(transcript_id)
    return evaluate_summary_from_text(
        transcript_text=transcript_text,
        minutes=minutes,
        transcript_id=transcript_id,
        reference_summary=reference_summary,
    )
