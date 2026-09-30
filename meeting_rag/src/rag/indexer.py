import os
from pathlib import Path
from typing import Callable

from langchain_core.documents import Document

from loader import load_transcript
from chunker import split_for_rag

from rag.vector_store import (
    create_vector_store,
    save_vector_store,
)

_noop: Callable[[str], None] = lambda _msg: None


class Indexer:
    """
    Each transcript gets its own folder: vectorstore/{transcript_id}/
    Accepts an optional `emit` callback to report progress to the caller.
    """

    def __init__(
        self,
        index_dir: str,
        chunking_strategy: str | None = None,
        chunk_size: int | None = None,
        chunk_overlap: int | None = None,
    ):
        self.index_dir = index_dir
        self.chunking_strategy = chunking_strategy or os.getenv("RAG_CHUNKING_STRATEGY", "semantic")
        self.chunk_size = chunk_size or int(os.getenv("RAG_CHUNK_SIZE", "512"))
        self.chunk_overlap = chunk_overlap or int(os.getenv("RAG_CHUNK_OVERLAP", "50"))

    def build(self, file_path: str, emit: Callable[[str], None] = _noop):

        emit("Loading transcript file…")
        print("[INFO] Loading transcript...")
        document = load_transcript(file_path)

        emit(f"Running RAG chunking ({self.chunking_strategy})…")
        print(f"[INFO] RAG chunking ({self.chunking_strategy})...")
        chunks = split_for_rag(
            document,
            strategy=self.chunking_strategy,
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
        )

        nb_chunks = len(chunks)
        emit(f"Chunking method: RAG ({self.chunking_strategy}) — {nb_chunks} chunk(s) produced")
        print(f"[INFO] {nb_chunks} chunks created")

        # Save RAG chunks to disk
        import json
        transcript_id = Path(self.index_dir).name
        rag_chunks_dir = Path("data/chunks/rag")
        rag_chunks_dir.mkdir(parents=True, exist_ok=True)
        rag_file = rag_chunks_dir / f"{transcript_id}.json"

        chunks_payload = [
            {
                "chunk_id": i,
                "source": Path(file_path).name,
                "page_content": chunk.page_content,
            }
            for i, chunk in enumerate(chunks)
        ]

        with open(rag_file, "w", encoding="utf-8") as f:
            json.dump(chunks_payload, f, ensure_ascii=False, indent=2)

        emit(f"RAG chunks saved to {rag_file}")
        print(f"[INFO] RAG chunks saved to {rag_file}")

        indexed_chunks = []
        for i, chunk in enumerate(chunks):
            indexed_chunks.append(
                Document(
                    page_content=chunk.page_content,
                    metadata={
                        "chunk_id": i,
                        "source": Path(file_path).name,
                    },
                )
            )

        emit("Building FAISS vector store…")
        print("[INFO] Building vector store...")
        vector_store = create_vector_store(indexed_chunks)

        emit("Saving FAISS index to disk…")
        print("[INFO] Saving vector store...")
        save_vector_store(vector_store, self.index_dir)

        emit("✅ Vector index created.")
        print("[SUCCESS] Index created.")