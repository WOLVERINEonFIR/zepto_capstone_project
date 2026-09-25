from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer


BASE_DIR = Path(__file__).resolve().parent
DOCS_DIR = BASE_DIR / "docs"
DB_DIR = BASE_DIR / "chroma_db"

COLLECTION_NAME = "zepto_policies"


def load_documents():
    documents = []
    ids = []
    metadatas = []

    for file_path in sorted(DOCS_DIR.glob("doc_*.txt")):
        text = file_path.read_text(encoding="utf-8").strip()

        if not text:
            continue

        documents.append(text)
        ids.append(file_path.stem)
        metadatas.append({
            "document_id": file_path.stem,
            "source": file_path.name,
        })

    return ids, documents, metadatas


def build_index():
    ids, documents, metadatas = load_documents()

    if len(documents) != 8:
        raise ValueError(
            f"Expected 8 documents, but found {len(documents)}."
        )

    print("Loading embedding model...")
    model = SentenceTransformer("all-MiniLM-L6-v2")

    print("Creating embeddings...")
    embeddings = model.encode(
        documents,
        normalize_embeddings=True
    )

    client = chromadb.PersistentClient(path=str(DB_DIR))

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    collection.upsert(
        ids=ids,
        documents=documents,
        embeddings=embeddings.tolist(),
        metadatas=metadatas,
    )

    print(f"Indexed documents: {collection.count()}")
    print(f"ChromaDB location: {DB_DIR}")


if __name__ == "__main__":
    build_index()