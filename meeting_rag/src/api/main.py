import sys
import uuid as uuid_mod
import asyncio
from typing import Any
from pathlib import Path
from dotenv import load_dotenv

# Load env variables first before any other local imports
src_dir = Path(__file__).resolve().parent.parent
env_path = src_dir / ".env"
load_dotenv(dotenv_path=env_path)
load_dotenv()  # also load from CWD just in case

# Add project root to sys.path so 'database' package is findable
root_dir = src_dir.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from fastapi import FastAPI, File, HTTPException, UploadFile, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session

from agent import create_chat_agent
from schemas import MeetingMinutes, SummaryEvalRequest, RagEvalRequest, EvalResult
from services.transcript_service import process_upload
from database.db import get_db
from database.models import User, Transcript
from database.crud import create_chat_message, get_meeting_minutes, get_user_transcripts
from utils.security import get_current_user
from api.auth import router as auth_router
from api.benchmark import router as benchmark_router

app = FastAPI(title="Meeting Transcript API", version="0.1.0")
app.include_router(auth_router)
app.include_router(benchmark_router)
app.add_middleware(
    CORSMiddleware,
    # Explicit origin required when allow_credentials=True (browsers reject "*" with credentials)
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,  # Allows httpOnly cookies to be sent cross-origin
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Schemas ───────────────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str
    transcript_id: str | None = None
    thread_id: str | None = None  # null = premier message → le backend génère un thread_id


class ChatResponse(BaseModel):
    answer: str
    thread_id: str  # toujours renvoyé pour que le frontend le conserve
    chunk_ids: list[str] = []


class UploadResponse(BaseModel):
    transcript_id: str
    filename: str
    minutes: MeetingMinutes


class ChatMessageItem(BaseModel):
    id: str
    role: str
    content: str
    timestamp: str
    chunk_ids: list[str] = []


class ConversationItem(BaseModel):
    id: str
    user_id: str
    transcript_id: str | None = None
    title: str
    subtitle: str
    messages: list[ChatMessageItem]
    created_at: str


import datetime

class TranscriptListItem(BaseModel):
    transcript_id: uuid_mod.UUID
    filename: str
    status: str
    created_at: datetime.datetime

    class Config:
        from_attributes = True


# ── Routes ────────────────────────────────────────────────────────────────────


import json as _json
import queue as _queue
from fastapi.responses import StreamingResponse


@app.post("/api/transcripts")
async def upload_transcript(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Upload a transcript and stream processing progress as SSE events.

    Event types sent to the client:
    - `data: {"type": "log",  "message": "..."}\\n\\n`   — progress update
    - `data: {"type": "done", "data": {...}}\\n\\n`       — success with UploadResponse payload
    - `data: {"type": "error","message": "..."}\\n\\n`    — failure
    """
    # ── Filename validation ────────────────────────────────────────────────────
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required.")

    allowed_extensions = {".txt", ".vtt"}
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{file_ext}'. Allowed: {', '.join(allowed_extensions)}.",
        )

    # ── Read & size validation ─────────────────────────────────────────────────
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Empty file.")
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large ({len(content) // (1024*1024)} MB). Maximum allowed size is 10 MB.",
        )

    filename = file.filename
    user_id  = str(current_user.user_id)

    # ── SSE streaming generator ────────────────────────────────────────────────
    # A thread-safe queue bridges the sync worker thread → async generator.
    log_queue: asyncio.Queue[str | None] = asyncio.Queue()
    loop = asyncio.get_event_loop()

    def emit(message: str) -> None:
        """Called from the worker thread — puts an SSE log event into the queue."""
        event = _json.dumps({"type": "log", "message": message})
        loop.call_soon_threadsafe(log_queue.put_nowait, f"data: {event}\n\n")

    async def run_processing() -> None:
        """Runs process_upload in a thread, then signals done/error into the queue."""
        try:
            transcript_id, minutes = await asyncio.to_thread(
                process_upload, content, filename, user_id, db, emit
            )
            payload = _json.dumps({
                "type": "done",
                "data": {
                    "transcript_id": transcript_id,
                    "filename": filename,
                    "minutes": minutes.model_dump(),
                },
            })
            await log_queue.put(f"data: {payload}\n\n")
        except Exception as exc:
            error_event = _json.dumps({"type": "error", "message": str(exc)})
            await log_queue.put(f"data: {error_event}\n\n")
        finally:
            await log_queue.put(None)  # sentinel → stop the generator

    async def event_stream():
        # Start processing in background
        task = asyncio.create_task(run_processing())
        try:
            while True:
                item = await log_queue.get()
                if item is None:
                    break
                yield item
        finally:
            task.cancel()

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        },
    )


@app.get("/api/transcripts", response_model=list[TranscriptListItem])
async def list_transcripts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_user_transcripts(db, current_user.user_id)


@app.get("/api/chats", response_model=list[ConversationItem])
async def list_chats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve all conversation threads and messages for the current user from PostgreSQL.
    """
    from database.models import ChatHistory, Transcript
    user_id = current_user.user_id

    records = (
        db.query(ChatHistory)
        .filter(ChatHistory.user_id == user_id)
        .order_by(ChatHistory.created_at.asc())
        .all()
    )

    conversations_map: dict[str, list[ChatHistory]] = {}
    for r in records:
        key = str(r.transcript_id) if r.transcript_id else "general"
        if key not in conversations_map:
            conversations_map[key] = []
        conversations_map[key].append(r)

    t_ids = [r.transcript_id for r in records if r.transcript_id]
    filenames: dict[str, str] = {}
    if t_ids:
        transcripts = db.query(Transcript).filter(Transcript.transcript_id.in_(t_ids)).all()
        for t in transcripts:
            filenames[str(t.transcript_id)] = t.filename

    conversations: list[ConversationItem] = []
    for key, msgs in conversations_map.items():
        if not msgs:
            continue
        first_msg = msgs[0]
        t_id_str = str(first_msg.transcript_id) if first_msg.transcript_id else None
        filename = filenames.get(t_id_str, "New Conversation") if t_id_str else "General Conversation"

        title = filename if t_id_str else (msgs[0].message[:30] + "..." if len(msgs[0].message) > 30 else msgs[0].message)
        subtitle = f"Transcript: {filename}" if t_id_str else "General conversation"

        formatted_msgs = [
            ChatMessageItem(
                id=str(m.id),
                role=m.role or "assistant",
                content=m.message or "",
                timestamp=m.created_at.isoformat() if m.created_at else "",
                chunk_ids=[],
            )
            for m in msgs
        ]

        conversations.append(
            ConversationItem(
                id=f"chat_{key}",
                user_id=str(user_id),
                transcript_id=t_id_str,
                title=title,
                subtitle=subtitle,
                messages=formatted_msgs,
                created_at=first_msg.created_at.isoformat() if first_msg.created_at else "",
            )
        )

    conversations.reverse()
    return conversations


@app.post("/api/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user_id = str(current_user.user_id)
    transcript_id = request.transcript_id or None

    # thread_id null = premier message de cette conversation → on le crée
    thread_id = request.thread_id if request.thread_id else str(uuid_mod.uuid4())

    # Identifiant de session isolé par utilisateur (évite les collisions entre users)
    scoped_thread_id = f"{user_id}_{thread_id}"

    # Sauvegarde du message utilisateur
    create_chat_message(
        db=db,
        user_id=user_id,
        transcript_id=transcript_id,
        role="user",
        message=request.message,
    )

    # Routing : agent RAG si transcript chargé, sinon LLM direct
    upload_path = Path("data/uploads") / f"{transcript_id}.txt" if transcript_id else None
    agent = create_chat_agent(request.transcript_id)

    config = {
    "configurable": {
        "thread_id": scoped_thread_id,
    }
}

    result: Any = await asyncio.to_thread(
           agent.invoke,
        {
        "messages": [
            {
                "role": "user",
                "content": request.message,
            }
        ]
    },
    config,
)

    answer = result["messages"][-1].content
    
    import re
    chunk_ids_set = set()
    filename = "Unknown Transcript"
    if transcript_id:
        transcript = db.query(Transcript).filter(Transcript.transcript_id == transcript_id).first()
        if transcript:
            filename = transcript.filename

    for msg in result.get("messages", []):
        if getattr(msg, "type", "") == "tool" or getattr(msg, "name", "") == "search_meeting":
            matches = re.findall(r"\[Chunk\s+([A-Za-z0-9_-]+)\]", getattr(msg, "content", ""))
            for m in matches:
                chunk_ids_set.add(f"{filename} (Chunk {m})")

    # Sauvegarde de la réponse de l'assistant
    create_chat_message(
        db=db,
        user_id=user_id,
        transcript_id=transcript_id,
        role="assistant",
        message=answer,
    )

    return ChatResponse(answer=answer, thread_id=thread_id, chunk_ids=list(chunk_ids_set))


@app.get("/api/transcripts/{transcript_id}/minutes", response_model=MeetingMinutes)
async def get_minutes(
    transcript_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        t_uuid = uuid_mod.UUID(transcript_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid transcript ID format")

    minutes = get_meeting_minutes(db, t_uuid)
    if not minutes:
        raise HTTPException(status_code=404, detail="Meeting minutes not found")
    return minutes


@app.post("/api/evaluate/summary", response_model=EvalResult)
async def evaluate_summary_endpoint(
    request: SummaryEvalRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Evaluate an existing meeting summary using SummarizationMetric and HallucinationMetric.

    Requires transcript_id. Loads the minutes from DB and the transcript from disk.
    """
    try:
        t_uuid = uuid_mod.UUID(request.transcript_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid transcript ID format")

    minutes = get_meeting_minutes(db, t_uuid)
    if not minutes:
        raise HTTPException(status_code=404, detail="Meeting minutes not found")

    from evaluation.summarization_eval import evaluate_summary

    result = await asyncio.to_thread(
        evaluate_summary,
        request.transcript_id,
        minutes,
        request.reference_summary,
    )
    return result


@app.post("/api/evaluate/rag", response_model=EvalResult)
async def evaluate_rag_endpoint(
    request: RagEvalRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Evaluate a RAG response using FaithfulnessMetric, AnswerRelevancyMetric,
    and optionally ContextualPrecisionMetric (if expected_answer is provided).

    The frontend should send the question, answer, and retrieved_chunks.
    """
    from evaluation.rag_eval import evaluate_rag_response

    result = await asyncio.to_thread(
        evaluate_rag_response,
        request.question,
        request.answer,
        request.retrieved_chunks,
        request.transcript_id,
        request.expected_answer,
    )
    return result


@app.get("/api/health")
async def health():
    return {"status": "ok"}
