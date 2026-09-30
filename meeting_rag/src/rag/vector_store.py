from pathlib import Path

from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS

from rag.embeddings import get_embeddings


def create_vector_store(documents: list[Document]) -> FAISS:
    """
    Create a FAISS vector store from a list of documents.
    """

    embeddings = get_embeddings()

    vector_store = FAISS.from_documents(
        documents=documents,
        embedding=embeddings,
    )

    return vector_store


def save_vector_store(vector_store: FAISS, index_dir: str | Path) -> None:
    """Save FAISS index under vectorstore/{transcript_id}/."""
    path = Path(index_dir)
    path.mkdir(parents=True, exist_ok=True)
    vector_store.save_local(str(path))
    print(f"[INFO] Vector store saved to {path}")


def load_vector_store(index_dir: str | Path) -> FAISS:
    """Load an existing FAISS index for one transcript."""
    path = Path(index_dir)
    embeddings = get_embeddings()
    vector_store = FAISS.load_local(
        str(path),
        embeddings,
        allow_dangerous_deserialization=True,
    )
    print(f"[INFO] Vector store loaded from {path}")
    return vector_store
