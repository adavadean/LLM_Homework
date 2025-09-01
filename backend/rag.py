from typing import List, Dict, Any
import chromadb
from chromadb.utils import embedding_functions
from settings import settings

client = chromadb.PersistentClient(path=settings.CHROMA_DIR)

openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key=settings.OPENAI_API_KEY,
    model_name=settings.EMBEDDING_MODEL,
)

collection = client.get_or_create_collection(
    name=settings.COLLECTION_NAME,
    embedding_function=openai_ef,
    metadata={
        "hnsw:space": "cosine"
    },
)

def upsert_items(items: List[Dict[str, Any]]) -> int:
    """Upsert a list of items into the collection.
    Each item requires: title, short_summary, tags (optional).
    Uses the title as ID (slugified)."""
    def slugify(s: str) -> str:
        import re
        s = s.lower()
        s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
        return s

    ids = [slugify(it["title"]) for it in items]
    documents = [it["short_summary"] for it in items]
    metadatas = [{
    "title": it["title"],
    "tags": ", ".join(it.get("tags", [])),  
} for it in items]

    collection.upsert(ids=ids, documents=documents, metadatas=metadatas)
    return len(items)

def query(text: str, k: int = 3) -> Dict[str, Any]:
    res = collection.query(
        query_texts=[text],
        n_results=k,
        include=["distances", "documents", "metadatas"],
    )
    return res

def is_collection_empty() -> bool:
    try:
        res = collection.peek()
        return len(res.get("ids", [])) == 0
    except Exception:
        return True
