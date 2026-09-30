"""
Upload pipeline with progress callbacks.

Each step calls `emit(message)` to push a progress log to the SSE stream.
emit is a simple callable injected from the endpoint.
"""

from pathlib import Path
from typing import Callable
import hashlib
import uuid

from sqlalchemy.orm import Session

from rag.indexer import Indexer
from schemas import MeetingMinutes
from summarizer import Summarizer

from database.crud import (
    get_transcript_by_hash,
    create_transcript,
    create_meeting_minutes,
    get_meeting_minutes,
    update_transcript,
    update_transcript_status,
)

UPLOAD_DIR = Path("data/uploads")
VECTORSTORE_DIR = Path("vectorstore")

# A no-op emit used when no progress callback is provided (backward compat)
_noop: Callable[[str], None] = lambda _msg: None


def compute_hash(file_bytes: bytes) -> str:
    return hashlib.sha256(file_bytes).hexdigest()


def process_upload(
    file_bytes: bytes,
    filename: str,
    user_id: str,
    db: Session,
    emit: Callable[[str], None] = _noop,
) -> tuple[str, MeetingMinutes]:

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    # ── Hash & dedup ───────────────────────────────────────────────────────────
    emit("Computing file hash…")
    file_hash = compute_hash(file_bytes)

    existing = get_transcript_by_hash(db=db, user_id=user_id, file_hash=file_hash)
    if existing:
        minutes = get_meeting_minutes(db, existing.transcript_id)
        if minutes is not None:
            emit("Duplicate detected — returning cached result.")
            return str(existing.transcript_id), minutes
        transcript = existing
    else:
        transcript = create_transcript(
            db=db,
            user_id=user_id,
            filename=filename,
            file_hash=file_hash,
        )

    transcript_id = str(transcript.transcript_id)
    file_path = UPLOAD_DIR / f"{transcript_id}.txt"
    index_dir = str(VECTORSTORE_DIR / transcript_id)

    try:
        # ── Save file ──────────────────────────────────────────────────────────
        emit(f"Saving file: {filename}")
        file_path.write_bytes(file_bytes)

        # ── Build vector index ─────────────────────────────────────────────────
        emit("Building vector index…")
        Indexer(index_dir=index_dir).build(str(file_path), emit=emit)

        # ── Summarize ──────────────────────────────────────────────────────────
        emit("Starting summarization pipeline…")
        minutes = Summarizer().run(str(file_path), transcript_id=transcript_id, emit=emit)

        # ── Persist ───────────────────────────────────────────────────────────
        emit("Saving meeting minutes to database…")
        create_meeting_minutes(
            db=db,
            transcript_id=transcript.transcript_id,
            minutes=minutes,
        )

        update_transcript(
            db=db,
            transcript_id=transcript.transcript_id,
            file_path=str(file_path),
            vectorstore_path=index_dir,
        )

        emit("✅ Processing complete!")
        return transcript_id, minutes

    except Exception:
        update_transcript_status(
            db=db,
            transcript_id=transcript.transcript_id,
            status="failed",
        )
        raise