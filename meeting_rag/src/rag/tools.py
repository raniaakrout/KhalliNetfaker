from pathlib import Path
import json

from langchain.tools import tool

from rag.retriever import retrieve_documents


def make_chat_tools(transcript_id: str | None) -> list:
    """
    Return the tools available for the current conversation.

    - If no transcript is selected -> no tools.
    - Otherwise -> search + summary tools.
    """

    if transcript_id is None:
        return []

    upload_dir = Path("data/uploads")
    vectorstore_dir = Path("vectorstore")

    index_dir = str(vectorstore_dir / transcript_id)
    file_path = str(upload_dir / f"{transcript_id}.txt")
    minutes_path = upload_dir / f"{transcript_id}_minutes.json"

    @tool
    def search_meeting(query: str) -> str:
        """
        Search the meeting transcript for factual questions.
        """

        docs = retrieve_documents(query, index_dir=index_dir)

        if not docs:
            return "No relevant information found in the transcript."

        return "\n\n---\n\n".join(
            f"[Chunk {doc.metadata.get('chunk_id', 'N/A')}]\n{doc.page_content}"
            for doc in docs
        )

    @tool
    def get_meeting_summary() -> str:
        """
        Return the meeting summary.
        """

        if minutes_path.exists():
            return minutes_path.read_text(encoding="utf-8")

        from summarizer import Summarizer

        minutes = Summarizer().run(file_path, transcript_id)

        payload = minutes.model_dump()

        minutes_path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        return json.dumps(payload, indent=2, ensure_ascii=False)

    return [search_meeting, get_meeting_summary]