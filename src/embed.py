"""
Embedding and vector storage for RAG chatbot.

Embeds document chunks using sentence-transformers (all-MiniLM-L6-v2),
stores them in a persistent ChromaDB collection, and provides semantic search.
"""

import hashlib
import sys
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer

from ingest import get_chunks

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

MODEL_NAME = "all-MiniLM-L6-v2"
COLLECTION_NAME = "rag_documents"
CHROMA_PATH = str(Path(__file__).resolve().parent.parent / "chroma_db")

# ---------------------------------------------------------------------------
# Embedding model (lazy-loaded singleton)
# ---------------------------------------------------------------------------

_model = None

def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)
    return _model


# ---------------------------------------------------------------------------
# ChromaDB client + collection
# ---------------------------------------------------------------------------

def _get_collection() -> chromadb.Collection:
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )


def _chunk_id(chunk: dict) -> str:
    """Deterministic ID from chunk text + metadata so we can skip duplicates."""
    raw = chunk["text"] + str(sorted(chunk["metadata"].items()))
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def add_chunks(chunks: list[dict]) -> int:
    """
    Embed and store chunks in ChromaDB. Skips chunks already in the collection.
    Returns the number of newly added chunks.
    """
    collection = _get_collection()
    model = _get_model()

    # Build IDs and check which are already stored
    ids = [_chunk_id(c) for c in chunks]
    existing = set()
    # Query in batches (ChromaDB get has no batch limit but let's be safe)
    batch_size = 500
    for i in range(0, len(ids), batch_size):
        batch_ids = ids[i : i + batch_size]
        result = collection.get(ids=batch_ids)
        existing.update(result["ids"])

    # Filter to only new chunks
    new_chunks = []
    new_ids = []
    for chunk, cid in zip(chunks, ids):
        if cid not in existing:
            new_chunks.append(chunk)
            new_ids.append(cid)

    if not new_chunks:
        return 0

    # Embed
    texts = [c["text"] for c in new_chunks]
    embeddings = model.encode(texts, show_progress_bar=len(texts) > 50)

    # Convert metadata values to str (ChromaDB requires str/int/float)
    metadatas = []
    for c in new_chunks:
        meta = {}
        for k, v in c["metadata"].items():
            meta[k] = v if isinstance(v, (int, float)) else str(v)
        metadatas.append(meta)

    # Upsert in batches
    for i in range(0, len(new_ids), batch_size):
        end = i + batch_size
        collection.add(
            ids=new_ids[i:end],
            embeddings=embeddings[i:end].tolist(),
            documents=texts[i:end],
            metadatas=metadatas[i:end],
        )

    return len(new_chunks)


def search(query: str, n_results: int = 5) -> list[dict]:
    """
    Semantic search: embed the query and return the top N most relevant chunks.

    Returns list of dicts with keys: text, metadata, distance.
    """
    collection = _get_collection()
    model = _get_model()

    if collection.count() == 0:
        return []

    query_embedding = model.encode([query])[0].tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(n_results, collection.count()),
    )

    output = []
    for i in range(len(results["ids"][0])):
        output.append({
            "text": results["documents"][0][i],
            "metadata": results["metadatas"][0][i],
            "distance": results["distances"][0][i],
        })

    return output


def collection_stats() -> dict:
    """Return basic stats about the stored collection."""
    collection = _get_collection()
    count = collection.count()
    return {"collection": COLLECTION_NAME, "total_chunks": count}


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    default_docs = str(Path(__file__).resolve().parent.parent / "docs")
    folder = sys.argv[1] if len(sys.argv) > 1 else default_docs

    # Step 1: Ingest
    print(f"Ingesting documents from: {folder}")
    chunks = get_chunks(folder)
    print(f"  {len(chunks)} chunks from ingest.py")

    # Step 2: Embed and store
    print(f"\nEmbedding with {MODEL_NAME}...")
    added = add_chunks(chunks)
    stats = collection_stats()
    print(f"  Added {added} new chunks ({stats['total_chunks']} total in collection)")

    # Step 3: Test queries
    test_queries = [
        "How do I create a new branch in git?",
        "What does the First Amendment say?",
        "How does RAG retrieval work?",
        "What is the purpose of the Plain Writing Act?",
    ]

    print("\n" + "=" * 60)
    print("SEARCH TESTS")
    print("=" * 60)

    for query in test_queries:
        print(f"\nQuery: \"{query}\"")
        print("-" * 50)
        results = search(query, n_results=3)
        for i, r in enumerate(results, 1):
            source = r["metadata"].get("source", "?")
            page = r["metadata"].get("page", "")
            section = r["metadata"].get("section", "")
            location = f"p.{page}" if page else section
            score = 1 - r["distance"]  # cosine similarity
            preview = r["text"][:150].replace("\n", " ")
            print(f"  {i}. [{source} | {location}] (sim={score:.3f})")
            print(f"     {preview}...")
        print()


if __name__ == "__main__":
    main()
