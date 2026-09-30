"""
Unified and decoupled chunking module.

Separates chunking strategies for:
1. Summarization (Map-Reduce oriented: token, recursive, semantic)
2. RAG Indexation (Vector retrieval oriented: semantic, token, recursive)
"""

import os
from typing import Literal, Optional
from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_text_splitters import TokenTextSplitter, RecursiveCharacterTextSplitter
from semantic_chunker import get_semantic_chunker

load_dotenv()

ChunkStrategy = Literal["token", "recursive", "semantic"]


def split_document(
    document: Document,
    strategy: str = "token",
    chunk_size: int = 1024,
    chunk_overlap: int = 100,
) -> list[Document]:
    """
    Split a document using the specified strategy:
    - 'token': TokenTextSplitter (predictable token count, ideal for LLM summarization map-step)
    - 'recursive': RecursiveCharacterTextSplitter (paragraph / sentence / word split with overlap)
    - 'semantic': SemanticChunker (breakpoint detection based on embedding similarity)
    """
    strat = strategy.lower().strip()
    metadata = document.metadata or {}

    if strat == "token":
        splitter = TokenTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )
        return splitter.create_documents([document.page_content], metadatas=[metadata])

    elif strat == "recursive":
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )
        return splitter.create_documents([document.page_content], metadatas=[metadata])

    elif strat == "semantic":
        chunker = get_semantic_chunker()
        return chunker.create_documents([document.page_content], metadatas=[metadata])

    else:
        raise ValueError(
            f"Unknown chunking strategy '{strategy}'. Supported strategies: 'token', 'recursive', 'semantic'."
        )


def split_for_summary(
    document: Document,
    strategy: Optional[str] = None,
    chunk_size: Optional[int] = None,
    chunk_overlap: Optional[int] = None,
) -> list[Document]:
    """
    Chunking tailored for the summarizer pipeline.
    Defaults to token chunking configured in .env (or 1024 tokens / 100 overlap).
    """
    chosen_strategy = strategy or os.getenv("SUMMARY_CHUNKING_STRATEGY", "token")
    chosen_size = chunk_size or int(os.getenv("SUMMARY_CHUNK_SIZE", "1024"))
    chosen_overlap = chunk_overlap or int(os.getenv("SUMMARY_CHUNK_OVERLAP", "100"))

    return split_document(
        document=document,
        strategy=chosen_strategy,
        chunk_size=chosen_size,
        chunk_overlap=chosen_overlap,
    )


def split_for_rag(
    document: Document,
    strategy: Optional[str] = None,
    chunk_size: Optional[int] = None,
    chunk_overlap: Optional[int] = None,
) -> list[Document]:
    """
    Chunking tailored for RAG vector search indexation.
    Defaults to semantic chunking configured in .env (or 512 tokens / 50 overlap for fixed splitters).
    """
    chosen_strategy = strategy or os.getenv("RAG_CHUNKING_STRATEGY", "semantic")
    chosen_size = chunk_size or int(os.getenv("RAG_CHUNK_SIZE", "512"))
    chosen_overlap = chunk_overlap or int(os.getenv("RAG_CHUNK_OVERLAP", "50"))

    return split_document(
        document=document,
        strategy=chosen_strategy,
        chunk_size=chosen_size,
        chunk_overlap=chosen_overlap,
    )
