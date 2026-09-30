from sqlalchemy.orm import Session

from database.models import User, Transcript
from database.models import MeetingMinutes as DBMeetingMinutes
import uuid
from schemas import MeetingMinutes as SchemaMeetingMinutes

# ---------- USER ----------

def create_user(
    db: Session,
    username: str,
    email: str,
    password_hash: str
):

    user = User(
        username=username,
        email=email,
        password_hash=password_hash
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user



def get_user_by_email(
    db: Session,
    email: str
):

    return (
        db.query(User)
        .filter(User.email == email)
        .first()
    )


def get_user_by_id(
    db: Session,
    user_id: str,
):
    """Look up a user by their UUID (used by JWT auth)."""
    try:
        u_id = uuid.UUID(user_id)
    except ValueError:
        return None
    return (
        db.query(User)
        .filter(User.user_id == u_id)
        .first()
    )


# ---------- TRANSCRIPT ----------


def create_transcript(
    db,
    user_id,
    filename,
    file_hash,
):
    u_id = uuid.UUID(str(user_id)) if isinstance(user_id, (str, uuid.UUID)) else user_id
    transcript = Transcript(
        user_id=u_id,
        filename=filename,
        file_hash=file_hash,
        status="processing",
    )

    db.add(transcript)
    db.commit()
    db.refresh(transcript)

    return transcript



def get_transcript_by_hash(
    db: Session,
    user_id,
    file_hash
):
    u_id = uuid.UUID(str(user_id)) if isinstance(user_id, (str, uuid.UUID)) else user_id
    return (
        db.query(Transcript)
        .filter(
            Transcript.user_id == u_id,
            Transcript.file_hash == file_hash
        )
        .first()
    )


def get_user_transcripts(
    db: Session,
    user_id
):
    u_id = uuid.UUID(str(user_id)) if isinstance(user_id, (str, uuid.UUID)) else user_id
    return (
        db.query(Transcript)
        .filter(Transcript.user_id == u_id)
        .order_by(Transcript.created_at.desc())
        .all()
    )





 


def create_meeting_minutes(
    db: Session,
    transcript_id,
    minutes: SchemaMeetingMinutes,
):

    meeting_minutes = DBMeetingMinutes(
        transcript_id=transcript_id,
        summary=minutes.summary,
        key_decisions=minutes.key_decisions,
        action_items=[item.model_dump() for item in minutes.action_items],
        sentiment=minutes.sentiment,
    )

    db.add(meeting_minutes)
    db.commit()
    db.refresh(meeting_minutes)

    return meeting_minutes






def get_meeting_minutes(
    db: Session,
    transcript_id,
) -> SchemaMeetingMinutes | None:

    minutes = (
        db.query(DBMeetingMinutes)
        .filter(
            DBMeetingMinutes.transcript_id == transcript_id
        )
        .first()
    )

    if minutes is None:
        return None

    from typing import cast, Literal
    from schemas import ActionItem

    # Ensure sentiment is one of the 3 valid Pydantic values
    raw_sentiment = str(minutes.sentiment or "Neutral")
    if raw_sentiment not in ("Positive", "Neutral", "Negative"):
        raw_sentiment = "Neutral"

    # Reconstruct ActionItem objects from the JSON dicts stored in DB
    action_items = [
        ActionItem(**item) if isinstance(item, dict) else item
        for item in (minutes.action_items or [])
    ]

    return SchemaMeetingMinutes(
        summary=str(minutes.summary),
        key_decisions=cast(list[str], minutes.key_decisions or []),
        action_items=action_items,
        sentiment=cast(Literal["Positive", "Neutral", "Negative"], raw_sentiment),
    )


def update_transcript(
    db,
    transcript_id,
    file_path,
    vectorstore_path,
    
):

    transcript = (
        db.query(Transcript)
        .filter(
            Transcript.transcript_id == transcript_id
        )
        .first()
    )

    if transcript is None:
        return None

    transcript.file_path = file_path
    transcript.vectorstore_path = vectorstore_path
    transcript.status = "completed"

    db.commit()
    db.refresh(transcript)

    return transcript




def update_transcript_status(
    db,
    transcript_id,
    status,
):

    transcript = (
        db.query(Transcript)
        .filter(
            Transcript.transcript_id == transcript_id
        )
        .first()
    )

    if transcript is None:
        return

    transcript.status = status

    db.commit()


# ---------- CHAT HISTORY ----------

from database.models import ChatHistory

def create_chat_message(
    db: Session,
    user_id: str | uuid.UUID,
    transcript_id: str | uuid.UUID | None,
    role: str,
    message: str,
):
    """Save a chat message in the database."""
    u_id = uuid.UUID(str(user_id))
    t_id = uuid.UUID(str(transcript_id)) if transcript_id else None

    db_msg = ChatHistory(
        user_id=u_id,
        transcript_id=t_id,
        role=role,
        message=message,
    )
    db.add(db_msg)
    db.commit()
    db.refresh(db_msg)
    return db_msg


def get_chat_history(
    db: Session,
    user_id: str | uuid.UUID,
    transcript_id: str | uuid.UUID | None = None,
    limit: int = 50,
):
    """Retrieve chat history for a user, optionally filtered by transcript."""
    u_id = uuid.UUID(str(user_id))
    t_id = uuid.UUID(str(transcript_id)) if transcript_id else None

    query = db.query(ChatHistory).filter(ChatHistory.user_id == u_id)
    if t_id:
        query = query.filter(ChatHistory.transcript_id == t_id)
    else:
        query = query.filter(ChatHistory.transcript_id.is_(None))

    return query.order_by(ChatHistory.created_at.asc()).limit(limit).all()
