from typing import Literal, cast
import os

from dotenv import load_dotenv

from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_experimental.text_splitter import SemanticChunker

load_dotenv()

BreakpointType = Literal[
    "gradient",
    "interquartile",
    "percentile",
    "standard_deviation",
]

# ── Lazy singleton ─────────────────────────────────────────────────────────────
# The HuggingFace model (~120 MB) is loaded only on the first call to
# get_semantic_chunker(), not at module import time.
# This keeps server startup fast and avoids blocking on a cold start.
_semantic_chunker: SemanticChunker | None = None


def get_semantic_chunker() -> SemanticChunker:
    """Return the shared SemanticChunker, creating it on first call."""
    global _semantic_chunker
    if _semantic_chunker is None:
        print("[INFO] Loading HuggingFace embedding model (first upload)…")
        embeddings = HuggingFaceEmbeddings(
            model_name=os.getenv("EMBEDDING_MODEL"),
            encode_kwargs={"normalize_embeddings": True},
        )
        threshold_type = cast(
            BreakpointType,
            os.getenv("BREAKPOINT_THRESHOLD_TYPE", "percentile"),
        )
        _semantic_chunker = SemanticChunker(
            embeddings=embeddings,
            breakpoint_threshold_type=threshold_type,
            breakpoint_threshold_amount=float(
                os.getenv("BREAKPOINT_THRESHOLD_AMOUNT", 95)
            ),
        )
        print("[INFO] HuggingFace embedding model loaded.")
    return _semantic_chunker


def split_transcript(document: Document) -> list[Document]:
    """
    Split a meeting transcript into semantic chunks.
    """
    chunker = get_semantic_chunker()
    return chunker.create_documents(
        [document.page_content],
        metadatas=[document.metadata],
    )