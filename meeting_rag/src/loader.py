import sys
from langchain_community.document_loaders import TextLoader
from dotenv import load_dotenv

if sys.platform.startswith('win'):
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')  # type: ignore[attr-defined]
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')  # type: ignore[attr-defined]

load_dotenv()

def load_transcript(file_path: str):
    loader = TextLoader(file_path, encoding="utf-8")
    documents = loader.load()
    
    doc = documents[0]
    
    print(f"[OK] Document charge")
    print(f"Nombre de caracteres : {len(doc.page_content)}")
    print(f"Source : {doc.metadata['source']}")
    print(f"\nApercu (500 premiers caracteres) :\n")
    print(doc.page_content[:500])
    
    return documents[0]

if __name__ == "__main__":
    docs = load_transcript("data/2022_Q4_dbk_processed.txt")
