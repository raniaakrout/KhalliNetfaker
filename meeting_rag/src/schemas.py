from typing import Literal
import uuid

from pydantic import BaseModel, Field


class ActionItem(BaseModel):
    """Represents an action item extracted from a meeting."""

    task: str = Field(
        description="Task that needs to be completed."
    )

    owner: str | None = Field(
        default=None,
        description="Person responsible for the task if explicitly mentioned."
    )

    deadline: str | None = Field(
        default=None,
        description="Deadline if explicitly mentioned in the transcript."
    )


class MeetingChunkSummary(BaseModel):
    """Structured summary generated for one semantic chunk."""

    summary: str = Field(
        description="A concise paragraph summarizing the chunk."
    )

    key_decisions: list[str] = Field(
        default_factory=list,
        description="List of decisions explicitly made in this chunk."
    )

    action_items: list[ActionItem] = Field(
        default_factory=list,
        description="List of action items extracted from this chunk."
    )

    sentiment: Literal["Positive", "Neutral", "Negative"] = Field(
        description="Overall sentiment expressed in this chunk."
    )


class MeetingMinutes(BaseModel):
    """Final structured meeting minutes."""

    summary: str = Field(
        description="Overall summary of the meeting."
    )

    key_decisions: list[str] = Field(
        default_factory=list,
        description="Unique decisions made during the meeting."
    )

    action_items: list[ActionItem] = Field(
        default_factory=list,
        description="Final list of meeting action items."
    )

    sentiment: Literal["Positive", "Neutral", "Negative"] = Field(
        description="Overall sentiment of the meeting."
    )


class MetricScore(BaseModel):
    name: str
    score: float
    reason: str
    threshold: float
    passed: bool


class EvalResult(BaseModel):
    transcript_id: str
    pipeline: str
    metrics: list[MetricScore]
    evaluated_at: str


class SummaryEvalRequest(BaseModel):
    transcript_id: str
    reference_summary: str | None = None


class RagEvalRequest(BaseModel):
    transcript_id: str
    question: str
    answer: str
    retrieved_chunks: list[str]
    expected_answer: str | None = None


class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., description="Unique email address")
    password: str = Field(..., min_length=6, description="Plain text password")


class UserLogin(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    username: str
    email: str


class UserResponse(BaseModel):
    user_id: uuid.UUID
    username: str
    email: str

    class Config:
        from_attributes = True