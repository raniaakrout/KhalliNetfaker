import os

from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings

load_dotenv()


def get_embeddings() -> HuggingFaceEmbeddings:


    return HuggingFaceEmbeddings(
        model_name=os.getenv("EMBEDDING_MODEL"),
        model_kwargs={
            "device": "cpu",
        },
        encode_kwargs={
            "normalize_embeddings": True,
        },
    )


if __name__ == "__main__":

    embeddings = get_embeddings()

    vector = embeddings.embed_query(
        "What was the revenue in Q4?"
    )

    print(len(vector))