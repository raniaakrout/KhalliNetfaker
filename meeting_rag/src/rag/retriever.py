from langchain_core.documents import Document

from rag.vector_store import load_vector_store


def retrieve_documents(
    query: str,
    index_dir: str,
    k: int = 4,
) -> list[Document]:
    """Similarity search on the FAISS index for one transcript."""
    vector_store = load_vector_store(index_dir)
    return vector_store.similarity_search(query, k=k)
