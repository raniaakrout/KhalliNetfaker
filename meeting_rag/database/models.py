from sqlalchemy import (
    Column,
    String,
    Text,
    DateTime,
    ForeignKey,
    JSON,
    func
)

from sqlalchemy.orm import relationship, Mapped

from database.db import Base

import uuid
from sqlalchemy.dialects.postgresql import UUID


class User(Base):

    __tablename__ = "users"

    user_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    username = Column(String, nullable=False)

    email = Column(
        String,
        unique=True,
        nullable=False
    )

    password_hash = Column(
        String,
        nullable=False
    )

    created_at = Column(
        DateTime,
        server_default=func.now()
    )


    transcripts = relationship(
        "Transcript",
        back_populates="user"
    )



class Transcript(Base):

    __tablename__ = "transcripts"


    transcript_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )


    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.user_id"),
        nullable=False
    )


    filename = Column(String)

    file_hash = Column(
        String,
        nullable=False
    )


    file_path = Column(Text)

    vectorstore_path = Column(Text)


    status = Column(
        String,
        default="processing"
    )


    created_at = Column(
        DateTime,
        server_default=func.now()
    )


    user = relationship(
        "User",
        back_populates="transcripts"
    )


    meeting_minutes = relationship(
        "MeetingMinutes",
        back_populates="transcript",
        uselist=False
    )


    chat_history = relationship(
        "ChatHistory",
        back_populates="transcript"
    )




class MeetingMinutes(Base):

    __tablename__ = "meeting_minutes"


    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )


    transcript_id = Column(
        UUID(as_uuid=True),
        ForeignKey("transcripts.transcript_id")
    )


    summary = Column(Text)

    key_decisions = Column(JSON)

    action_items = Column(JSON)

    sentiment = Column(String)


    created_at = Column(
        DateTime,
        server_default=func.now()
    )


    transcript = relationship(
        "Transcript",
        back_populates="meeting_minutes"
    )



class ChatHistory(Base):

    __tablename__ = "chat_history"


    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )


    transcript_id = Column(
        UUID(as_uuid=True),
        ForeignKey("transcripts.transcript_id"),
        nullable=True
    )


    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.user_id"),
        nullable=False
    )


    role = Column(String)

    message = Column(Text)


    created_at = Column(
        DateTime,
        server_default=func.now()
    )


    transcript = relationship(
        "Transcript",
        back_populates="chat_history"
    )



