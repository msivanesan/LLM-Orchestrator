"""
VectorStore — per-user ChromaDB context manager.

Uses ChromaDB running in Docker via HTTP client.
Each user gets an isolated collection for semantic context retrieval.
Embeddings: all-MiniLM-L6-v2 (CPU-friendly, 384-dim).
"""
import os
import hashlib
import logging
from typing import List, Dict, Optional

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

# ── Config from env ───────────────────────────────────────────────────────────
CHROMA_HOST       = os.getenv('CHROMA_HOST', 'localhost')
CHROMA_PORT       = int(os.getenv('CHROMA_PORT', '8000'))
CHROMA_AUTH_TOKEN = os.getenv('CHROMA_AUTH_TOKEN', 'changeme-chroma-token')
EMBED_MODEL_NAME  = os.getenv('EMBED_MODEL', 'all-MiniLM-L6-v2')

# ── Singletons ────────────────────────────────────────────────────────────────
_embed_model: Optional[SentenceTransformer] = None
_chroma_client: Optional[chromadb.HttpClient] = None


def _get_embed_model() -> SentenceTransformer:
    global _embed_model
    if _embed_model is None:
        logger.info("Loading embedding model: %s", EMBED_MODEL_NAME)
        _embed_model = SentenceTransformer(EMBED_MODEL_NAME)
    return _embed_model


def _get_chroma_client() -> chromadb.HttpClient:
    """Return a ChromaDB HTTP client connected to the Docker container."""
    global _chroma_client
    if _chroma_client is None:
        logger.info("Connecting to ChromaDB at %s:%s", CHROMA_HOST, CHROMA_PORT)
        _chroma_client = chromadb.HttpClient(
            host=CHROMA_HOST,
            port=CHROMA_PORT,
            settings=Settings(
                chroma_client_auth_provider="chromadb.auth.token.TokenAuthClientProvider",
                chroma_client_auth_credentials=CHROMA_AUTH_TOKEN,
                anonymized_telemetry=False,
            ),
        )
    return _chroma_client


# ── Helpers ───────────────────────────────────────────────────────────────────

def _collection_name(user_id: int) -> str:
    """Deterministic, ChromaDB-safe collection name per user."""
    h = hashlib.md5(f"user_{user_id}".encode()).hexdigest()[:8]
    return f"u{user_id}_{h}"


def _get_collection(user_id: int):
    client = _get_chroma_client()
    return client.get_or_create_collection(
        name=_collection_name(user_id),
        metadata={"hnsw:space": "ip"},  # Inner Product (Dot Product)
    )


# ── Public API ────────────────────────────────────────────────────────────────

def upsert_message(
    user_id: int,
    message_id: int,
    text: str,
    session_id: int,
    role: str,
) -> None:
    """Embed one message and upsert it into the user's ChromaDB collection."""
    try:
        model     = _get_embed_model()
        embedding = model.encode(text).tolist()
        col       = _get_collection(user_id)
        col.upsert(
            ids=[str(message_id)],
            embeddings=[embedding],
            documents=[text],
            metadatas=[{
                "session_id": session_id,
                "role":       role,
                "message_id": message_id,
                "user_id":    user_id,
            }],
        )
        logger.debug("Upserted message %s for user %s", message_id, user_id)
    except Exception:
        logger.exception("VectorStore.upsert_message failed (msg=%s user=%s)",
                         message_id, user_id)


def query_context(
    user_id: int,
    query_text: str,
    n_results: int = 8,
    session_id: Optional[int] = None,
) -> List[Dict]:
    """
    Semantic search across a user's conversation history.
    Optionally scoped to a specific session.

    Returns list of dicts: {content, role, session_id, message_id, score}
    """
    try:
        model     = _get_embed_model()
        embedding = model.encode(query_text).tolist()
        col       = _get_collection(user_id)

        count = col.count()
        if count == 0:
            return []

        where = {"session_id": session_id} if session_id else None
        results = col.query(
            query_embeddings=[embedding],
            n_results=min(n_results, count),
            include=["documents", "metadatas", "distances"],
            where=where,
        )

        items = []
        if results and results.get("documents"):
            for doc, meta, dist in zip(
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0],
            ):
                items.append({
                    "content":    doc,
                    "role":       meta.get("role"),
                    "session_id": meta.get("session_id"),
                    "message_id": meta.get("message_id"),
                    "score":      round(1 - dist, 4),  # cosine similarity
                })
        return items
    except Exception:
        logger.exception("VectorStore.query_context failed (user=%s)", user_id)
        return []


def delete_session_vectors(user_id: int, session_id: int) -> None:
    """Remove all vectors for a deleted session from ChromaDB."""
    try:
        col     = _get_collection(user_id)
        results = col.get(where={"session_id": session_id})
        if results and results.get("ids"):
            col.delete(ids=results["ids"])
            logger.info("Deleted %d vectors for session %s", len(results["ids"]), session_id)
    except Exception:
        logger.exception("VectorStore.delete_session_vectors failed (session=%s)", session_id)


def chroma_health() -> bool:
    """Return True if ChromaDB Docker container is reachable."""
    try:
        client = _get_chroma_client()
        client.heartbeat()
        return True
    except Exception:
        return False
