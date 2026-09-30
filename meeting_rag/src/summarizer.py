"""
Summarizer pipeline
Hierarchical merge
     We now merge in batches of BATCH_SIZE, then merge the intermediates.

"""

import json
from typing import List, cast, Callable

from langchain_core.documents import Document
from langchain_core.messages import HumanMessage, SystemMessage

import os
from loader import load_transcript
from chunker import split_for_summary
from schemas import MeetingChunkSummary, MeetingMinutes
from llm_utils import get_llm
from prompts.summary_prompt import SUMMARY_SYSTEM_PROMPT
from prompts.merge_prompt import MERGE_SYSTEM_PROMPT

# Maximum number of chunk summaries sent to the merge agent in one call
MERGE_BATCH_SIZE = 6

_noop: Callable[[str], None] = lambda _msg: None


class Summarizer:
    """
    End-to-end pipeline:
    Transcript → Chunking (Token/Recursive/Semantic) → Chunk Summaries → Hierarchical Merge → MeetingMinutes
    Accepts an optional `emit` callback to report progress to the caller.
    """

    def __init__(
        self,
        chunking_strategy: str | None = None,
        chunk_size: int | None = None,
        chunk_overlap: int | None = None,
    ):
        llm = get_llm()
      
        self.chunk_llm = llm.with_structured_output(MeetingChunkSummary)
        self.merge_llm = llm.with_structured_output(MeetingMinutes)

        self.chunking_strategy = chunking_strategy or os.getenv("SUMMARY_CHUNKING_STRATEGY", "token")
        self.chunk_size = chunk_size or int(os.getenv("SUMMARY_CHUNK_SIZE", "1024"))
        self.chunk_overlap = chunk_overlap or int(os.getenv("SUMMARY_CHUNK_OVERLAP", "100"))

    # ------------------------------------------------------------------
    # Step 1 — Chunking
    # ------------------------------------------------------------------

    def chunk_transcript(
        self, file_path: str, emit: Callable[[str], None] = _noop
    ) -> List[Document]:
        doc = load_transcript(file_path)
        emit(f"Running summary chunking ({self.chunking_strategy} — size: {self.chunk_size}, overlap: {self.chunk_overlap})…")
        chunks = split_for_summary(
            doc,
            strategy=self.chunking_strategy,
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
        )
        msg = f"Summary chunking ({self.chunking_strategy}) produced {len(chunks)} chunk(s)"
        print(f"[INFO] {msg}")
        emit(msg)
        return chunks

    # ------------------------------------------------------------------
    # Step 2 — Map: summarize each chunk individually
    # ------------------------------------------------------------------

    def summarize_chunks(
        self, chunks: List[Document], emit: Callable[[str], None] = _noop
    ) -> List[MeetingChunkSummary]:
        results = []
        total = len(chunks)
        for i, chunk in enumerate(chunks):
            msg = f"Summarizing chunk {i + 1}/{total}"
            print(f"[INFO] {msg}")
            emit(msg)
            messages = [
                SystemMessage(content=SUMMARY_SYSTEM_PROMPT),
                HumanMessage(content=f"[Chunk {i + 1} of {total}]\n\n{chunk.page_content}"),
            ]
            summary = cast(MeetingChunkSummary, self.chunk_llm.invoke(messages))
            results.append(summary)
        return results

    # ------------------------------------------------------------------
    # Step 3 — Reduce: hierarchical merge
    # ------------------------------------------------------------------

    def _merge_batch(
        self,
        summaries: List[MeetingChunkSummary],
        label: str = "",
        emit: Callable[[str], None] = _noop,
    ) -> MeetingMinutes:
        payload = json.dumps([s.model_dump() for s in summaries], ensure_ascii=False, indent=2)
        messages = [
            SystemMessage(content=MERGE_SYSTEM_PROMPT),
            HumanMessage(content=(
                "Here are the structured summaries of all meeting segments. "
                "Synthesize them into the final meeting minutes. "
                f"Use only the information present in these summaries.\n\n{payload}"
            )),
        ]
        msg = f"Merging batch {label} ({len(summaries)} summaries)"
        print(f"[INFO] {msg}")
        emit(msg)
        minutes = cast(MeetingMinutes, self.merge_llm.invoke(messages))
        return minutes

    def _minutes_to_chunk_summary(self, minutes: MeetingMinutes) -> MeetingChunkSummary:
        return MeetingChunkSummary(
            summary=minutes.summary,
            key_decisions=minutes.key_decisions,
            action_items=minutes.action_items,
            sentiment=minutes.sentiment,
        )

    def merge_summaries(
        self,
        summaries: List[MeetingChunkSummary],
        emit: Callable[[str], None] = _noop,
    ) -> MeetingMinutes:
        """
        Hierarchical merge — processes in batches of MERGE_BATCH_SIZE to
        stay within context limits regardless of transcript length.
        """
        current: List[MeetingChunkSummary] = summaries
        level = 0

        while len(current) > MERGE_BATCH_SIZE:
            level += 1
            next_level: List[MeetingChunkSummary] = []
            batches = [current[i: i + MERGE_BATCH_SIZE] for i in range(0, len(current), MERGE_BATCH_SIZE)]
            msg = f"Merge level {level}: {len(current)} → {len(batches)} batch(es)"
            print(f"[INFO] {msg}")
            emit(msg)
            for b_idx, batch in enumerate(batches):
                merged = self._merge_batch(
                    batch,
                    label=f"L{level}-{b_idx + 1}/{len(batches)}",
                    emit=emit,
                )
                next_level.append(self._minutes_to_chunk_summary(merged))
            current = next_level

        return self._merge_batch(current, label="final", emit=emit)

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------

    def run(
        self,
        file_path: str,
        transcript_id: str | None = None,
        emit: Callable[[str], None] = _noop,
    ) -> MeetingMinutes:
        chunks = self.chunk_transcript(file_path, emit=emit)
        summaries = self.summarize_chunks(chunks, emit=emit)

        if transcript_id:
            from pathlib import Path
            import json
            summary_chunks_dir = Path("data/chunks/summary")
            summary_chunks_dir.mkdir(parents=True, exist_ok=True)
            summary_file = summary_chunks_dir / f"{transcript_id}.json"

            payload = [s.model_dump() for s in summaries]
            with open(summary_file, "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False, indent=2)

            msg = f"Summary chunks saved to {summary_file}"
            print(f"[INFO] {msg}")
            emit(msg)

        final_minutes = self.merge_summaries(summaries, emit=emit)
        return final_minutes


if __name__ == "__main__":
    summarizer = Summarizer()
    result = summarizer.run("data/2022_Q4_dbk_processed.txt")
    print("\n" + "=" * 60)
    print(result.model_dump_json(indent=2))